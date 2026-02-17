from celery import chain
from .tasks import extract_task, transform_task, load_task, notify_task

class Pipeline:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path

    def run_async(self):
        workflow = chain(
            extract_task.s(self.json_file_path),
            transform_task.s(),
            load_task.s(),
            notify_task.s()
        )
        result = workflow.apply_async()
        return result
