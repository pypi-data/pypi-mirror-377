import re
from evotool.task.base_task import EvoEngineerInterface, Solution, Operator
from typing import List
from .cuda_task_config import CudaTaskConfig




class EvoEngineerCudaInterface(EvoEngineerInterface):
    def __init__(self, task_config: CudaTaskConfig):
        super().__init__(task_config)

    def get_init_operators(self) -> List[Operator]:
        """Get initialization operators for CUDA optimization"""
        return [
            Operator("init", 0)
        ]
    
    def get_offspring_operators(self) -> List[Operator]:
        """Get offspring operators for CUDA optimization"""
        return [
            Operator("crossover", 2),
            Operator("mutation", 1)
        ]

    def get_operator_prompt(self, operator_name: str, selected_individuals: List[Solution], current_best_sol: Solution, random_thoughts: List[str], **kwargs) -> List[dict]:
        """Generate prompt for any operator"""
        task_description = self.task_config.get_base_task_description()

        if current_best_sol is None:
            current_best_sol = self.make_init_sol()
        
        if operator_name == "init":
            # Build the thoughts section if available
            thoughts_section = ""
            if random_thoughts and len(random_thoughts) > 0:
                thoughts_list = "\n".join([f"- {thought}" for thought in random_thoughts])
                thoughts_section = f"""

Reference insights (consider if relevant):
{thoughts_list}

"""
            
            prompt = f"""
{task_description}

Here is the CUDA kernel code you need to optimize:

<current_kernel>
<name>{current_best_sol.other_info['name']}</name>
<thought>{current_best_sol.other_info['thought']}</thought>
<code>
```c++
{current_best_sol.sol_string}
```
</code>
<runtime>{-current_best_sol.evaluation_res.score:.5f} milliseconds</runtime>
<profile_info>
{current_best_sol.evaluation_res.additional_info['prof_string']}
</profile_info>
</current_kernel>{thoughts_section}

Think deeply about how to optimize this CUDA kernel. {'Reference insights are provided above - use them as inspiration if they seem relevant to your optimization approach.' if random_thoughts and len(random_thoughts) > 0 else ''} Propose a new CUDA kernel that:
1. Analyzes the current implementation to identify optimization opportunities
2. Applies proven CUDA optimization techniques based on your analysis
3. Explains your optimization rationale and approach clearly

The new kernel should aim to reduce the runtime of the operation while ensuring it returns the correct result.
The PYBIND11_MODULE has to be the same as in the example.
MAKE SURE THE PROPOSAL CODE IS VALID CUDA CODE.
FOLLOW EXACTLY THIS FORMAT. DO NOT ADD ANYTHING ELSE.

RESPONSE FORMAT - Follow this EXACT structure (order matters):

name: [lowercase_descriptor_with_underscores]

code:
```cpp
[Your complete CUDA kernel implementation here]
```

thought: [Your detailed optimization rationale and approach]

CRITICAL REQUIREMENTS:
1. Keep this exact order: name, then code, then thought
2. The 'name:' line must be a single line with no extra text
3. The code MUST be wrapped in ```cpp and ``` markers
4. Include the complete CUDA implementation with all headers
5. End with your optimization explanation after 'thought:'
6. Do not add any extra text outside this structure

"""
            return [{'role': 'user', 'content': prompt}]

        elif operator_name == "crossover":
            # Build the thoughts section if available
            thoughts_section = ""
            if random_thoughts and len(random_thoughts) > 0:
                thoughts_list = "\n".join([f"- {thought}" for thought in random_thoughts])
                thoughts_section = f"""

Reference insights (consider if relevant):
{thoughts_list}

"""
            
            # Build XML-structured individuals
            indivs_xml = ""
            for i, indi in enumerate(selected_individuals):
                name = indi.other_info.get('name', f"kernel_{i+1}")
                runtime = -indi.evaluation_res.score
                thought = indi.other_info.get('thought', 'No thought provided')
                
                indivs_xml += f"""
<kernel_{i+1}>
<name>{name}</name>
<thought>{thought}</thought>
<code>
```c++
{indi.sol_string}
```
</code>
<runtime>{runtime:.5f} milliseconds</runtime>
</kernel_{i+1}>"""
            
            prompt = f"""
{task_description}

Here is the current best CUDA kernel to optimize:

<current_kernel>
<name>{current_best_sol.other_info.get('name', 'current_best')}</name>
<thought>{current_best_sol.other_info.get('thought', 'Current best implementation')}</thought>
<code>
```c++
{current_best_sol.sol_string}
```
</code>
<runtime>{-current_best_sol.evaluation_res.score:.5f} milliseconds</runtime>
<profile_info>
{current_best_sol.evaluation_res.additional_info['prof_string']}
</profile_info>
</current_kernel>

I have {len(selected_individuals)} other kernel implementations to learn from:
{indivs_xml}{thoughts_section}

Analyze the current best kernel and these alternative implementations, then think deeply about how to combine their best ideas. {'Reference insights are provided above - use them as inspiration if they seem relevant to your crossover approach.' if random_thoughts and len(random_thoughts) > 0 else ''} Propose a new CUDA kernel that:
1. Analyzes the different optimization approaches from the existing implementations
2. Combines the most effective ideas and techniques from multiple kernels
3. Explains your crossover rationale and which implementation ideas you merged

The new kernel should aim to reduce the runtime by combining ideas from the existing implementations while ensuring it returns the correct result.
The PYBIND11_MODULE has to be the same as in the example.
MAKE SURE THE PROPOSAL CODE IS VALID CUDA CODE.
FOLLOW EXACTLY THIS FORMAT. DO NOT ADD ANYTHING ELSE.

RESPONSE FORMAT - Follow this EXACT structure (order matters):

name: [lowercase_descriptor_with_underscores]

code:
```cpp
[Your complete CUDA kernel implementation here]
```

thought: [Your detailed optimization rationale and approach]

CRITICAL REQUIREMENTS:
1. Keep this exact order: name, then code, then thought
2. The 'name:' line must be a single line with no extra text
3. The code MUST be wrapped in ```cpp and ``` markers
4. Include the complete CUDA implementation with all headers
5. End with your optimization explanation after 'thought:'
6. Do not add any extra text outside this structure

"""
            return [{'role': 'user', 'content': prompt}]
        elif operator_name == "mutation":
            individual = selected_individuals[0]
            
            # Build the thoughts section if available
            thoughts_section = ""
            if random_thoughts and len(random_thoughts) > 0:
                thoughts_list = "\n".join([f"- {thought}" for thought in random_thoughts])
                thoughts_section = f"""

Reference insights (consider if relevant):
{thoughts_list}

"""
            
            name = individual.other_info.get('name', 'mutation_base')
            runtime = -individual.evaluation_res.score
            thought = individual.other_info.get('thought', 'No thought provided')
            
            prompt = f"""
{task_description}

Here is the current best CUDA kernel for reference:

<current_best>
<name>{current_best_sol.other_info.get('name', 'current_best')}</name>
<thought>{current_best_sol.other_info.get('thought', 'Current best implementation')}</thought>
<code>
```c++
{current_best_sol.sol_string}
```
</code>
<runtime>{-current_best_sol.evaluation_res.score:.5f} milliseconds</runtime>
<profile_info>
{current_best_sol.evaluation_res.additional_info['prof_string']}
</profile_info>
</current_best>

Here is the kernel implementation to mutate:

<source_kernel>
<name>{name}</name>
<thought>{thought}</thought>
<code>
```c++
{individual.sol_string}
```
</code>
<runtime>{runtime:.5f} milliseconds</runtime>
</source_kernel>{thoughts_section}

Think creatively about how to fundamentally reimagine this kernel, using the current best as your correctness reference. {'Reference insights are provided above - use them as inspiration if they seem relevant to your mutation approach.' if random_thoughts and len(random_thoughts) > 0 else ''} Propose a deeply mutated CUDA kernel that:
1. Explores radical changes in algorithmic approach, memory access patterns, or parallelization strategy
2. May completely restructure the computation while maintaining functional correctness against the current best
3. Explains your bold mutation concept and the reasoning behind this fundamental transformation

The mutated kernel should have a different form but maintain the same functionality while aiming for better runtime performance than the current best.
The PYBIND11_MODULE has to be the same as in the example.
MAKE SURE THE PROPOSAL CODE IS VALID CUDA CODE.
FOLLOW EXACTLY THIS FORMAT. DO NOT ADD ANYTHING ELSE.

RESPONSE FORMAT - Follow this EXACT structure (order matters):

name: [lowercase_descriptor_with_underscores]

code:
```cpp
[Your complete CUDA kernel implementation here]
```

thought: [Your detailed optimization rationale and approach]

CRITICAL REQUIREMENTS:
1. Keep this exact order: name, then code, then thought
2. The 'name:' line must be a single line with no extra text
3. The code MUST be wrapped in ```cpp and ``` markers
4. Include the complete CUDA implementation with all headers
5. End with your optimization explanation after 'thought:'
6. Do not add any extra text outside this structure

"""
            return [{'role': 'user', 'content': prompt}]
        else:
            raise ValueError(f"Unknown operator: {operator_name}")

    def parse_response(self, response_str: str) -> Solution:
        """Improved parser with multiple fallback strategies"""
        if not response_str or not response_str.strip():
            return Solution("")

        content = response_str.strip()

        # Strategy 1: Standard format parsing (most reliable)
        result = self._parse_standard_format(content)
        if result and result[1]:  # Ensure we have code
            return Solution(result[1], other_info={"name": result[0], "thought": result[2]})

        # Strategy 2: Flexible format parsing
        result = self._parse_flexible_format(content)
        if result and result[1]:
            return Solution(result[1], other_info={"name": result[0], "thought": result[2]})

        # Strategy 3: Code block fallback
        code = self._extract_any_code_block(content)
        if code:
            return Solution(code, other_info={"name": "extracted", "thought": "Fallback parsing"})

        # Strategy 4: Raw content (last resort)
        return Solution(content, other_info={"name": "raw", "thought": "Failed to parse"})

    def _parse_standard_format(self, content: str) -> tuple:
        """Parse standard format: name -> code -> thought order"""
        # Extract name (independent pattern)
        name_pattern = r'^name:\s*([^\n\r]+?)(?:\n|\r|$)'
        name_match = re.search(name_pattern, content, re.MULTILINE | re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else ""

        # Extract code block (independent pattern)
        code_pattern = r'code:\s*\n*```(?:cpp|c\+\+|cuda)?\n(.*?)```'
        code_match = re.search(code_pattern, content, re.DOTALL | re.IGNORECASE)
        code = code_match.group(1).strip() if code_match else ""

        # Extract thought (independent pattern)
        thought_pattern = r'thought:\s*(.*?)$'
        thought_match = re.search(thought_pattern, content, re.DOTALL | re.IGNORECASE)
        thought = thought_match.group(1).strip() if thought_match else ""

        return (name, code, thought)

    def _parse_flexible_format(self, content: str) -> tuple:
        """More flexible parsing for variations in format"""
        # Try to extract name anywhere in the text
        name_pattern = r'(?:name|Name|NAME)\s*:?\s*([^\n\r]+)'
        name_match = re.search(name_pattern, content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else ""

        # Try to extract any code block
        code = self._extract_any_code_block(content)

        # Try to extract thought
        thought_pattern = r'(?:thought|Thought|THOUGHT)\s*:?\s*(.*?)(?=\n(?:name|code)|$)'
        thought_match = re.search(thought_pattern, content, re.DOTALL | re.IGNORECASE)
        thought = thought_match.group(1).strip() if thought_match else ""

        return (name, code, thought)

    def _extract_any_code_block(self, content: str) -> str:
        """Extract any code block from the content"""
        # Priority 1: Look for ```cpp or ```c++ blocks
        cpp_pattern = r'```(?:cpp|c\+\+|cuda)\n(.*?)```'
        match = re.search(cpp_pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Priority 2: Look for any ``` blocks
        generic_pattern = r'```[^\n]*\n(.*?)```'
        match = re.search(generic_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Priority 3: Look for code: section without proper markers
        code_pattern = r'code:\s*\n*(.*?)(?=\n(?:thought|$))'
        match = re.search(code_pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            code_content = match.group(1).strip()
            # Remove any remaining ``` markers
            code_content = re.sub(r'^```[^\n]*\n?', '', code_content)
            code_content = re.sub(r'\n?```\s*$', '', code_content)
            return code_content.strip()

        return ""

