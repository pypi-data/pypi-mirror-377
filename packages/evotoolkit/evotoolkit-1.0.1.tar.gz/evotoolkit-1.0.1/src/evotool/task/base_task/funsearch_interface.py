from abc import ABC, abstractmethod
from typing import List
from .base_evaluator import Solution
from .base_method_interface import BaseMethodInterface
from .base_task_config import BaseTaskConfig



class FunSearchInterface(BaseMethodInterface):
    """Base adapter for FunSearch algorithm"""

    def __init__(self, task_config: BaseTaskConfig):
        super().__init__(task_config)

    def make_init_sol(self) -> Solution:
        return self.task_config.make_init_sol_wo_other_info()
    
    @abstractmethod
    def get_prompt(self, solutions: List[Solution]) -> List[dict]:
        """Generate prompt based on multiple solutions"""
        pass
