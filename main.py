import sys
import time
import imageio
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image  # 用于图像处理

class RecorderThread(QtCore.QThread):
    frameCaptured = QtCore.pyqtSignal(int)
    recordingTimeUpdated = QtCore.pyqtSignal(float)  # 用于传递录制时间

    def __init__(self, rect, frame_rate):
        super().__init__()
        self.rect = rect
        self.frames = []
        self.isRecording = False
        self.screen = QtWidgets.QApplication.primaryScreen()
        self.frame_rate = frame_rate
        self.start_time = None
        self.end_time = None

    def run(self):
        self.isRecording = True
        sleep_time = 1.0 / self.frame_rate
        self.start_time = time.time()  # 记录开始时间
        while self.isRecording:
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            if elapsed_time >= 15:
                # 达到15秒，停止录制
                break
            pixmap = self.screen.grabWindow(0, self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height())
            self.frames.append(pixmap.toImage())
            self.frameCaptured.emit(len(self.frames))
            self.recordingTimeUpdated.emit(elapsed_time)
            time.sleep(sleep_time)  # 根据帧率调整
        self.end_time = time.time()  # 记录结束时间
        self.isRecording = False  # 确保录制状态为False

    def stop(self):
        self.isRecording = False
        self.wait()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('屏幕录制转GIF')
        self.setFixedSize(250, 250)
        self.rect = None
        self.frames = []

        # 默认参数
        self.frame_rate = 10  # 默认帧率
        self.speed_multiplier = 1.0  # 默认播放速度倍数

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

        # 录制时间显示
        self.timeLabel = QtWidgets.QLabel('录制时间：0秒')
        self.layout.addWidget(self.timeLabel)

        # 帧率选择（使用滑动条）
        frame_rate_layout = QtWidgets.QHBoxLayout()
        frame_rate_label = QtWidgets.QLabel('帧率 (f/s):')
        self.frame_rate_value_label = QtWidgets.QLabel(str(self.frame_rate))
        self.frame_rate_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.frame_rate_slider.setRange(1, 50)
        self.frame_rate_slider.setValue(self.frame_rate)
        self.frame_rate_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.frame_rate_slider.setTickInterval(5)
        self.frame_rate_slider.valueChanged.connect(self.updateFrameRate)
        frame_rate_layout.addWidget(frame_rate_label)
        frame_rate_layout.addWidget(self.frame_rate_slider)
        frame_rate_layout.addWidget(self.frame_rate_value_label)
        self.layout.addLayout(frame_rate_layout)

        # 播放速度倍数选择（使用滑动条）
        speed_multiplier_layout = QtWidgets.QHBoxLayout()
        speed_multiplier_label = QtWidgets.QLabel('播放速度倍数:')
        self.speed_multiplier_value_label = QtWidgets.QLabel(f'{self.speed_multiplier:.2f}')
        self.speed_multiplier_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_multiplier_slider.setRange(25, 200)  # 对应0.25到2.00
        self.speed_multiplier_slider.setValue(int(self.speed_multiplier * 100))
        self.speed_multiplier_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.speed_multiplier_slider.setTickInterval(25)
        self.speed_multiplier_slider.valueChanged.connect(self.updateSpeedMultiplier)
        speed_multiplier_layout.addWidget(speed_multiplier_label)
        speed_multiplier_layout.addWidget(self.speed_multiplier_slider)
        speed_multiplier_layout.addWidget(self.speed_multiplier_value_label)
        self.layout.addLayout(speed_multiplier_layout)

        self.recorderThread = None

    def updateFrameRate(self, value):
        self.frame_rate = value
        self.frame_rate_value_label.setText(str(self.frame_rate))

    def updateSpeedMultiplier(self, value):
        self.speed_multiplier = value / 100.0
        self.speed_multiplier_value_label.setText(f'{self.speed_multiplier:.2f}')

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
            self.recorderThread = RecorderThread(self.rect, self.frame_rate)
            self.recorderThread.frameCaptured.connect(self.updateStatus)
            self.recorderThread.recordingTimeUpdated.connect(self.updateRecordingTime)
            self.recorderThread.start()
            self.startButton.setEnabled(False)
            self.endButton.setEnabled(True)
            self.selectButton.setEnabled(False)
            self.statusLabel.setText('录制中...')

    def updateStatus(self, frameCount):
        self.statusLabel.setText(f'录制中... 已捕获帧数：{frameCount}')

    def updateRecordingTime(self, elapsed_time):
        self.timeLabel.setText(f'录制时间：{int(elapsed_time)}秒')

    def endRecording(self):
        if self.recorderThread and self.recorderThread.isRecording:
            self.recorderThread.stop()
            self.recorderThread.wait()
            self.frames = self.recorderThread.frames
            self.total_recording_time = self.recorderThread.end_time - self.recorderThread.start_time  # 计算总录制时间
            self.saveRecording()
            self.resetUI()

    def saveRecording(self):
        options = QtWidgets.QFileDialog.Options()
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存GIF文件", "", "GIF文件 (*.gif)", options=options)
        if filePath:
            images = []
            total_frames = len(self.frames)
            if total_frames == 0:
                QtWidgets.QMessageBox.warning(self, '警告', '没有录制到任何帧。')
                return

            # 原始每帧持续时间
            original_duration_per_frame = self.total_recording_time / total_frames
            # 计算GIF中每帧的持续时间（毫秒）
            duration_per_frame = (original_duration_per_frame / self.speed_multiplier) * 1000

            for frame in self.frames:
                # 将 QImage 转换为 NumPy 数组
                frame = frame.convertToFormat(QtGui.QImage.Format_RGBA8888)
                width = frame.width()
                height = frame.height()
                ptr = frame.bits()
                ptr.setsize(frame.byteCount())
                arr = np.array(ptr).reshape(height, width, 4)

                # 将 NumPy 数组转换为 PIL 图像
                img = Image.fromarray(arr, 'RGBA')

                images.append(img)

            # 保存为 GIF
            try:
                images[0].save(
                    filePath,
                    save_all=True,
                    append_images=images[1:],
                    duration=duration_per_frame,
                    loop=0
                )
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, '保存失败', f'GIF保存失败：{str(e)}')
        else:
            QtWidgets.QMessageBox.warning(self, '取消', '未选择保存路径，录制已取消。')

    def resetUI(self):
        self.startButton.setEnabled(False)
        self.endButton.setEnabled(False)
        self.selectButton.setEnabled(True)
        self.statusLabel.setText('请先选择录制范围')
        self.timeLabel.setText('录制时间：0秒')
        self.frames = []

    def closeEvent(self, event):
        if self.recorderThread and self.recorderThread.isRunning():
            self.recorderThread.stop()
            self.recorderThread.wait()
        event.accept()

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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
