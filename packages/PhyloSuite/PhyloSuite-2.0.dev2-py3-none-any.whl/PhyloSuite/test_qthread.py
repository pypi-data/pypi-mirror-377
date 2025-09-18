import sys
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class WorkThread(QThread):
    finished = pyqtSignal(object)  # 增加信号，用于返回结果

    def __init__(self, function, parent=None):
        super().__init__(parent)
        self.function = function

    def run(self):
        result = self.function()
        self.finished.emit(result)  # 把结果传回主线程

# GUI 示例
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QThread读取TSV示例")

        self.label = QLabel("未开始读取")
        self.button = QPushButton("读取 data.tsv")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.button.clicked.connect(self.load_data)

    def load_data(self):
        def read_tsv():
            df = pd.read_csv('data.tsv', sep='\t')
            return df

        self.thread = WorkThread(read_tsv)
        self.thread.finished.connect(self.on_data_loaded)
        self.thread.start()
        self.label.setText("正在读取...")

    def on_data_loaded(self, df):
        self.label.setText(f"读取完成：{len(df)} 行")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
