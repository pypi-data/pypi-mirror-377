from evotool.task.base_task import Solution, BaseTaskConfig, EvaluationResult


class CudaTaskConfig(BaseTaskConfig):
    """Cuda Adapter"""
    def __init__(self, task_info: dict):
        super().__init__(task_info)

    def get_base_task_description(self) -> str:
        """Get the base task description using task info"""
        gpu_type = self.task_info.get("gpu_type", "RTX 4090")
        cuda_version = self.task_info.get("cuda_version", "12.4.1")
        return f"""You are a Machine Learning Engineer trying to reduce the runtime of a CUDA kernel. Make sure the kernel returns the correct result. Do not use any alternative precision that could result in an incorrect result. The kernel will be run on a {gpu_type} GPU with CUDA {cuda_version}.
"""

    def make_init_sol_wo_other_info(self) -> Solution:
        init_sol = Solution(self.task_info["cuda_code"])
        evaluation_res = EvaluationResult(
            valid=True,
            score=-self.task_info["cuda_info"]["runtime"],
            additional_info={
                    "code": self.task_info['cuda_code'],
                    "temp_str": None,
                    "runtime": self.task_info["cuda_info"]["runtime"],
                    "prof_string": self.task_info["cuda_info"]["prof_string"],
                    "compilation_error": False,
                    "comparison_error": False,
                    "error_msg": None,
                    "exception": None
            }
        )
        init_sol.evaluation_res = evaluation_res
        return init_sol