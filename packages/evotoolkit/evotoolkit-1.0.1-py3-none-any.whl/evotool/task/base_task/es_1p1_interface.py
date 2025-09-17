import abc
from typing import List
from abc import abstractmethod

from .base_evaluator import Solution, EvaluationResult
from .base_method_interface import BaseMethodInterface
from .base_task_config import BaseTaskConfig



class Es1p1Interface(BaseMethodInterface):
    """ES(1+1) Adapter"""

    def __init__(self, task_config: BaseTaskConfig):
        super().__init__(task_config)

    def make_init_sol(self) -> Solution:
        return self.task_config.make_init_sol_wo_other_info()

    @abstractmethod
    def get_prompt(self, best_sol:Solution) -> List[dict]:
        raise NotImplementedError()

