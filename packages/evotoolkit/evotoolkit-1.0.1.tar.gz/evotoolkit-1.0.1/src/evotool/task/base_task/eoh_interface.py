from abc import ABC, abstractmethod
from typing import List
from .base_evaluator import Solution

from .base_method_interface import BaseMethodInterface
from .base_task_config import BaseTaskConfig


class EohInterface(BaseMethodInterface):
    """Base adapter for EoH (Evolution of Heuristics) algorithm"""
    
    def __init__(self, task_config: BaseTaskConfig):
        super().__init__(task_config)

    def make_init_sol(self) -> Solution:
        init_sol = self.task_config.make_init_sol_wo_other_info()
        other_info = {'algorithm': "None"}
        init_sol.other_info = other_info
        return init_sol
    
    @abstractmethod
    def get_prompt_i1(self) -> List[dict]:
        """Generate initialization prompt (I1 operator)"""
        pass
    
    @abstractmethod
    def get_prompt_e1(self, selected_individuals: List[Solution]) -> List[dict]:
        """Generate E1 (crossover) prompt"""
        pass
    
    @abstractmethod
    def get_prompt_e2(self, selected_individuals: List[Solution]) -> List[dict]:
        """Generate E2 (guided crossover) prompt"""
        pass
    
    @abstractmethod
    def get_prompt_m1(self, individual: Solution) -> List[dict]:
        """Generate M1 (mutation) prompt"""
        pass
    
    @abstractmethod
    def get_prompt_m2(self, individual: Solution) -> List[dict]:
        """Generate M2 (parameter mutation) prompt"""
        pass