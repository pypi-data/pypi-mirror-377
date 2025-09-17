import os
import json
from ..base_run_state_dict import BaseRunStateDict
from evotool.task.base_task import Solution

class FunSearchRunStateDict(BaseRunStateDict):
    def __init__(
            self,
            task_info: dict,
            tot_sample_nums: int = 0,
            sol_history: list[Solution] = None,
            database_file: str = None,
            is_done: bool = False
    ):
        super().__init__(task_info)
        
        self.tot_sample_nums = tot_sample_nums
        self.sol_history = sol_history or []  # All solutions (valid/invalid)
        self.database_file = database_file  # Path to database JSON file
        self.is_done = is_done
        self.usage_history = {}
        
    def to_json(self) -> dict:
        """Convert the run state to JSON-serializable dictionary"""
        # Convert Solution objects to dictionaries
        sol_history_json = []
        for sol in self.sol_history:
            sol_dict = {
                'sol_string': sol.sol_string,
                'other_info': sol.other_info,
                'evaluation_res': None
            }
            if sol.evaluation_res:
                sol_dict['evaluation_res'] = {
                    'valid': sol.evaluation_res.valid,
                    'score': sol.evaluation_res.score,
                    'additional_info': sol.evaluation_res.additional_info
                }
            sol_history_json.append(sol_dict)
        
        return {
            'task_info': self.task_info,
            'sol_history': sol_history_json,
            'database_file': self.database_file,
            'tot_sample_nums': self.tot_sample_nums,
            'is_done': self.is_done,
            'usage_history': self.usage_history
        }
        
    @classmethod
    def from_json(cls, data: dict) -> 'FunSearchRunStateDict':
        """Create instance from JSON data"""
        from evotool.task.base_task import Solution, EvaluationResult
        
        # Convert sol_history from dictionaries back to Solution objects
        sol_history = []
        for sol_dict in data.get('sol_history', []):
            evaluation_res = None
            if sol_dict.get('evaluation_res'):
                eval_data = sol_dict['evaluation_res']
                evaluation_res = EvaluationResult(
                    valid=eval_data['valid'],
                    score=eval_data['score'],
                    additional_info=eval_data['additional_info']
                )
            
            solution = Solution(
                sol_string=sol_dict['sol_string'],
                other_info=sol_dict.get('other_info'),
                evaluation_res=evaluation_res
            )
            sol_history.append(solution)
        
        instance = cls(
            task_info=data['task_info'],
            tot_sample_nums=data.get('tot_sample_nums', 0),
            sol_history=sol_history,
            database_file=data.get('database_file'),
            is_done=data.get('is_done', False),
        )
        instance.usage_history = data.get('usage_history', {})
        return instance
    
    def save_database_state(self, database_dict: dict, output_path: str) -> None:
        """Save database state to a separate JSON file"""
        if not self.database_file:
            # Generate database filename based on output path
            self.database_file = os.path.join(output_path, "programs_database.json")
        
        database_path = self.database_file
        if not os.path.isabs(database_path):
            database_path = os.path.join(output_path, database_path)
        
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(database_dict, f, indent=2, ensure_ascii=False)
    
    def load_database_state(self, output_path: str) -> dict:
        """Load database state from the separate JSON file"""
        if not self.database_file:
            return {}
        
        database_path = self.database_file
        if not os.path.isabs(database_path):
            database_path = os.path.join(output_path, database_path)
        
        if not os.path.exists(database_path):
            return {}
        
        try:
            with open(database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load database state from {database_path}: {e}")
            return {}
    
    def has_database_state(self, output_path: str) -> bool:
        """Check if database state file exists"""
        if not self.database_file:
            return False
        
        database_path = self.database_file
        if not os.path.isabs(database_path):
            database_path = os.path.join(output_path, database_path)
        
        return os.path.exists(database_path)