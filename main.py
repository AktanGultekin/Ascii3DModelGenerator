# ascii_stl_viewer.py
import sys
import math
from stl import mesh
from PyQt5 import QtWidgets, QtGui, QtCore
from functions import *

# Bold-Light Characters
ASCII_CHARS = "@%#*+=-:. "

class AsciiViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STL → 3D ASCII Viewer (Shaded)")
        self.resize(1000, 700)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Controls
        controls = QtWidgets.QHBoxLayout()
        load_btn = QtWidgets.QPushButton("Load STL")
        load_btn.clicked.connect(self.load_stl)
        controls.addWidget(load_btn)

        self.rx_slider = self._make_slider(-180, 180, 0, "Rot X", controls)
        self.ry_slider = self._make_slider(-180, 180, 0, "Rot Y", controls)
        self.rz_slider = self._make_slider(-180, 180, 0, "Rot Z", controls)
        self.zoom_slider = self._make_slider(1, 400, 100, "Zoom (%)", controls)

        controls.addStretch()
        layout.addLayout(controls)

        # ASCII Area
        self.ascii_area = QtWidgets.QPlainTextEdit()
        self.ascii_area.setReadOnly(True)
        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        font.setPointSize(8)
        self.ascii_area.setFont(font)
        layout.addWidget(self.ascii_area)

        # Status
        self.status = QtWidgets.QLabel("STL not loaded.")
        layout.addWidget(self.status)

        # Datas
        self.points = None
        self.brightness = None

        for s in (self.rx_slider, self.ry_slider, self.rz_slider, self.zoom_slider):
            s.valueChanged.connect(self.update_render)

        # Menu
        file_menu = self.menuBar().addMenu("&File")
        open_action = QtWidgets.QAction("Open...", self)
        open_action.triggered.connect(self.load_stl)
        file_menu.addAction(open_action)

    def _make_slider(self, minv, maxv, init, label, parent_layout):
        lbl = QtWidgets.QLabel(f"{label}: {init}")
        s = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        s.setMinimum(minv)
        s.setMaximum(maxv)
        s.setValue(init)
        s.setTickPosition(QtWidgets.QSlider.TicksBelow)
        s.setTickInterval((maxv-minv)//10 if maxv-minv>0 else 1)
        s.valueChanged.connect(lambda v, l=lbl, name=label: l.setText(f"{name}: {v}"))

        widget = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(widget)
        vbox.setContentsMargins(2,2,2,2)
        vbox.addWidget(lbl)
        vbox.addWidget(s)

        parent_layout.addWidget(widget)
        return s

    def load_stl(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select STL File", "", "STL Files (*.stl);;All Files (*)")
        if not path:
            return
        try:
            m = mesh.Mesh.from_file(path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"STL could not be read:\n{e}")
            return
        self.points, self.brightness = mesh_to_shaded_points(m)
        self.status.setText(f"Loaded: {path} | Vertices: {len(self.points)}")
        self.update_render()

    def update_render(self):
        if self.points is None:
            return
        rx = math.radians(self.rx_slider.value())
        ry = math.radians(self.ry_slider.value())
        rz = math.radians(self.rz_slider.value())
        zoom_percent = self.zoom_slider.value()
        scale = zoom_percent / 100.0 * 1.5

        w = max(40, self.ascii_area.viewport().width())
        h = max(20, self.ascii_area.viewport().height())
        fm = QtGui.QFontMetrics(self.ascii_area.font())
        char_w = fm.horizontalAdvance("W") or 7
        char_h = fm.height() or 12
        cols = max(80, int(w / char_w))
        rows = max(40, int(h / char_h))

        proj = project_points(self.points, width=cols, height=rows,
                              scale=scale, rx=rx, ry=ry, rz=rz)
        ascii_str = points_to_ascii_shaded(proj, self.brightness,
                                           cols=cols, rows=rows,
                                           chars=ASCII_CHARS)
        self.ascii_area.setPlainText(ascii_str)

def main():
    app = QtWidgets.QApplication(sys.argv)
    viewer = AsciiViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":

    main()
