import logging
import sys
import warnings

from PyQt6.QtWidgets import QApplication
from mx_process_manager.manager import ProcessManager


# 过滤掉所有 sipPyTypeDict 相关的弃用警告
warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")

logger = logging.getLogger(__name__)

def main():
    app = QApplication(sys.argv)
    window = ProcessManager()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()