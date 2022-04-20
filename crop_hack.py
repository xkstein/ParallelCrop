#!/usr/bin/env python3

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout,\
        QVBoxLayout, QGridLayout, QFileDialog, QAction, QLineEdit, QLabel,  \
        QTabWidget, QPushButton
from src.ImagePlot import ImagePlot
from src.ImagePlotTab import ImagePlotTab
from src.count_grains import count_grains
import pyqtgraph as pg
from skimage import io
import numpy as np
import csv
import sys
import time

# TODO: re-implement all of these functions as toolbar functions
def key_press(event):
    # Locks ROI
    if event.text() == 'm':
        image_plot[2].roi.translatable = (image_plot[2].roi.translatable != True)

    # Does transformation with selected points
    elif event.text() == 'a':
        # The fused image on the right:
        image_plot[2].roi.setSize(pg.Point(c_size[0], c_size[1]))
      
class Window(QMainWindow):
    sigKeyPress = pyqtSignal(object)
    sigSave = pyqtSignal(object)
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Manual Align")

        self.central_win = QWidget()

        layout = QHBoxLayout()

        #self.table_widget = ImagePlotTableWidget(self)
        #self.table_widget = ImagePlotTab(self, ['img1', 'img2', 'img3', 'img4', 'img5'])
        self.table_widget = ImagePlotTab(self, ['1', '2', '3', '4', '5'])
        layout.addWidget(self.table_widget)

        trace_layout = QVBoxLayout()
        self.trace = ImagePlot(use_roi = True, slave_roi=False)
        self.trace.sigKeyPress.connect(key_press)
        self.trace.roi.sigRegionChanged.connect(self.trace_roi_moved)
        trace_layout.addWidget(self.trace)

        trace_info = QHBoxLayout()
        trace_button = QPushButton('Select Tracing')
        trace_button.clicked.connect(self.openTrace)
        trace_info.addWidget(trace_button)

        self.trace_label = QLabel('Test', self)
        self.trace.roi.sigRegionChangeFinished.connect(self.update_trace_text)
        trace_info.addWidget(self.trace_label)

        trace_layout.addLayout(trace_info)
        layout.addLayout(trace_layout)

        self.central_win.setLayout(layout)
        self.setCentralWidget(self.central_win)

        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")

        openTraceAction = QAction("&Open Tracing", self)
        openTraceAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_O))
        openTraceAction.triggered.connect(self.openTrace)
        fileMenu.addAction(openTraceAction)

        saveAction = QAction("&Save All...", self)
        saveAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        saveAction.triggered.connect(self.save_all)
        fileMenu.addAction(saveAction)

        saveTraceAction = QAction("&Save Trace Image...", self)
#        saveTraceAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_T))
        saveTraceAction.triggered.connect(self.save_trace)
        fileMenu.addAction(saveTraceAction)

    def trace_roi_moved(self):
        if self.trace.active:
            pos = self.trace.roi.pos()
            size = self.trace.roi.size()
            self.table_widget.roi_move((pos, size))

    def openTrace(self):
        if select := QFileDialog.getOpenFileName(win, 'Open file', '.', "Image files (*.jpg *.gif *.png *.tif)")[0]:
            self.trace.setImage(select)
    
    def save_all(self):
        self.trace_roi_moved()
        if select := QFileDialog.getSaveFileName(win, 'Save Aligned Image', '.')[0]:
            suf = select.split('/')[-1]
            out_dir = select[:-len(suf)]
            self.sigSave.emit((out_dir, suf))
            save_path = out_dir + 'trace' + suf + '.png'
            self.trace.save_roi(save_path)
    
    def update_trace_text(self, ev):
        grains = count_grains(self.trace.getROI())
        self.trace_label.setText(f'Grains in ROI: {grains}')

    def save_trace(self):
        if select := QFileDialog.getSaveFileName(win, 'Save Aligned Image', '.')[0]:
            suf = select.split('/')[-1]
            out_dir = select[:-len(suf)]
            save_path = out_dir + 'trace' + suf + '.png'
            self.trace.save_roi(save_path)

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
app = QApplication([])
win = Window()

# You can access points by accessing image_plot1.points
win.show()

if (sys.flags.interactive != 1) or not hasattr(Qt.QtCore, "PYQT_VERSION"):
    QApplication.instance().exec_()

