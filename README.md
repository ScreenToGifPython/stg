
# Screen Capture to GIF Converter

This application is designed to capture a specified area of your screen and save it as a GIF file. It is built using Python and PyQt5, ensuring a user-friendly graphical interface and efficient handling of screen capturing.

## Features

- **Customizable Capture Area**: Select the specific screen area you want to capture.
- **Adjustable Frame Rate**: Control the smoothness of the output GIF by adjusting the frame rate.
- **Adjustable Speed Multiplier**: Modify the playback speed of the GIF.
- **Real-time Capture Feedback**: Displays the number of captured frames and total recording time in real-time.
- **Automatic Time Limit**: Stops recording automatically after 15 seconds to prevent unnecessarily long recordings.

## Requirements

Before you run the application, ensure that you have the following installed:

- Python 3.x
- PyQt5
- imageio
- NumPy
- Pillow (PIL)

## Installation

To set up the application on your local machine:

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2. **Install Dependencies**
    Use pip to install the required Python packages:
    ```bash
    pip install pyqt5 numpy imageio pillow
    ```

## Usage

To run the application, execute the following command in the terminal:

```bash
python main.py
```

### Steps to Capture and Save a GIF:

1. **Select Capture Area**: Click the 'Select Area' button and drag to select the area of your screen you want to capture.
2. **Start Recording**: Press the 'Start' button to begin capturing.
3. **End Recording**: Click the 'End' button once you're done, or wait for the automatic timeout.
4. **Save the GIF**: A dialog will prompt you to choose a location to save the GIF file.

## Customization

- **Frame Rate**: Adjust the frame rate slider to increase or decrease the number of frames captured per second.
- **Speed Multiplier**: Adjust the speed multiplier slider to change the playback speed of the generated GIF.

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change. Ensure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)


---


# 屏幕捕捉转GIF转换器

本应用旨在捕捉您屏幕上指定区域的内容，并将其保存为GIF文件。它使用Python和PyQt5构建，确保了用户友好的图形界面和高效的屏幕捕捉处理。

## 功能特点

- **可自定义的捕捉区域**：选择您想要捕捉的屏幕特定区域。
- **可调节的帧率**：通过调节帧率控制输出GIF的流畅度。
- **可调节的播放速度倍数**：修改GIF的播放速度。
- **实时捕捉反馈**：实时显示已捕获的帧数和总录制时间。
- **自动时间限制**：录制自动在15秒后停止，以防止不必要的长时间录制。

## 系统要求

在运行应用程序之前，请确保您已安装以下内容：

- Python 3.x
- PyQt5
- imageio
- NumPy
- Pillow（PIL）

## 安装

要在本地机器上设置应用程序：

1. **克隆仓库**
    ```bash
    git clone https://github.com/your-username/your-repository.git
    cd your-repository
    ```

2. **安装依赖**
    使用pip安装所需的Python包：
    ```bash
    pip install pyqt5 numpy imageio pillow
    ```

## 使用方法

要运行应用程序，在终端执行以下命令：

```bash
python main.py
```

### 捕捉并保存GIF的步骤：

1. **选择捕捉区域**：点击“选择区域”按钮并拖动以选择您屏幕上的区域。
2. **开始录制**：按下“开始”按钮开始捕捉。
3. **结束录制**：完成后点击“结束”按钮，或等待自动超时。
4. **保存GIF**：将会提示一个对话框，让您选择保存GIF文件的位置。

## 自定义

- **帧率**：调整帧率滑块以增加或减少每秒捕获的帧数。
- **速度倍数**：调整速度倍数滑块来改变生成GIF的播放速度。

## 贡献

欢迎贡献！对于重大变更，请先开一个议题讨论您希望改变的内容。适当时确保更新测试。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/)
