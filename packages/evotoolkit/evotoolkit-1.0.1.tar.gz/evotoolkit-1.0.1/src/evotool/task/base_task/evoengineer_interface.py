from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .base_evaluator import Solution
from .base_method_interface import BaseMethodInterface
from .base_task_config import BaseTaskConfig


class Operator:
    """Simple operator class with name and selection size"""
    
    def __init__(self, name: str, selection_size: int = 0):
        self.name = name
        self.selection_size = selection_size


class EvoEngineerInterface(BaseMethodInterface):
    """Base adapter for EvoEngineer algorithm"""

    def __init__(self, task_config: BaseTaskConfig):
        super().__init__(task_config)

    def make_init_sol(self) -> Solution:
        other_info = {'name': "Baseline", "thought": "Baseline"}
        init_sol = self.task_config.make_init_sol_wo_other_info()
        init_sol.other_info = other_info
        return init_sol
    
    @abstractmethod
    def get_init_operators(self) -> List[Operator]:
        """Get initialization operators for this task (should have selection_size=0)"""
        pass
    
    @abstractmethod
    def get_offspring_operators(self) -> List[Operator]:
        """Get offspring operators for this task"""
        pass
    
    @abstractmethod
    def get_operator_prompt(self, operator_name: str, selected_individuals: List[Solution], current_best_sol: Solution, random_thoughts: List[str], **kwargs) -> List[dict]:
        """Generate prompt for any operator
        
        Args:
            operator_name: Name of the operator 
            selected_individuals: Selected individuals for the operator
            **kwargs: Additional operator-specific parameters
            :param current_best_sol:
        """
        pass