# -*- encoding: utf-8 -*-
"""
@File: main.py
@Modify Time: 2024/10/1 16:12       
@Author: Kevin-Chen
@Descriptions: 
"""

import sys
import time
import imageio
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets


class SelectionWidget(QtWidgets.QWidget):
    selectionMade = QtCore.pyqtSignal(QtCore.QRect)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('选择录制范围')
        self.screen = QtWidgets.QApplication.primaryScreen()
        # 设置窗口标志为无边框、置顶
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        # 设置窗口大小为屏幕尺寸
        self.setGeometry(self.screen.geometry())
        # 设置窗口背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 确保窗口接收鼠标事件
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        # 设置鼠标为十字光标
        self.setCursor(QtCore.Qt.CrossCursor)
        self.origin = QtCore.QPoint()
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # 使用半透明的黑色填充窗口
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 100))

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        selectedRect = QtCore.QRect(self.mapToGlobal(self.origin), self.mapToGlobal(event.pos())).normalized()
        self.selectionMade.emit(selectedRect)
        self.close()


class RecorderThread(QtCore.QThread):
    frameCaptured = QtCore.pyqtSignal(int)

    def __init__(self, rect):
        super().__init__()
        self.rect = rect
        self.frames = []
        self.isRecording = False
        self.screen = QtWidgets.QApplication.primaryScreen()

    def run(self):
        self.isRecording = True
        while self.isRecording:
            pixmap = self.screen.grabWindow(0, self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height())
            self.frames.append(pixmap.toImage())
            self.frameCaptured.emit(len(self.frames))
            time.sleep(0.1)  # 10 FPS

    def stop(self):
        self.isRecording = False
        self.wait()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('屏幕录制转GIF')
        self.setFixedSize(550, 350)
        self.rect = None
        self.frames = []

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.selectButton = QtWidgets.QPushButton('选择范围')
        self.selectButton.clicked.connect(self.openSelectionWidget)
        self.layout.addWidget(self.selectButton)

        self.startButton = QtWidgets.QPushButton('开始')
        self.startButton.clicked.connect(self.startRecording)
        self.startButton.setEnabled(False)
        self.layout.addWidget(self.startButton)

        self.endButton = QtWidgets.QPushButton('结束')
        self.endButton.clicked.connect(self.endRecording)
        self.endButton.setEnabled(False)
        self.layout.addWidget(self.endButton)

        self.statusLabel = QtWidgets.QLabel('请先选择录制范围')
        self.layout.addWidget(self.statusLabel)

        self.recorderThread = None

    def openSelectionWidget(self):
        self.hide()
        self.selectionWidget = SelectionWidget()
        self.selectionWidget.selectionMade.connect(self.setSelection)
        self.selectionWidget.show()

    def setSelection(self, rect):
        self.rect = rect
        self.startButton.setEnabled(True)
        self.statusLabel.setText(f'已选择区域：{rect}')
        self.show()

    def startRecording(self):
        if self.rect:
            self.recorderThread = RecorderThread(self.rect)
            self.recorderThread.frameCaptured.connect(self.updateStatus)
            self.recorderThread.start()
            self.startButton.setEnabled(False)
            self.endButton.setEnabled(True)
            self.selectButton.setEnabled(False)
            self.statusLabel.setText('录制中...')

    def updateStatus(self, frameCount):
        self.statusLabel.setText(f'录制中... 已捕获帧数：{frameCount}')

    def endRecording(self):
        if self.recorderThread:
            self.recorderThread.stop()
            self.frames = self.recorderThread.frames
            self.saveRecording()
            self.resetUI()

    def saveRecording(self):
        options = QtWidgets.QFileDialog.Options()
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存GIF文件", "", "GIF文件 (*.gif)", options=options)
        if filePath:
            images = []
            for frame in self.frames:
                frame = frame.convertToFormat(QtGui.QImage.Format_RGBA8888)
                width = frame.width()
                height = frame.height()
                ptr = frame.bits()
                ptr.setsize(frame.byteCount())
                arr = np.array(ptr).reshape(height, width, 4)
                images.append(arr)
            imageio.mimsave(filePath, images, fps=10)
            QtWidgets.QMessageBox.information(self, '完成', f'GIF已保存到 {filePath}')
        else:
            QtWidgets.QMessageBox.warning(self, '取消', '未选择保存路径，录制已取消。')

    def resetUI(self):
        self.startButton.setEnabled(False)
        self.endButton.setEnabled(False)
        self.selectButton.setEnabled(True)
        self.statusLabel.setText('请先选择录制范围')
        self.frames = []

    def closeEvent(self, event):
        if self.recorderThread and self.recorderThread.isRunning():
            self.recorderThread.stop()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
