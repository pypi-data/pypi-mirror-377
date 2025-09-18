import asyncio
import logging
import re
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLineEdit, QLabel, QSlider, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import QtGui
from PyQt6.QtGui import QPalette, QColor
from mx_process_manager import support
from mx_process_manager.process_list import ProcessItem, ProcessListController
from mx_process_manager.view_base import CONF_COLUMNS
from mx_process_manager.view_table import ProcessTableView
from mx_process_manager.view_tree import ProcessTreeView


logger = logging.getLogger(__name__)

class ProcessManager(QMainWindow):
    __processFiltered = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.__filterTask = None
        self.__processFiltered.connect(self.__onProcessUpdateAndFiltered)

        self.search_filter = ""
        self.__aggregate_column = None

        self.controller = ProcessListController()
        self.controller.onProcessListChanged.connect(self.__update_process_list_for_view)
        self.controller.start()
        
        self.setWindowTitle("进程管理器")
        self.setGeometry(100, 100, 1600, 800)
        self.setup_ui()
        self.setup_dark_theme()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        logger.info("Process manager started.")

    def setup_dark_theme(self):
        # 设置深色主题
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)

    def setup_ui(self):
        # 设置默认字体大小
        # font = self.font()
        # font.setPointSize(12)
        # self.setFont(font)

        default_tree_mode = False  # 默认使用树形视图模式

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.main_layout = layout

        # 创建搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索进程:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.__on_search_change)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # 创建树形视图
        self.tree = ProcessTreeView(self.controller)
        self.tree.setVisible(default_tree_mode)  # 根据默认模式设置可见性
        layout.addWidget(self.tree)

        # 创建普通表格视图
        self.table = ProcessTableView(self.controller)
        self.table.setVisible(not default_tree_mode)  # 根据默认模式设置可见性
        layout.addWidget(self.table)

        # 创建刷新间隔控制
        refresh_layout = QHBoxLayout()
        refresh_label = QLabel("刷新间隔(秒):")
        self.switch_checkbox = QCheckBox("树表模式")
        self.switch_checkbox.setChecked(default_tree_mode)
        self.switch_checkbox.stateChanged.connect(self.__toggle_view_mode)

        self.refresh_slider = QSlider(Qt.Orientation.Horizontal)
        self.refresh_slider.setFixedWidth(200)
        self.refresh_slider.setRange(1, 60)
        self.refresh_slider.setValue(support.INTERVAL)
        self.refresh_slider.valueChanged.connect(self.__update_refresh_interval)
        self.refresh_value_label = QLabel(f"{self.refresh_slider.value()}秒")
        self.refresh_slider.valueChanged.connect(lambda value: self.refresh_value_label.setText(f"{value}秒"))
        
        self.view_combobox = QComboBox()
        self.view_combobox.addItems(["无"] + [column["label"] for column in CONF_COLUMNS if column.get("aggregate", False)])
        self.view_combobox.currentIndexChanged.connect(self.__on_aggregate_change)

        refresh_layout.addWidget(refresh_label)
        refresh_layout.addWidget(self.refresh_slider)
        refresh_layout.addWidget(self.refresh_value_label)
        refresh_layout.addStretch()
        refresh_layout.addWidget(QLabel("聚合列:"))
        refresh_layout.addWidget(self.view_combobox)
        refresh_layout.addWidget(self.switch_checkbox)

        layout.addLayout(refresh_layout)

    def __setAggregateColumn(self, column: str | None):
        self.__aggregate_column = None
        # 在CONF_COLUMNS中查找，如果每个元素的“key”的值以“_aggr”开头，则将该元素从list中直接删除
        for col in CONF_COLUMNS:
            if col.get('key', '').startswith('_aggr_'):
                CONF_COLUMNS.remove(col)
        if column is None:
            return
        # 找到column在CONF_COLUMNS中的索引
        column_idx = next((i for i, col in enumerate(CONF_COLUMNS) if col['key'] == column), None)
        if column_idx is not None:
            target_column = CONF_COLUMNS[column_idx]
            self.__aggregate_column = target_column['key']
            CONF_COLUMNS.insert(column_idx + 1, {
                ** target_column,
                'key': f"_aggr_{column}",
                'label': f"{target_column['label']}(s)",
                'columnWidth': target_column['columnWidth'] + 10,
                'aggregate': False
            })

    def __on_aggregate_change(self, index):
        column_key = self.view_combobox.currentText()
        if column_key == "无":
            self.__setAggregateColumn(None)
        else:
            column = next((col for col in CONF_COLUMNS if col["label"] == column_key), None)
            if column:
                self.__setAggregateColumn(column["key"])
        newTree = ProcessTreeView(self.controller)
        newTable = ProcessTableView(self.controller)
        newTree.setVisible(self.tree.isVisible())
        newTable.setVisible(self.table.isVisible())
        oldTree = self.tree
        oldTable = self.table
        self.main_layout.replaceWidget(oldTree, newTree)
        self.main_layout.replaceWidget(oldTable, newTable)
        oldTree.destroy()
        oldTable.destroy()
        self.tree = newTree
        self.table = newTable

        self.controller.refresh()

    def __update_refresh_interval(self, value: int):
        self.controller.setRefreshInterval(value)

    def __on_search_change(self, text):
        self.search_filter = text.lower()
        self.__update_process_list_for_view(self.controller.processes)

    def __toggle_view_mode(self, state):
        if state == Qt.CheckState.Checked.value:
            self.table.hide()
            self.tree.show()
        else:
            self.tree.hide()
            self.table.show()
        self.__update_process_list_for_view(self.controller.processes)

    async def __filter_matched_search_processes(self, processes: dict[int, ProcessItem]):
        filteredProcesses = {}
        if self.search_filter:
            columnsForFilter = ['pid', 'name', 'command', 'username', 'ports']
            try:
                search_matcher = re.compile(f".*?{self.search_filter}.*", re.IGNORECASE)
                for pid, item in processes.items():
                    for column in columnsForFilter:
                        if search_matcher.match(item.formatted_info[column]):
                            filteredProcesses[pid] = item
                            break
            except re.error as e:
                pass
        else:
            filteredProcesses = processes
        self.__processFiltered.emit(filteredProcesses)

    def __update_process_list_for_view(self, processes: dict[int, ProcessItem]):
        if self.__filterTask is not None:
            self.__filterTask.cancel()
        self.__filterTask = asyncio.run_coroutine_threadsafe(self.__filter_matched_search_processes(processes), support.EVENT_LOOPER)

    def __onProcessUpdateAndFiltered(self, filtered_processes):
        if self.__aggregate_column:
            for pid, item in filtered_processes.items():
                item.aggregate(self.__aggregate_column)
        if self.switch_checkbox.isChecked():
            self.tree.update_processes(filtered_processes)
        else:
            self.table.update_processes(filtered_processes)
        
    def closeEvent(self, a0: Optional[QtGui.QCloseEvent]):
        self.controller.stop()
        if a0:
            a0.accept()