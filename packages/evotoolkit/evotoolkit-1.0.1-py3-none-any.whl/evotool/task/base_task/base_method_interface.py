import abc
from abc import abstractmethod
from .base_evaluator import Solution
from .base_task_config import BaseTaskConfig


class BaseMethodInterface(abc.ABC):
    """Base Adapter"""
    def __init__(self, task_config: BaseTaskConfig):
        self.task_config = task_config

    @abstractmethod
    def make_init_sol(self) -> Solution:
        """Create initial solution from task info."""
        raise NotImplementedError()

    @abstractmethod
    def parse_response(self, response_str: str) -> Solution:
        raise NotImplementedError()