import re
from evotool.task.base_task import Es1p1Interface, Solution, EvaluationResult
from  typing import List

from .cuda_task_config import CudaTaskConfig


class Es1P1CudaInterface(Es1p1Interface):
    def __init__(self, task_config: CudaTaskConfig):
        super().__init__(task_config)

    def get_prompt(self, best_sol:Solution) -> List[dict]:
        prompt = f"""
{self.task_config.get_base_task_description()}

Here is the CUDA kernel code example you need to optimize:
```cpp
{best_sol.sol_string}
```

Propose a new CUDA kernel code which aims to reduce the runtime of the operation, while ensuring the kernel returns the correct result.

Answer using the following schema:

```cpp
[Your kernel implementation]
```

The pybind11 cuda module name has to be the same as in the example.
MAKE SURE THE PROPOSAL CODE IS VALID CUDA CODE.
FOLLOW EXACTLY THIS FORMAT. DO NOT ADD ANYTHING ELSE.

"""
        prompt_content = [{'role': 'user', 'content': prompt}]
        return prompt_content

    def parse_response(self, response_str: str) -> Solution:
        # Try different code block patterns in order of preference
        patterns = [
            r'```cpp\s*\n(.*?)\n```',      # cpp
            r'```c\+\+\s*\n(.*?)\n```',    # c++
            r'```cuda\s*\n(.*?)\n```',     # cuda
            r'```c\s*\n(.*?)\n```',        # c
            r'```\s*\n(.*?)\n```'          # generic code block
        ]
        
        # Find all matches using case insensitive search
        for pattern in patterns:
            matches = re.findall(pattern, response_str, re.DOTALL | re.IGNORECASE)
            if matches:
                # Return the longest match (likely the most complete implementation)
                return Solution(max(matches, key=len).strip())
        # Last resort: return stripped response
        return Solution(response_str.strip())

