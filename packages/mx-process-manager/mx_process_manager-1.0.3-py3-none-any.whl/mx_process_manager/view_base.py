from PyQt6.QtCore import Qt

CONF_COLUMNS = [
    {"key": "name", "label": "进程名", "textAlign": Qt.AlignmentFlag.AlignLeft, "columnWidth": 150},
    {"key": "pid", "label": "PID", "textAlign": Qt.AlignmentFlag.AlignRight, "columnWidth": 70},
    {"key": "ppid", "label": "PPID", "textAlign": Qt.AlignmentFlag.AlignRight, "columnWidth": 70},
    {"key": "cpu_time", "label": "CPU时间", "textAlign": Qt.AlignmentFlag.AlignRight, "updateOnChanged": True, "columnWidth": 100, "aggregate": True},
    {"key": "cpu_percent", "label": "CPU率", "textAlign": Qt.AlignmentFlag.AlignRight, "updateOnChanged": True, "columnWidth": 60, "aggregate": True},
    {"key": "start_time", "label": "启动时间", "textAlign": Qt.AlignmentFlag.AlignRight, "updateOnChanged": True, "columnWidth": 80},
    {"key": "avg_power", "label": "平均算力(Hz)", "textAlign": Qt.AlignmentFlag.AlignRight, "updateOnChanged": True, "columnWidth": 90, "aggregate": True},
    {"key": "duration_time", "label": "已运行", "textAlign": Qt.AlignmentFlag.AlignRight, "updateOnChanged": True, "columnWidth": 100},
    {"key": "memory", "label": "内存占用", "textAlign": Qt.AlignmentFlag.AlignRight, "updateOnChanged": True, "columnWidth": 80, "aggregate": True},
    {"key": "command", "label": "命令", "textAlign": Qt.AlignmentFlag.AlignLeft, "columnWidth": 550},
    {"key": "username", "label": "用户名", "textAlign": Qt.AlignmentFlag.AlignLeft, "columnWidth": 80},
    {"key": "ports", "label": "端口", "textAlign": Qt.AlignmentFlag.AlignLeft, "updateOnChanged": True, "columnWidth": 120}
]
CONF_PID_COLUMN_IDX = next((i for i, col in enumerate(CONF_COLUMNS) if col["key"] == "pid"), 0)