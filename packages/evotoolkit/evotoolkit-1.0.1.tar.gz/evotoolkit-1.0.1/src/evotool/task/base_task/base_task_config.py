import abc
from abc import abstractmethod
from .base_evaluator import Solution


class BaseTaskConfig(abc.ABC):
    """Base Task Adapter"""
    def __init__(self, task_info: dict):
        self.task_info = task_info

    # Task-wise methods
    @abstractmethod
    def get_base_task_description(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def make_init_sol_wo_other_info(self) -> Solution:
        """Create initial solution from task info without other_info."""
        raise NotImplementedError()