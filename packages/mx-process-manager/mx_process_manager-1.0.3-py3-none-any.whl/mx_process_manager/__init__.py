# 增加全局的异常处理，在KeyboardInterrupt时忽略打印
import logging.handlers
import sys
import os
import signal
import logging

from PyQt6.QtWidgets import QApplication

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 捕获KeyboardInterrupt异常
def signal_handler(signal, frame):
    logger.info("Process manager interrupted by user.")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)