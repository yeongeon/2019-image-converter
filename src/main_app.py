# -*- coding: utf-8 -*-
import sys
import os
from urllib import request

import cv2
from PySide2 import QtUiTools, QtGui
from PySide2.QtGui import QPixmap, QImage, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog

class MainView(QMainWindow):
    #__slots__ = ()
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.ui_template = QtUiTools.QUiLoader().load(resource_path("./ui/image-converter.ui"))
        self.initView()
        self.setCentralWidget(self.ui_template)
        self.setWindowTitle("Image Converter")
        self.setWindowIcon(QtGui.QPixmap(resource_path("./images/icon.png")))
        self.resize(1200, 800)
        self.show()

    def initView(self):
        self.display_image(resource_path("./images/no-image-box.png"))

        # 초기화
        self.ui_template.plainTextEdit_file.setEnabled(False)
        self.ui_template.plainTextEdit_file.setPlaceholderText("이미지 파일을 선택해주세요")
        self.ui_template.plainTextEdit_file.setPlainText("")

        # Step1. Input
        self.ui_template.radioButton_file.setChecked(True)
        self.ui_template.radioButton_file.clicked.connect(self.radioButtonClicked)
        self.ui_template.radioButton_url.clicked.connect(self.radioButtonClicked)
        self.ui_template.pushButton_load.clicked.connect(self.func_pushButton_load)
        # self.ui_template.progressBar_load.

        # Step2. Filtering
        # Grayfy
        self.ui_template.checkBox_grayfy.stateChanged.connect(self.grayfyChecked)
        # Scale
        self.ui_template.horizontalSlider_scale.setTickInterval(10)
        self.ui_template.horizontalSlider_scale.setSingleStep(1)
        self.ui_template.horizontalSlider_scale.valueChanged[int].connect(self.changedSliderValue)

        # Rotation
        self.ui_template.pushButton_rotationLeft.clicked.connect(self.rotationLeft)
        self.ui_template.pushButton_rotationRight.clicked.connect(self.rotationRight)
        # Format Converting
        self.ui_template.comboBox_formats.addItems(['변경할 이미지 포멧을 선택하세요'])
        self.ui_template.comboBox_formats.insertSeparator(2)
        list1 = [
            self.tr('png'),
            self.tr('jpg'),
            self.tr('gif'),
        ]
        self.ui_template.comboBox_formats.addItems(list1)
        self.ui_template.comboBox_formats.setCurrentIndex(0)

        # Step3. Output
        self.ui_template.pushButton_save.clicked.connect(self.func_pushButton_save)

        # turn on buttons
        self.func_turn_off()

    def radioButtonClicked(self):
        if self.ui_template.radioButton_file.isChecked() :
            print("GroupBox_rad1 Chekced")
            # self.ui_template.progressBar_load.setWindowOpacity(100.0);
            self.ui_template.plainTextEdit_file.setEnabled(False)
            self.ui_template.plainTextEdit_file.setPlaceholderText("이미지 파일을 선택해주세요")
            self.ui_template.plainTextEdit_file.setPlainText("")
        elif self.ui_template.radioButton_url.isChecked() :
            print("GroupBox_rad2 Checked")
            # self.ui_template.progressBar_load.setWindowOpacity(0.0);
            self.ui_template.plainTextEdit_file.setPlainText("")
            self.ui_template.plainTextEdit_file.setEnabled(True)
            self.ui_template.plainTextEdit_file.setPlaceholderText("이미지 URL을 입력하세요")
            self.ui_template.plainTextEdit_file.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard | Qt.TextEditable)
        return

    def func_pushButton_load(self):
        if self.ui_template.radioButton_file.isChecked() :
            fname = QFileDialog.getOpenFileName(self, filter="Image Files (*.jpg *.jpeg *.gif *.png *.JPG *.JPEG *.GIF *.PNG)")
            self.display_fpath(fname[0])
            self.display_image(fname[0])
        elif self.ui_template.radioButton_url.isChecked():
            url = self.ui_template.plainTextEdit_file.toPlainText()
            image = request.urlopen(url).read()

            pixmap = QPixmap()
            pixmap.loadFromData(image)
            self.ui_template.label_preview.setPixmap(pixmap)

        # turn on buttons
        self.func_turn_on()
        return

    def func_turn_on(self):
        self.ui_template.checkBox_grayfy.setEnabled(True)
        self.ui_template.horizontalSlider_scale.setEnabled(True)
        self.ui_template.pushButton_rotationLeft.setEnabled(True)
        self.ui_template.pushButton_rotationRight.setEnabled(True)
        self.ui_template.comboBox_formats.setEnabled(True)
        self.ui_template.pushButton_save.setEnabled(True)

    def func_turn_off(self):
        self.ui_template.checkBox_grayfy.setEnabled(False)
        self.ui_template.horizontalSlider_scale.setEnabled(False)
        self.ui_template.pushButton_rotationLeft.setEnabled(False)
        self.ui_template.pushButton_rotationRight.setEnabled(False)
        self.ui_template.comboBox_formats.setEnabled(False)
        self.ui_template.pushButton_save.setEnabled(False)


    def func_pushButton_save(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')
        pixmap = self.ui_template.label_preview.pixmap()
        pixmap.save(name[0])

    def grayfyChecked(self):
        if self.ui_template.checkBox_grayfy.isChecked():
            print("CHECKED!")
            path = self.ui_template.plainTextEdit_file.toPlainText()


            gray_img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

            height, width = gray_img.shape[:2]
            pmap = QImage(gray_img, width, height, QImage.Format_Grayscale8)
            # QPixmap::fromImage(*Img);
            pmap = self.adjust_resize_image(pmap)
            self.ui_template.label_preview.setPixmap(pmap)
        else:
            print("UNCHECKED!")

    def changedSliderValue(self, val):
        pmap = self.adjust_scale_image(val)
        self.ui_template.label_preview.setPixmap(pmap)
        print(val)

    def rotationLeft(self):
        print('left')

    def rotationRight(self):
        print('right')

    def display_fpath(self, fname):
        self.ui_template.plainTextEdit_file.setPlainText(fname)

    def display_image(self, fname):
        pmap = QPixmap(fname)
        pmap = self.adjust_resize_image(pmap)
        self.ui_template.label_preview.setPixmap(pmap)

    def adjust_resize_image(self, pmap):
        frame_width = self.ui_template.label_preview.width()
        frame_height = self.ui_template.label_preview.height()
        img_width = pmap.width()
        img_height = pmap.height()
        if img_width > frame_width :
            pmap.scaledToWidth(frame_width)
            return pmap
        elif img_height > frame_height :
            pmap.scaledToHeight(frame_height)
            return pmap
        return pmap

    def adjust_scale_image(self, val):
        frame_width = self.ui_template.label_preview.width()
        pmap = self.ui_template.label_preview.pixmap()
        img_width = pmap.width()

        middle = 50
        ratio = (middle-val)/middle
        print(ratio)
        img_width = frame_width * ratio
        pmap.scaledToWidth(img_width)

        return pmap

def resource_path(relative_path):
    return os.path.join(os.path.abspath("./../resources/"), relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainView()
    #main.show()

    sys.exit(app.exec_())

