import time
import pythoncom
import win32api
from win32com.taskscheduler import taskscheduler

task_name = "mlb_videos_worst_calls_yesterday"
task_program = r"C:\\Users\rcope\miniconda3\python.exe"
task_script = "examples/worst_calls_yesterday.py"


ts = pythoncom.CoCreateInstance(
    taskscheduler.CLSID_CTaskScheduler,
    None,
    pythoncom.CLSCTX_INPROC_SERVER,
    taskscheduler.IID.ITaskScheduler,
)

tasks = ts.Enum()
if task_name in tasks:
    print(f"Deleting existing scheduled task: {task_name}")
