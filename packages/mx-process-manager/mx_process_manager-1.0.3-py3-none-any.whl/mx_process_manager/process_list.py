import asyncio
import threading
from typing import Any, NoReturn
import concurrent.futures
from mx_process_manager import formatter, support
import psutil
import time
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QObject  # Add QObject import
import signal

CPU_COUNT = psutil.cpu_count(logical=True) or 1  # 如果获取失败，默认为1个CPU
# 获取CPU的算力
def get_cpu_power():
    try:
        cpu_power = sum(psutil.cpu_freq().current for _ in range(CPU_COUNT))
        return cpu_power
    except Exception:
        return 0

CPU_POWER = get_cpu_power()


class ProcessItem:

    def __init__(self, proc: psutil.Process):
        self.pid = proc.pid
        self.ppid = proc.info['ppid']
        self.proc = proc
        self.info = self.__gen_info()
        self.formatted_info = self.__gen_formatted_info()
        self.children: list[ProcessItem] = []

    def __gen_info(self):
        try:
            used_cpu_time = self.proc.info['cpu_times'].user + self.proc.info['cpu_times'].system
            running_duration_time = datetime.now().timestamp() - self.proc.info['create_time']
            avg_time_percent = used_cpu_time / (running_duration_time * CPU_COUNT)
            # 平均每个单位秒，CPU的逻辑核总算力占用了多少
            avg_power = CPU_POWER * avg_time_percent
            return {
                'pid': self.proc.info['pid'],
                'ppid': self.proc.info['ppid'],
                'name': self.proc.info['name'],
                'cwd': self.proc.info['cwd'] if self.proc.info['cwd'] else "[unknown]",
                'cpu_time': self.proc.info['cpu_times'].user + self.proc.info['cpu_times'].system,
                'cpu_percent': self.proc.info['cpu_percent'],
                'start_time': self.proc.info['create_time'],
                'avg_power': avg_power,
                'memory': self.proc.info['memory_info'].rss,
                'memory_percent': self.proc.info['memory_percent'],
                'command': self.proc.info['cmdline'] if self.proc.info['cmdline'] else [f"[{self.proc.info['name']}]"],
                'username': self.proc.info['username'],
                'duration_time': datetime.now().timestamp() - self.proc.info['create_time'],
                'ports': "[pending]",
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}
        
    def __gen_formatted_info(self):
        if not self.info:
            return {}
        formatted_info = {
            ** self.info
        }
        for key in formatted_info.keys():
            formatted_info[key] = self.__getFormatter(key)(formatted_info[key])
        return formatted_info
    
    def aggregate(self, column: str):
        prefixed_column = f"_aggr_{column}"
        if self.info.get(prefixed_column) is not None:
            return self.info[prefixed_column]
        self.info[prefixed_column] = (sum(child.aggregate(column) for child in self.children) if self.children else 0) + self.info.get(column, 0)
        self.formatted_info[prefixed_column] = self.__getFormatter(column)(self.info[prefixed_column])
        return self.info[prefixed_column]
    
    def __getFormatter(self, column: str):
        return {
            'pid': lambda x: str(x),
            'ppid': lambda x: str(x),
            'cpu_time': lambda x: formatter.formatNumberWithUnits(x, [(100, '毫秒', '.02f'), (60, '.', '02d'), (60, ':', '02d'), (60, ':', '02d'), (24, '天 ', '')]),
            'cpu_percent': lambda x: f"{x:.1f}%",
            'start_time': lambda x: datetime.fromtimestamp(x).strftime('%m-%d %H:%M'),
            'avg_power': lambda x: formatter.formatNumberWithUnits(int(x * 1000), [(1000, 'K', ''), (1000, 'M', ''), (1000, 'G', ''), (1000, 'T', ''), (1000, 'P', '')], 2),
            'memory': lambda x: formatter.formatNumberWithUnits(int(x/1024/1024), [(1024, 'M', ''), (1024, 'G', ''), (1024, 'T', '')], 2),
            'command': lambda x: f"<{self.info["cwd"]}> {' '.join(x)}",
            'duration_time': lambda x: formatter.formatWithExample(int(x), formatter.EXAMPLE_DURATION_TIME)
        }.get(column, lambda x: str(x))


class ProcessListController(QObject):  # Change inheritance to QObject
    onProcessListChanged = pyqtSignal(dict)
    processes: dict[int, ProcessItem] = {}
    interval: int = support.INTERVAL

    _refresh_task: concurrent.futures.Future | None = None

    def __init__(self):
        super().__init__()

    async def __refresh_processes(self):
        await asyncio.sleep(0.2)
        fetchPortsCounter = 0
        fetchedPortsCache = {}
        while True:
            try:
                _processes: dict[int, ProcessItem] = {}
                for proc in psutil.process_iter(['name', 'pid', 'ppid', 'cpu_times', 'cpu_percent', 'create_time', 'memory_info', 'memory_percent', 'cmdline', 'username', 'cwd']):
                    try:
                        _processes[proc.pid] = ProcessItem(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                for pid, process in _processes.items():
                    parent_proc = _processes.get(process.ppid)
                    if parent_proc and parent_proc.pid != 1:
                        if parent_proc.pid != pid:
                            parent_proc.children.append(process)
                if fetchPortsCounter % 10 == 0:
                    fetchPortsCounter = fetchPortsCounter + 1
                    fetchedPortsCache = {pid: "[pending]" for pid in _processes.keys()}
                
                for pid, process in _processes.items():
                    if pid in fetchedPortsCache:
                        if fetchedPortsCache.get(pid) != "[pending]":
                            ports = fetchedPortsCache[pid]
                        else:
                            try:
                                ports = ",".join([f":{conn.laddr.port}" for conn in [conn for conn in process.proc.net_connections(kind="inet") if conn.status == "LISTEN"]])
                                ports = f"[{ports}]"
                            except Exception:
                                ports = "[permission denied]"
                            fetchedPortsCache[pid] = ports
                        process.info['ports'] = ports
                        process.formatted_info['ports'] = ports
                    else:
                        fetchedPortsCache[pid] = "[pending]"
                self.processes = _processes
                self.onProcessListChanged.emit(_processes)
                await asyncio.sleep(self.interval)
            except Exception as e:
                await asyncio.sleep(1)

    def setRefreshInterval(self, seconds: int):
        self.interval = seconds
        self.refresh()

    def refresh(self):
        if self._refresh_task:
            self._refresh_task.cancel()
        self._refresh_task = asyncio.run_coroutine_threadsafe(self.__refresh_processes(), support.EVENT_LOOPER)

    def start(self):
        self.refresh()

    def stop(self):
        if self._refresh_task:
            self._refresh_task.cancel()
    
    def kill_process_and_children(self, pid):
        asyncio.run_coroutine_threadsafe(self.__kill_process_and_children(pid), support.EVENT_LOOPER)

    async def __kill_process_and_children(self, pid):
        try:
            process = psutil.Process(pid)
            children = process.children(recursive=True)
            
            # 首先尝试使用SIGTERM
            for child in children:
                try:
                    child.send_signal(signal.SIGTERM)
                except psutil.NoSuchProcess:
                    pass
            try:
                process.send_signal(signal.SIGTERM)
            except psutil.NoSuchProcess:
                pass
            self.refresh()
            await asyncio.sleep(10)
            self.__force_kill_process_and_children(pid)
        except psutil.NoSuchProcess:
            pass
        self.refresh()

    def __force_kill_process_and_children(self, pid):
        try:
            # 检查进程是否还存在，如果存在则使用SIGKILL
            process = psutil.Process(pid)
            children = process.children(recursive=True)
            for child in children:
                try:
                    if child.is_running():
                        child.kill()
                except psutil.NoSuchProcess:
                    pass
            
            try:
                if process.is_running():
                    process.kill()
            except psutil.NoSuchProcess:
                pass
        except psutil.NoSuchProcess:
            pass
        self.refresh()