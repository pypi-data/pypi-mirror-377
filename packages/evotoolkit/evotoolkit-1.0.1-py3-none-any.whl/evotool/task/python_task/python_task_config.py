import abc
from abc import abstractmethod
from evotool.task.base_task import Solution
from evotool.task.base_task.base_task_config import BaseTaskConfig


class PythonTaskConfig(BaseTaskConfig):
    """Base Task Adapter"""
    def __init__(self, task_info: dict):
        super().__init__(task_info)

    # Task-wise methods
    @abstractmethod
    def get_base_task_description(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def make_init_sol_wo_other_info(self) -> Solution:
        """Create initial solution from task info without other_info."""
        raise NotImplementedError()