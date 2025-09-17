import re
from abc import ABC, abstractmethod
from typing import List
from evotool.task.base_task import Es1p1Interface, Solution
from .python_task_config import PythonTaskConfig


class Es1P1PythonInterface(Es1p1Interface):
    def __init__(self, task_config: PythonTaskConfig):
        super().__init__(task_config)
    
    def get_prompt(self, best_sol: Solution|None) -> List[dict]:
        task_description = self.task_config.get_base_task_description()

        prompt = f"""
{task_description}

Here is the Python code example you need to optimize:
```python
{best_sol.sol_string}
```

Propose a new Python code which performs better than the above code.

Answer using the following schema:

```python
[Your Python implementation]
```
MAKE SURE THE PROPOSAL CODE IS VALID PYTHON CODE.
FOLLOW EXACTLY THIS FORMAT. DO NOT ADD ANYTHING ELSE.

"""
        prompt_content = [{'role': 'user', 'content': prompt}]
        return prompt_content

    def parse_response(self, response_str: str) -> Solution:
        # Try different code block patterns in order of preference
        patterns = [
            r'```python\s*\n(.*?)\n```',
            r'```Python\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```'  # generic code block
        ]

        # Find all matches using case insensitive search
        for pattern in patterns:
            matches = re.findall(pattern, response_str, re.DOTALL | re.IGNORECASE)
            if matches:
                # Return the longest match (likely the most complete implementation)
                return Solution(max(matches, key=len).strip())
        # Last resort: return stripped response
        return Solution(response_str.strip())