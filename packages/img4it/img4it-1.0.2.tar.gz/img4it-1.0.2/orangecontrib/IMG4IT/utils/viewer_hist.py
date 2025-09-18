# -*- coding: utf-8 -*-
"""
Viewer TIFF 16 bits avec réglage d'étalement, zoom/pan
+ navigation dossier (←/→ et boutons)
+ modes: linéaire, gamma 0.5, gamma 2.0, sigmoïde,
         log, inverse-log, exponentielle, racine √, racine ³,
         HE (global), CLAHE (local via scikit-image si dispo)
Toutes les courbes respectent les bornes min/max (percentiles).
Rafraîchissement immédiat sur toute interaction.
Affiche la colonne/ligne sous la souris.
Dépendances: AnyQt (PyQt6), numpy, tifffile
Optionnel: scikit-image (pour CLAHE)
"""

import sys
import os
import numpy as np
import tifffile as tiff
from AnyQt import QtWidgets, QtGui, QtCore

# --- CLAHE optionnel via scikit-image ---
try:
    from skimage import exposure as sk_exposure
    HAS_SKIMAGE = True
except Exception:
    HAS_SKIMAGE = False


def qimage_from_gray_uint8(arr_u8: np.ndarray) -> QtGui.QImage:
    """Convertit un ndarray uint8 (H, W) en QImage Grayscale8 sans copie."""
    if arr_u8.dtype != np.uint8 or arr_u8.ndim != 2:
        raise ValueError("qimage_from_gray_uint8 attend un array (H, W) en uint8.")
    if not arr_u8.flags["C_CONTIGUOUS"]:
        arr_u8 = np.ascontiguousarray(arr_u8)
    h, w = arr_u8.shape
    bytes_per_line = arr_u8.strides[0]
    qimg = QtGui.QImage(arr_u8.data, w, h, bytes_per_line,
                        QtGui.QImage.Format.Format_Grayscale8)
    qimg._arr_ref = arr_u8  # garder réf vivante
    return qimg


def hist_uint16(arr_u16: np.ndarray) -> np.ndarray:
    return np.bincount(arr_u16.ravel(), minlength=65536)


def percentile_from_hist(hist: np.ndarray, total_px: int, p: float) -> int:
    """Retourne une valeur 16 bits au percentile p en s'appuyant sur l'histogramme 65536 bins."""
    if p <= 0:
        return 0
    if p >= 100:
        return 65535
    target = total_px * (p / 100.0)
    cdf = np.cumsum(hist, dtype=np.int64)
    idx = int(np.searchsorted(cdf, target, side="left"))
    return int(np.clip(idx, 0, 65535))


# === HE & CLAHE sur t in [0,1] ===
def he_on_unit_float(t: np.ndarray, nbins: int = 256) -> np.ndarray:
    t = np.clip(t.astype(np.float32), 0.0, 1.0)
    h, bins = np.histogram(t, bins=int(max(2, nbins)), range=(0.0, 1.0))
    cdf = np.cumsum(h).astype(np.float32)
    if cdf[-1] <= 0:
        return t
    cdf /= cdf[-1]
    bin_centers = (bins[:-1] + bins[1:]) * 0.5
    y = np.interp(t.ravel(), bin_centers, cdf).reshape(t.shape).astype(np.float32)
    return y


def clahe_on_unit_float(t: np.ndarray, clip_limit: float = 0.01, nbins: int = 256) -> np.ndarray:
    t = np.clip(t.astype(np.float32), 0.0, 1.0)
    if HAS_SKIMAGE:
        y = sk_exposure.equalize_adapthist(t, clip_limit=float(max(1e-6, clip_limit)), nbins=int(max(2, nbins)))
        return y.astype(np.float32, copy=False)
    # fallback: HE global
    return he_on_unit_float(t, nbins=nbins)


class ImageView(QtWidgets.QGraphicsView):
    """Widget avec zoom + pan à la souris + émission des coords souris."""
    mouseMoved = QtCore.Signal(int, int)  # (col, row)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHints(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self._img_w = 0
        self._img_h = 0

    def set_image_size(self, w: int, h: int):
        self._img_w = int(max(0, w))
        self._img_h = int(max(0, h))

    def wheelEvent(self, event: QtGui.QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        f = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        self.scale(f, f)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        # Coordonnées scène sous la souris
        sp = self.mapToScene(event.position().toPoint())
        x = int(np.floor(sp.x()))
        y = int(np.floor(sp.y()))
        # Borne dans l'image
        if 0 <= x < self._img_w and 0 <= y < self._img_h:
            self.mouseMoved.emit(x, y)
        else:
            # Hors image -> on émet -1 pour signaler "n/a"
            self.mouseMoved.emit(-1, -1)
        super().mouseMoveEvent(event)


class Tiff16Viewer(QtWidgets.QWidget):
    def __init__(self, input_path, parent=None):
        super().__init__(parent)

        # --- Résolution du dossier et de la liste d'images ---
        self.files = []
        self.idx = 0
        self._resolve_inputs(input_path)

        # --- État traitement ---
        self.arr16 = None
        self.h = self.w = 0
        self.hist = None
        self.total_px = 0
        self.min_val = 0
        self.max_val = 0

        # --- Vue graphique (zoom/pan) ---
        self.scene = QtWidgets.QGraphicsScene()
        self.view = ImageView()
        self.view.setScene(self.scene)
        self.pixmap_item = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        # --- Bandeau nom de fichier + navigation ---
        self.name_label = QtWidgets.QLabel("--")
        self.name_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)

        self.btn_prev = QtWidgets.QPushButton("← Précédent")
        self.btn_next = QtWidgets.QPushButton("Suivant →")

        nav = QtWidgets.QHBoxLayout()
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)
        nav.addStretch(1)
        nav.addWidget(self.name_label)

        # --- Coordonnées souris (colonnes / lignes) ---
        self.col_edit = QtWidgets.QLineEdit()
        self.col_edit.setReadOnly(True)
        self.col_edit.setFixedWidth(90)
        self.col_edit.setPlaceholderText("Colonne")
        self.row_edit = QtWidgets.QLineEdit()
        self.row_edit.setReadOnly(True)
        self.row_edit.setFixedWidth(90)
        self.row_edit.setPlaceholderText("Ligne")

        coords = QtWidgets.QHBoxLayout()
        coords.addWidget(QtWidgets.QLabel("Col:"))
        coords.addWidget(self.col_edit)
        coords.addSpacing(8)
        coords.addWidget(QtWidgets.QLabel("Ligne:"))
        coords.addWidget(self.row_edit)
        coords.addStretch(1)

        # --- Contrôles percentiles ---
        self.low_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.high_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        for s in (self.low_slider, self.high_slider):
            s.setRange(0, 100)
            s.setTickInterval(5)
            s.setSingleStep(1)
            s.setTracking(True)  # rafraîchit pendant le drag
        self.low_slider.setValue(2)
        self.high_slider.setValue(98)

        self.low_spin = QtWidgets.QSpinBox(); self.low_spin.setRange(0, 100); self.low_spin.setSuffix(" %")
        self.high_spin = QtWidgets.QSpinBox(); self.high_spin.setRange(0, 100); self.high_spin.setSuffix(" %")
        self.low_spin.setValue(self.low_slider.value())
        self.high_spin.setValue(self.high_slider.value())

        # --- Boutons d'étendue ---
        self.btn_auto = QtWidgets.QPushButton("Auto (2–98%)")
        self.btn_full = QtWidgets.QPushButton("Plein écart (min–max)")
        self.btn_reset = QtWidgets.QPushButton("Réinitialiser vue")

        # --- Boutons d'augmentation de contraste ---
        # existants
        self.btn_lin = QtWidgets.QPushButton("Linéaire")
        self.btn_gam05 = QtWidgets.QPushButton("Gamma 0.5")
        self.btn_gam20 = QtWidgets.QPushButton("Gamma 2.0")
        self.btn_sig = QtWidgets.QPushButton("Sigmoïde")
        # nouveaux
        self.btn_log = QtWidgets.QPushButton("Log")
        self.btn_invlog = QtWidgets.QPushButton("Inverse-Log")
        self.btn_exp = QtWidgets.QPushButton("Exponentielle")
        self.btn_sqrt = QtWidgets.QPushButton("Racine √")
        self.btn_cbrt = QtWidgets.QPushButton("Racine ³")
        self.btn_he = QtWidgets.QPushButton("HE (global)")
        self.btn_clahe = QtWidgets.QPushButton("CLAHE")

        # Réglages HE / CLAHE
        self.he_bins_spin = QtWidgets.QSpinBox()
        self.he_bins_spin.setRange(16, 4096)
        self.he_bins_spin.setSingleStep(16)
        self.he_bins_spin.setValue(256)
        self.he_bins_spin.setToolTip("Nombre de bins pour HE (global)")
        self.clahe_clip_spin = QtWidgets.QDoubleSpinBox()
        self.clahe_clip_spin.setRange(0.001, 0.100)
        self.clahe_clip_spin.setSingleStep(0.001)
        self.clahe_clip_spin.setDecimals(3)
        self.clahe_clip_spin.setValue(0.010)
        self.clahe_clip_spin.setToolTip("Clip limit pour CLAHE")

        # État courant de la courbe
        # modes: linear, gamma05, gamma20, sigmoid, log, invlog, exp, sqrt, cbrt, he, clahe
        self.contrast_mode = "linear"

        # --- Layouts ---
        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel("Percentile bas"), 0, 0)
        grid.addWidget(self.low_slider, 0, 1)
        grid.addWidget(self.low_spin, 0, 2)
        grid.addWidget(QtWidgets.QLabel("Percentile haut"), 1, 0)
        grid.addWidget(self.high_slider, 1, 1)
        grid.addWidget(self.high_spin, 1, 2)

        btns = QtWidgets.QHBoxLayout()
        btns.addWidget(self.btn_auto)
        btns.addWidget(self.btn_full)
        btns.addWidget(self.btn_reset)
        btns.addStretch(1)

        contrast_btns1 = QtWidgets.QHBoxLayout()
        contrast_btns1.addWidget(QtWidgets.QLabel("Courbe contraste :"))
        for b in (self.btn_lin, self.btn_gam05, self.btn_gam20, self.btn_sig):
            contrast_btns1.addWidget(b)
        contrast_btns1.addStretch(1)

        contrast_btns2 = QtWidgets.QHBoxLayout()
        for b in (self.btn_log, self.btn_invlog, self.btn_exp, self.btn_sqrt, self.btn_cbrt, self.btn_he, self.btn_clahe):
            contrast_btns2.addWidget(b)
        contrast_btns2.addStretch(1)

        params_row = QtWidgets.QHBoxLayout()
        params_row.addWidget(QtWidgets.QLabel("HE nbins:"))
        params_row.addWidget(self.he_bins_spin)
        params_row.addSpacing(12)
        params_row.addWidget(QtWidgets.QLabel("CLAHE clip_limit:"))
        params_row.addWidget(self.clahe_clip_spin)
        params_row.addStretch(1)

        v = QtWidgets.QVBoxLayout(self)
        v.addLayout(nav)
        v.addWidget(self.view, stretch=1)
        v.addLayout(coords)           # <<--- coordonnées souris
        v.addLayout(grid)
        v.addLayout(btns)
        v.addLayout(contrast_btns1)
        v.addLayout(contrast_btns2)
        v.addLayout(params_row)

        # --- Connexions (rafraîchissement immédiat) ---
        self.low_slider.valueChanged.connect(self._on_low_slider)
        self.high_slider.valueChanged.connect(self._on_high_slider)
        self.low_spin.valueChanged.connect(self._on_low_spin)
        self.high_spin.valueChanged.connect(self._on_high_spin)

        self.btn_auto.clicked.connect(self.apply_auto)
        self.btn_full.clicked.connect(self.apply_full)
        self.btn_reset.clicked.connect(self.reset_view)

        # modes existants
        self.btn_lin.clicked.connect(lambda: self.set_contrast_mode("linear"))
        self.btn_gam05.clicked.connect(lambda: self.set_contrast_mode("gamma05"))
        self.btn_gam20.clicked.connect(lambda: self.set_contrast_mode("gamma20"))
        self.btn_sig.clicked.connect(lambda: self.set_contrast_mode("sigmoid"))

        # nouveaux modes
        self.btn_log.clicked.connect(lambda: self.set_contrast_mode("log"))
        self.btn_invlog.clicked.connect(lambda: self.set_contrast_mode("invlog"))
        self.btn_exp.clicked.connect(lambda: self.set_contrast_mode("exp"))
        self.btn_sqrt.clicked.connect(lambda: self.set_contrast_mode("sqrt"))
        self.btn_cbrt.clicked.connect(lambda: self.set_contrast_mode("cbrt"))
        self.btn_he.clicked.connect(lambda: self.set_contrast_mode("he"))
        self.btn_clahe.clicked.connect(lambda: self.set_contrast_mode("clahe"))

        # réglages HE/CLAHE
        self.he_bins_spin.valueChanged.connect(self.update_view)
        self.clahe_clip_spin.valueChanged.connect(self.update_view)

        # navigation
        self.btn_prev.clicked.connect(self.go_prev)
        self.btn_next.clicked.connect(self.go_next)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Left),  self, activated=self.go_prev)
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Right), self, activated=self.go_next)

        # coords souris
        self.view.mouseMoved.connect(self._on_mouse_moved)

        # Charge la première image
        self._load_current_image()

    # ---------- Gestion des entrées ----------
    def _resolve_inputs(self, input_path):
        path = os.path.abspath(input_path)
        if os.path.isdir(path):
            folder = path
            start_file = None
        else:
            folder = os.path.dirname(path) if os.path.dirname(path) else "."
            start_file = os.path.basename(path)

        exts = {".tif", ".tiff"}
        files = [f for f in os.listdir(folder)
                 if os.path.splitext(f)[1].lower() in exts]
        files.sort(key=lambda x: x.lower())

        if not files:
            QtWidgets.QMessageBox.critical(None, "Erreur", f"Aucune image .tif/.tiff dans :\n{folder}")
            sys.exit(1)

        self.files = [os.path.join(folder, f) for f in files]

        if start_file:
            try:
                self.idx = files.index(start_file)
            except ValueError:
                self.idx = 0
        else:
            self.idx = 0

    # ---------- Chargement d'image ----------
    def _load_current_image(self):
        path = self.files[self.idx]
        self._load_image_from_path(path)
        self.view.resetTransform()  # zoom 1:1
        self.update_view()
        self._update_name_label()

    def _load_image_from_path(self, path):
        arr = tiff.imread(path)
        if arr.ndim == 3:
            arr = arr[..., 0]
        if arr.dtype != np.uint16:
            arr = arr.astype(np.uint16, copy=False)
        self.arr16 = np.ascontiguousarray(arr)
        self.h, self.w = self.arr16.shape

        # Histogramme/stat
        self.hist = hist_uint16(self.arr16)
        self.total_px = int(self.arr16.size)
        self.min_val = int(self.arr16.min())
        self.max_val = int(self.arr16.max())

        # Ajuster la scène à la nouvelle taille
        self.scene.setSceneRect(0, 0, self.w, self.h)
        self.view.set_image_size(self.w, self.h)  # <<--- pour le suivi souris

    def _update_name_label(self):
        base = os.path.basename(self.files[self.idx])
        self.name_label.setText(f"{self.idx+1}/{len(self.files)}  —  {base}")

    # ---------- Navigation ----------
    def go_prev(self):
        if self.idx > 0:
            self.idx -= 1
            self._load_current_image()

    def go_next(self):
        if self.idx + 1 < len(self.files):
            self.idx += 1
            self._load_current_image()

    # ---------- Contraste ----------
    def set_contrast_mode(self, mode: str):
        self.contrast_mode = mode
        self.update_view()

    def compute_low_high_values(self):
        low_p, high_p = self.low_slider.value(), self.high_slider.value()
        if high_p <= low_p:
            high_p = min(low_p + 1, 100)
            for w, val in ((self.high_slider, high_p), (self.high_spin, high_p)):
                w.blockSignals(True); w.setValue(val); w.blockSignals(False)
        low_val = percentile_from_hist(self.hist, self.total_px, low_p)
        high_val = percentile_from_hist(self.hist, self.total_px, high_p)
        if high_val <= low_val:
            high_val = min(low_val + 1, 65535)
        return low_val, high_val

    @staticmethod
    def apply_curve_pointwise(t: np.ndarray, mode: str) -> np.ndarray:
        # t ∈ [0,1] en float32 — toutes les courbes partent de cette normalisation
        if mode == "linear":
            y = t
        elif mode == "gamma05":
            y = np.power(t, 0.5, dtype=np.float32)
        elif mode == "gamma20":
            y = np.power(t, 2.0, dtype=np.float32)
        elif mode == "sigmoid":
            gain = 10.0
            y = 1.0 / (1.0 + np.exp(-gain * (t - 0.5)))
            y = (y - y.min()) / max(1e-12, (y.max() - y.min()))
        elif mode == "log":
            c = 100.0
            y = np.log1p(c * t) / np.log1p(c)
        elif mode == "invlog":
            c = 4.0
            y = (np.expm1(c * t) / np.expm1(c)).astype(np.float32)
        elif mode == "exp":
            k = 0.7
            y = np.power(t, k, dtype=np.float32)
        elif mode == "sqrt":
            y = np.sqrt(t, dtype=np.float32)
        elif mode == "cbrt":
            y = np.power(t, 1.0 / 3.0, dtype=np.float32)
        else:
            y = t
        return np.clip(y, 0.0, 1.0).astype(np.float32)

    def stretch_to_8bit(self, arr16: np.ndarray, lv: int, hv: int) -> np.ndarray:
        # Normalisation stricte par bornes min/max choisies (percentiles) → T dans [0,1]
        rng = float(max(1, hv - lv))
        t = (arr16.astype(np.int32) - lv) / rng
        t = np.clip(t, 0.0, 1.0).astype(np.float32)

        mode = self.contrast_mode
        if mode == "he":
            y = he_on_unit_float(t, nbins=int(self.he_bins_spin.value()))
        elif mode == "clahe":
            y = clahe_on_unit_float(t, clip_limit=float(self.clahe_clip_spin.value()),
                                    nbins=int(self.he_bins_spin.value()))
        else:
            y = self.apply_curve_pointwise(t, mode)

        out = np.clip(y * 255.0, 0.0, 255.0).astype(np.uint8)
        return out

    # ---------- Rendu ----------
    def update_view(self):
        low_val, high_val = self.compute_low_high_values()
        img8 = self.stretch_to_8bit(self.arr16, low_val, high_val)
        qimg = qimage_from_gray_uint8(img8)
        self.pixmap_item.setPixmap(QtGui.QPixmap.fromImage(qimg))

        extra = ""
        if self.contrast_mode == "clahe" and not HAS_SKIMAGE:
            extra = " (CLAHE indisponible → HE)"
        title = (
            f"TIFF 16 bits – [{low_val} .. {high_val}] – {self.w}x{self.h} – "
            f"Mode: {self.contrast_mode}{extra} – HE bins={self.he_bins_spin.value()} – CLAHE clip={self.clahe_clip_spin.value():.3f}"
        )
        self.setWindowTitle(title)

    # ---------- Slots UI (rafraîchissement immédiat) ----------
    def _on_low_slider(self, val):
        self.low_spin.blockSignals(True)
        self.low_spin.setValue(val)
        self.low_spin.blockSignals(False)
        self.update_view()

    def _on_high_slider(self, val):
        if val <= self.low_slider.value():
            val = min(self.low_slider.value() + 1, 100)
            self.high_slider.blockSignals(True)
            self.high_slider.setValue(val)
            self.high_slider.blockSignals(False)
        self.high_spin.blockSignals(True)
        self.high_spin.setValue(val)
        self.high_spin.blockSignals(False)
        self.update_view()

    def _on_low_spin(self, val):
        self.low_slider.blockSignals(True)
        self.low_slider.setValue(val)
        self.low_slider.blockSignals(False)
        self.update_view()

    def _on_high_spin(self, val):
        if val <= self.low_spin.value():
            val = min(self.low_spin.value() + 1, 100)
            self.high_spin.blockSignals(True)
            self.high_spin.setValue(val)
            self.high_spin.blockSignals(False)
        self.high_slider.blockSignals(True)
        self.high_slider.setValue(val)
        self.high_slider.blockSignals(False)
        self.update_view()

    def _on_mouse_moved(self, col: int, row: int):
        if col < 0 or row < 0:
            self.col_edit.setText("")
            self.row_edit.setText("")
        else:
            self.col_edit.setText(str(col))
            self.row_edit.setText(str(row))

    def apply_auto(self):
        self.low_slider.setValue(2)
        self.high_slider.setValue(98)
        self.update_view()

    def apply_full(self):
        self.low_slider.setValue(0)
        self.high_slider.setValue(100)
        self.update_view()

    def reset_view(self):
        self.view.resetTransform()
        self.update_view()


def view_tiff_qt(input_path):
    app = QtWidgets.QApplication(sys.argv[:1])
    w = Tiff16Viewer(input_path)
    w.resize(1200, 950)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    # Si pas d’argument, boîte de dialogue fichier puis dossier si besoin
    if len(sys.argv) >= 2:
        path_in = sys.argv[1]
    else:
        app = QtWidgets.QApplication(sys.argv[:1])
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        dlg.setNameFilter("Images TIFF (*.tif *.tiff)")
        if dlg.exec():
            selected = dlg.selectedFiles()[0]
            path_in = selected
        else:
            dlg = QtWidgets.QFileDialog()
            dlg.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
            if dlg.exec():
                path_in = dlg.selectedFiles()[0]
            else:
                sys.exit(0)
        app.quit()
    view_tiff_qt(path_in)
