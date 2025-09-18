import asyncio
import threading
from PyQt6.QtCore import QThread


INTERVAL = 5


EVENT_LOOPER = asyncio.new_event_loop()
__EVENT_LOOPER_THREAD = threading.Thread(target=EVENT_LOOPER.run_forever, daemon=True)
# class EventLooperThread(QThread):
#     def run(self):
#         EVENT_LOOPER.run_forever()

# __EVENT_LOOPER_THREAD = EventLooperThread()
__EVENT_LOOPER_THREAD.start()



def required[T](value: T | None) -> T:
    if value is None:
        raise ValueError("Value cannot be None")
    return value

