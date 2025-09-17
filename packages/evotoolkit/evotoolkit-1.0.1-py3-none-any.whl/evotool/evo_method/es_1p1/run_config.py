from evotool.tools.llm import HttpsApi
from evotool.task.base_task import BaseEvaluator, Es1p1Interface
from ..base_config import BaseConfig
from typing import List, Optional

class Es1p1Config(BaseConfig):
    def __init__(
            self,
            task_info: dict,
            output_path: str,
            running_llm: HttpsApi,
            evaluator: BaseEvaluator,
            interface: Es1p1Interface,
            max_sample_nums: int = 45,
            num_samplers: int = 5,
            num_evaluators: int = 5,
            verbose: bool = True
    ):
        super().__init__(task_info, output_path, verbose)
        self.evaluator = evaluator
        self.running_llm = running_llm
        self.interface = interface
        self.max_sample_nums = max_sample_nums
        self.num_samplers = num_samplers
        self.num_evaluators = num_evaluators