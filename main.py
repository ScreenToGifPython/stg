# 导入必要的模块
import sys  # 提供对Python解释器的一些变量和函数的访问
import time  # 提供各种时间相关的函数
import imageio  # 用于读取和写入各种图像和视频格式
import numpy as np  # 用于科学计算，提供多维数组对象和各种派生对象
from PyQt5 import QtCore, QtGui, QtWidgets  # PyQt5框架的核心模块，用于创建GUI应用
from PIL import Image  # Python图像库，用于打开、操作和保存多种格式的图像文件

'''
这些包的用途解释：

1. sys：
   - 用于与Python解释器交互
   - 在本程序中主要用于处理命令行参数和退出应用程序
2. time：
   - 提供各种时间相关的函数
   - 在本程序中用于测量录制时间和控制帧率
3. imageio：
   - 用于读取和写入各种图像和视频格式
   - 虽然在提供的代码片段中没有直接使用，但可能在完整代码中用于保存GIF
4. numpy (np)：
   - 提供大量的数学函数和数组操作功能
   - 在本程序中用于图像数据的处理和操作
5. PyQt5 (QtCore, QtGui, QtWidgets)：
   - QtCore：提供核心的非GUI功能，��和槽机制、属性系统等
   - QtGui：提供窗口系统集成、事件处理、2D图形、基本图像、字体和文本等类
   - QtWidgets：提供一套UI元素来创建经典的桌面风格用户界面
6. PIL (Python Imaging Library)：
   - 提供图像处理和图形功能
   - 在本程序中用于处理和保存捕获的屏幕图像，特别是在创建GIF时
'''


class RecorderThread(QtCore.QThread):
    """
RecorderThread 类实现了以下主要功能：
1. 屏幕录制：
    它能够在指定的屏幕区域内进行连续的截图，从而实现屏幕录制功能。
2. 帧率控制：
    通过设定的帧率（frame_rate）来控制录制的速度，确保录制的流畅性。
3. 时间限制：
    设置了15秒的录制时间限制，超过这个时间会自动停止录制。
4. 异步操作：
    继承自 QThread，使得录制过程可以在后台线程中进行，不会阻塞主线程。
5. 状态管理：
    通过 isRecording 标志来管理录制的开始和结束状态。
6. 数据收集：
    将捕获的每一帧图像存储在 frames 列表中。
7. 实时反馈：
    使用 Qt 信号机制（frameCaptured 和 recordingTimeUpdated）来实时通知主线程录制的进度和时间。
8. 灵活控制：
    提供了 stop 方法允许外部控制录制的结束。
9. 间记录：
    记录制的开始和结束时间，便于后续处理（如计算总录制时间）。

总的来说，这个类封装了一个完整的屏幕录制功能，可以高效地捕获屏幕内容，并提供了必要的控制和反馈机制，使其能够很好地集成到更大的应用程序中。

    """
    # 定义信号，用于在捕获帧时发送帧数
    frameCaptured = QtCore.pyqtSignal(int)
    # 定义信号，用于更新录制时间
    recordingTimeUpdated = QtCore.pyqtSignal(float)

    def __init__(self, rect, frame_rate):
        # 调用父类的初始化方法
        super().__init__()
        # 存储要录制的屏幕区域
        self.rect = rect
        # 用于存储捕获的帧
        self.frames = []
        # 录制状态标志
        self.isRecording = False
        # 获取主屏幕对象，用于截图
        self.screen = QtWidgets.QApplication.primaryScreen()
        # 存储帧率
        self.frame_rate = frame_rate
        # 用于存储录制开始时间
        self.start_time = None
        # 用于存储录制结束时间
        self.end_time = None

    def run(self):
        # 设置录制状态为True
        self.isRecording = True
        # 计算每帧之间的睡眠时间，以达到指定帧
        sleep_time = 1.0 / self.frame_rate
        # 记录开始时
        self.start_time = time.time()

        while self.isRecording:
            # 获取当时间
            current_time = time.time()
            # 计算已经录制的时间
            elapsed_time = current_time - self.start_time

            # 如果录制时间达到或超过15秒，停止录制
            if elapsed_time >= 15:
                break

            # 捕获指定区域的屏幕截图
            pixmap = self.screen.grabWindow(0, self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height())
            # 将截图转换为QImage并添加到帧列表中
            self.frames.append(pixmap.toImage())
            # 发送信号，通知已捕获的帧数
            self.frameCaptured.emit(len(self.frames))
            # 发送信号，更新录制时间
            self.recordingTimeUpdated.emit(elapsed_time)
            # 根据帧率休眠，控制捕获速度
            time.sleep(sleep_time)

        # 记录结束时间
        self.end_time = time.time()
        # 确保录制状态设置为False
        self.isRecording = False

    def stop(self):
        # 设置录制状态为False，停止录制循环
        self.isRecording = False
        # 等待线程结束
        self.wait()


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        # 调用父类QWidget的初始化方法
        super().__init__()
        # 设置窗口标题
        self.setWindowTitle('屏幕录制转GIF v1.1.0')
        # 设置窗口固定大小为250x250像素
        self.setFixedSize(250, 250)
        # 初始化录制区域为None
        self.rect = None
        # 初始化帧列表为空
        self.frames = []

        # 设置默认参数
        self.frame_rate = 10  # 默认帧率为10帧/秒
        self.speed_multiplier = 1.0  # 默认播放速度倍数为1.0倍

        # 创建垂直布局 -----------------------------
        self.layout = QtWidgets.QVBoxLayout()
        # 将布局应用到窗口
        self.setLayout(self.layout)

        # 创建"选择范围"按钮 ------------------------
        self.selectButton = QtWidgets.QPushButton('选择范围')
        # 连接按钮点击事件到openSelectionWidget方法
        self.selectButton.clicked.connect(self.openSelectionWidget)
        # 将按钮添加到布局中
        self.layout.addWidget(self.selectButton)

        # 创建"开始"按钮 ---------------------------
        self.startButton = QtWidgets.QPushButton('开始')
        # 连接按钮点击事件到startRecording方法
        self.startButton.clicked.connect(self.startRecording)
        # 初时禁用"开始"按钮
        self.startButton.setEnabled(False)
        # 将按钮添加到布局中
        self.layout.addWidget(self.startButton)

        # 创建"结束"按钮 ---------------------------
        self.endButton = QtWidgets.QPushButton('结束')
        # 连接按钮点击事件到endRecording方法
        self.endButton.clicked.connect(self.endRecording)
        # 初始时禁用"结束"按钮
        self.endButton.setEnabled(False)
        # 将按钮添加到布局中
        self.layout.addWidget(self.endButton)

        # 创建状态标签 -----------------------------
        self.statusLabel = QtWidgets.QLabel('请先选择录制范围')
        # 将标签添加到布局中
        self.layout.addWidget(self.statusLabel)

        # 创建录制时间显示标签 ----------------------
        self.timeLabel = QtWidgets.QLabel('录制时间：0秒')
        # 将标签添加到布局中
        self.layout.addWidget(self.timeLabel)

        # 创建帧率选择的水平布局 ---------------------------------
        frame_rate_layout = QtWidgets.QHBoxLayout()
        # 创建帧率标签
        frame_rate_label = QtWidgets.QLabel('帧率 (f/s):')
        # 创建显示当帧率值的标签
        self.frame_rate_value_label = QtWidgets.QLabel(str(self.frame_rate))
        # 创帧率滑动条
        self.frame_rate_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # 设置滑动条的范围为1-50
        self.frame_rate_slider.setRange(1, 50)
        # 设置滑动条的初始值
        self.frame_rate_slider.setValue(self.frame_rate)
        # 设置滑动条的刻度位置
        self.frame_rate_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # 设置滑动条的刻度间隔
        self.frame_rate_slider.setTickInterval(5)
        # 连接滑动条值变化事件到updateFrameRate方法
        self.frame_rate_slider.valueChanged.connect(self.updateFrameRate)
        # 将各个组件添加到帧率布局中
        frame_rate_layout.addWidget(frame_rate_label)
        frame_rate_layout.addWidget(self.frame_rate_slider)
        frame_rate_layout.addWidget(self.frame_rate_value_label)
        # 将帧率布局添加到主布局中
        self.layout.addLayout(frame_rate_layout)

        # 创建播放速度倍数选择的水平布局 -----------------------------
        speed_multiplier_layout = QtWidgets.QHBoxLayout()
        # 创建播放速度倍数标签
        speed_multiplier_label = QtWidgets.QLabel('播放速度倍数:')
        # 创建显示当前播放速度倍数值的标签
        self.speed_multiplier_value_label = QtWidgets.QLabel(f'{self.speed_multiplier:.2f}')
        # 创建播放速度倍数滑动条
        self.speed_multiplier_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # 设置滑动条的范围为25-200（对应0.25到2.00倍速）
        self.speed_multiplier_slider.setRange(25, 200)
        # 设置滑动条的初始值
        self.speed_multiplier_slider.setValue(int(self.speed_multiplier * 100))
        # 设置滑动条的刻度位置
        self.speed_multiplier_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # 设置滑动条的刻度间隔
        self.speed_multiplier_slider.setTickInterval(25)
        # 连接滑动条值变化事件到updateSpeedMultiplier方法
        self.speed_multiplier_slider.valueChanged.connect(self.updateSpeedMultiplier)
        # 将各个组件添加到播放速度倍数布局中
        speed_multiplier_layout.addWidget(speed_multiplier_label)
        speed_multiplier_layout.addWidget(self.speed_multiplier_slider)
        speed_multiplier_layout.addWidget(self.speed_multiplier_value_label)
        # 将播放速度倍数布局添加到主布局中
        self.layout.addLayout(speed_multiplier_layout)

        # 初始化录制线程为None
        self.recorderThread = None

    def updateFrameRate(self, value):
        '''函数功能:更新帧率设置,并新UI显示'''
        # 更新帧率值
        self.frame_rate = value
        # 更新显示帧率的标签文本
        self.frame_rate_value_label.setText(str(self.frame_rate))

    def updateSpeedMultiplier(self, value):
        '''函数功能:更新播放速度倍数设置,并更新UI显示'''
        # 将滑动条的值(25-200)转换为实际的速度倍数(0.25-2.00)
        self.speed_multiplier = value / 100.0
        # 更新显示速度倍数的标签文本,保留两位小数
        self.speed_multiplier_value_label.setText(f'{self.speed_multiplier:.2f}')

    def openSelectionWidget(self):
        '''函数功能:打开选择录制区域的窗口'''
        # 隐藏主窗口
        self.hide()
        # 创建选择区域的窗口实例
        self.selectionWidget = SelectionWidget()
        # 连接选择完成的信号到setSelection方法
        self.selectionWidget.selectionMade.connect(self.setSelection)
        # 显示选择区域的窗口
        self.selectionWidget.show()

    def setSelection(self, rect):
        '''函数功能:设置选择的录制区域,更新UI状态'''
        # 保存选择的区域
        self.rect = rect
        # 启用开始按钮
        self.startButton.setEnabled(True)
        # 更新状态标签,显示选择的区域信息
        self.statusLabel.setText(f'已择区域：{rect}')
        # 显示主窗口
        self.show()

    def startRecording(self):
        '''函数功能:开始录制过程,创建并启动录制线程,更新UI状态'''
        if self.rect:
            # 创建录制线程,传入选择的区域和帧率
            self.recorderThread = RecorderThread(self.rect, self.frame_rate)
            # 连接帧捕获信号到更新状态的方法
            self.recorderThread.frameCaptured.connect(self.updateStatus)
            # 连接录制时间更新信号到更新时间显示的方法
            self.recorderThread.recordingTimeUpdated.connect(self.updateRecordingTime)
            # 启动录制线程
            self.recorderThread.start()
            # 禁用开始按钮
            self.startButton.setEnabled(False)
            # 启用结束按钮
            self.endButton.setEnabled(True)
            # 禁用选择区域按钮
            self.selectButton.setEnabled(False)
            # 更新状态标签
            self.statusLabel.setText('录制中...')

    def updateStatus(self, frameCount):
        '''函数功能:更新UI显示的录制状态,包括已捕获的帧数'''
        # 更新状态标签,显示当前捕获的帧数
        self.statusLabel.setText(f'录制中... 已捕获帧数：{frameCount}')

    def updateRecordingTime(self, elapsed_time):
        '''函数功能:更新UI显示的录制时间'''
        # 更新时间标签,显示已录制的时间(秒)
        self.timeLabel.setText(f'录制时间：{int(elapsed_time)}秒')

    def endRecording(self):
        """
        结束录制过程,停止录制线程,保存录制内容,并重置UI
        """
        # 检查录制线程是否存在且正在录制
        if self.recorderThread and self.recorderThread.isRecording:
            # 停止录制线程
            self.recorderThread.stop()
            # 等待线程完全停止
            self.recorderThread.wait()
            # 获取录制的帧
            self.frames = self.recorderThread.frames
            # 计算总录制时间
            self.total_recording_time = self.recorderThread.end_time - self.recorderThread.start_time
            # 保存录制内容
            self.saveRecording()
            # 重置UI状态
            self.resetUI()

    def saveRecording(self):
        """
        保存录制的内容为GIF文件。
        此函数负责打开文件保存对话框,处理录制的帧,
        并将它们保存为一个GIF动画文件。
        """
        # 设置文件对话框选项
        options = QtWidgets.QFileDialog.Options()
        # 打开保存文件对话框,获取保存路径
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存GIF文件", "", "GIF文件 (*.gif)", options=options)

        if filePath:
            # 初始化图像列表
            images = []
            # 获取总帧数
            total_frames = len(self.frames)

            # 检查是否有录制到帧
            if total_frames == 0:
                QtWidgets.QMessageBox.warning(self, '警告', '没有录制到任何帧。')
                return

            # 计算原始每帧持续时间
            original_duration_per_frame = self.total_recording_time / total_frames
            # 根据播放速度倍数计算GIF中每帧的持续时间（毫秒）
            duration_per_frame = (original_duration_per_frame / self.speed_multiplier) * 1000

            # 遍历所有录制的帧
            for frame in self.frames:
                # 将 QImage 转换为 RGBA8888 格式
                frame = frame.convertToFormat(QtGui.QImage.Format_RGBA8888)
                # 获取图像宽度和高度
                width = frame.width()
                height = frame.height()
                # 获取图像数据指针
                ptr = frame.bits()
                # 设置指针大小为图像字节数
                ptr.setsize(frame.byteCount())
                # 将图像数据转换为NumPy数组
                arr = np.array(ptr).reshape(height, width, 4)

                # 将NumPy数组转换为PIL图像
                img = Image.fromarray(arr, 'RGBA').convert('P', palette=Image.ADAPTIVE)
                # 将PIL图像添加到图像列表
                images.append(img)

            # 尝试保存GIF文件
            try:
                # 使用第一帧作为基础,保存所有帧为GIF
                images[0].save(
                    filePath,
                    save_all=True,  # 保存所有帧
                    append_images=images[1:],  # 添加后续帧
                    duration=duration_per_frame,  # 设置帧持续时间
                    loop=0,  # 设置循环次数,0表示无限循环
                    optimize=True  # 优化GIF文件大小
                )
            except Exception as e:
                # 如果保存失败,显示错误消息
                QtWidgets.QMessageBox.warning(self, '保存失败', f'GIF保存失败：{str(e)}')
        else:
            # 如果用户取消保存,显示取消消息
            QtWidgets.QMessageBox.warning(self, '取消', '未选择保存路径，录制已取消。')

    def resetUI(self):
        """
        重置用户界面到初始状态。
        此函数在录制结束后调用,用于重置所有UI元素到初始状态,
        包括按钮状态、标签文本和清空已录制的帧。
        """
        # 禁用"开始"按钮,因为还没有选择新的录制区域
        self.startButton.setEnabled(False)
        # 禁用"结束"按钮,因为没有正在进行的录制
        self.endButton.setEnabled(False)
        # 启用"选择范围"按钮,允许用户重新选择录制区域
        self.selectButton.setEnabled(True)
        # 重置状态标签文本,提示用户选择录制范围
        self.statusLabel.setText('请先选择录制范围')
        # 重置录制时间标签,显示初始时间为0秒
        self.timeLabel.setText('录制时间：0秒')
        # 清空已录制的帧列表
        self.frames = []

    def closeEvent(self, event):
        """
        处理窗口关闭事件。
        此函数在用户尝试关闭应用程序窗口时被调用,
        确保在关闭窗口前停止所有正在进行的录制线程。
        """
        # 检查是否存在录制线程且正在运行
        if self.recorderThread and self.recorderThread.isRunning():
            # 停止录制线程
            self.recorderThread.stop()
            # 等待录制线程完全停止
            self.recorderThread.wait()
        # 接受关闭事件,允许窗口关闭
        event.accept()


class SelectionWidget(QtWidgets.QWidget):
    """
    SelectionWidget类用于创建一个全屏透明窗口,允许用户通过鼠标拖动选择屏幕的特定区域。
    这个类主要用于屏幕录制应用中,让用户可以自定义要录制的屏幕区域。
    """
    # 定义一个自定义信号,当用户完成选择时发出,携带选择的矩形区域
    selectionMade = QtCore.pyqtSignal(QtCore.QRect)

    def __init__(self):
        """
        初始化SelectionWidget实例,设置窗口属性和初始化必要的变量。
        """
        # 调用父类的初始化方法
        super().__init__()
        # 设置窗口标题
        self.setWindowTitle('选择录制范围')
        # 获取主屏幕对象
        self.screen = QtWidgets.QApplication.primaryScreen()
        # 设置窗口标志为无边框、置顶
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        # 设置窗口大小为整个屏幕的尺寸
        self.setGeometry(self.screen.geometry())
        # 设置窗口背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 确保窗口可以接收鼠标事件
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        # 设置鼠标光标为十字形状
        self.setCursor(QtCore.Qt.CrossCursor)
        # 初始化起始点
        self.origin = QtCore.QPoint()
        # 创建一个橡皮筋选择框
        self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

    def paintEvent(self, event):
        """
        重写paintEvent方法,在窗口上绘制半透明的黑色遮罩。
        """
        # 创建QPainter对象
        painter = QtGui.QPainter(self)
        # 使用半透明的黑色填充整个窗口
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 100))

    def mousePressEvent(self, event):
        """
        处理鼠标按下事件,记录起始点并显示橡皮筋选择框。
        """
        # 记录鼠标按下的位置作为起始点
        self.origin = event.pos()
        # 设置橡皮筋选择框的初始大小
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        # 显示橡皮筋选择框
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        """
        处理鼠标移动事件,更新橡皮筋选择框的大小。
        """
        # 根据鼠标当前位置更新橡皮筋选择框的大小
        self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        """
        处理鼠标释放事件,隐藏橡皮筋选择框,发送选择完成的信号,并关闭窗口。
        """
        # 隐藏橡皮筋选择框
        self.rubberBand.hide()
        # 计算选择的矩形区域（转换为全局坐标）
        selectedRect = QtCore.QRect(self.mapToGlobal(self.origin), self.mapToGlobal(event.pos())).normalized()
        # 发送选择完成的信号,携带选择的矩形区域
        self.selectionMade.emit(selectedRect)
        # 关闭选择窗口
        self.close()


if __name__ == '__main__':
    # 创建 QApplication 实例
    # QApplication 管理图形用户界面应用程序的控制流和主要设置
    app = QtWidgets.QApplication(sys.argv)

    # 创建 MainWindow 类的实例
    # MainWindow 是我们自定义的主窗口类,包含了应用程序的主要界面和功能
    mainWin = MainWindow()

    # 显示主窗口
    # 这会使主窗口可见
    mainWin.show()

    # 进入应用程序的主事件循环并等待直到退出
    # app.exec_() 启动Qt事件循环
    # sys.exit() 确保应用程序干净地退出
    # 当最后一个窗口关闭时,事件循环将退出,返回exec_()的值
    sys.exit(app.exec_())
