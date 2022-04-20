from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, \
                            QFileDialog, QTabWidget, QPushButton
from src.ImagePlot import ImagePlot
import numpy as np

class ImagePlotTab(QWidget):
    def __init__(self, parent, tab_names=None):
        super().__init__(parent)
        self.parent = parent
        layout = QGridLayout(self)

        if tab_names is None:
            tab_names = ['Image 1', 'Image 2']

        # Initialize tab screen
        self.tabs = QTabWidget()

        self.tab_list = []
        for name in tab_names:
            table = QWidget()
            self.tabs.addTab(table, name)
            self.tab_list.append({'obj': table, 'name': name})

        # initialize tabs
        for ind, name in enumerate(tab_names):
            vbox = QVBoxLayout()
            hbox = QHBoxLayout()

            select_button = QPushButton("Open Image")
            select_button.clicked.connect(self.select_pressed)
            clear_button = QPushButton("Clear")
            clear_button.clicked.connect(self.clear_pressed)

            hbox.addWidget(select_button)
            hbox.addWidget(clear_button)
            
            plot = ImagePlot(use_roi=True, slave_roi=True, roi_color='b')
            vbox.addWidget(plot)
            vbox.addLayout(hbox)

            self.tab_list[ind]['plot'] = plot
            self.tab_list[ind]['obj'].setLayout(vbox)
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        parent.sigSave.connect(self.save_all)

    def select_pressed(self):
        if select := QFileDialog.getOpenFileName(self.parent, 'Open file', '.', "Image files (*.jpg *.gif *.png *.tif)")[0]:
            self.tab_list[self.tabs.currentIndex()]['plot'].setImage(select)
            label = select.split('/')[-1][:-4]
            self.tabs.setTabText(self.tabs.currentIndex(), label)
            self.tab_list[self.tabs.currentIndex()]['name'] = label
        
    def clear_pressed(self, name):
        self.tab_list[self.tabs.currentIndex()]['plot'].clearImage()

    def save_all(self, event):
        out_dir, suf = event
        for tab in self.tab_list:
            if tab['plot'].active:
                save_path = out_dir + tab['name'] + suf + '.png'
                tab['plot'].save_roi(save_path)

    def roi_move(self, tensor):
        for tab_dict in self.tab_list:
            if tab_dict['plot'].active:
                tab_dict['plot'].roi_move(tensor)

