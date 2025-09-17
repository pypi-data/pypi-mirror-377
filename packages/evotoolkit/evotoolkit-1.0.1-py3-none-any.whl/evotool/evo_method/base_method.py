import os
from abc import abstractmethod, ABC
from typing import List, Type
from evotool.task.base_task import Solution

from .base_config import BaseConfig
from .base_run_state_dict import BaseRunStateDict


class Method(ABC):
    def __init__(self, config:BaseConfig):
        self.config = config
        self.run_state_dict = self._load_run_state_dict()
        self._save_run_state_dict()

    @abstractmethod
    def run(self, *args):
        raise NotImplementedError()

    def verbose_info(self, message:str):
        if self.config.verbose:
            print(message)
    
    def verbose_title(self, text: str, total_width: int = 60):
        """Display a centered title with equal signs above and below"""
        if self.config.verbose:
            print("=" * total_width)
            print(text.center(total_width))
            print("=" * total_width)
    
    def verbose_stage(self, text: str, total_width: int = 60):
        """Display a stage separator with dashes"""
        if self.config.verbose:
            print("-" * total_width)
            print(text.center(total_width))
            print("-" * total_width)

    def verbose_gen(self, text: str, total_width: int = 60):
        """Display text centered with dashes on both sides"""
        if self.config.verbose:
            padding = (total_width - len(text)) // 2
            left_dashes = "-" * padding
            right_dashes = "-" * (total_width - len(text) - padding)
            print(left_dashes + text + right_dashes)

    def _save_run_state_dict(self):
        """Save run state to file"""
        self.run_state_dict.to_json_file(os.path.join(self.config.output_path, "run_state.json"))

    def _load_run_state_dict(self) -> BaseRunStateDict|None:
        """Load run state from file"""
        run_state_class = self._get_run_state_class()
        if os.path.exists(os.path.join(self.config.output_path, "run_state.json")):
            self.verbose_info(f"Loading run state from file {os.path.join(self.config.output_path, 'run_state.json')}")
            return run_state_class.from_json_file(os.path.join(self.config.output_path, "run_state.json"))
        else:
            run_state_dict = run_state_class(self.config.task_info)
            self.verbose_info(f"Initialized run state dict.")
            return run_state_dict

    @staticmethod
    def _get_best_valid_sol(sol_list: List[Solution]):
        valid_sols = []
        for sol in sol_list:
            if sol.evaluation_res is not None:
                if sol.evaluation_res.valid:
                    valid_sols.append(sol)

        # Return the kernel with minimum runtime
        best_kernel = max(valid_sols, key=lambda x: x.evaluation_res.score)
        return best_kernel

    @staticmethod
    def _get_best_sol(sol_list: List[Solution]):
        best_valid_sol = Method._get_best_valid_sol(sol_list)
        if best_valid_sol is not None:
            best_sol = best_valid_sol
        else:
            best_sol = sol_list[0]
        return best_sol

    @abstractmethod
    def _get_run_state_class(self) -> Type[BaseRunStateDict]:
        """Return the algorithm-specific RunStateDict class"""
        pass