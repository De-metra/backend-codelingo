import asyncio
import json
import traceback
from types import MappingProxyType

from app.models.models import Tests


class PythonExexcutor:
    def __init__(self, timeout: int = 2):
        self.timeout = timeout

    async def execute(self, user_code: str, tests: list[Tests], func_name: str) -> dict:
        try:
            compiled_code = self._compile_user_code(user_code, func_name)
        except Exception as e:
            return {
                "is_correct": False,
                "error": "SyntaxError",
                "details": str(e),
            }
        
        for test in tests:
            try:
                result = await self._run_single_test(compiled_code, test)
            except Exception as e:
                return {
                    "is_correct": False,
                    "error": "RuntimeError",
                    "details": str(e),
                }

            if not result["passed"]:
                return {
                    "is_correct": False,
                    "failed_test": result,
                }

        return {"is_correct": True}



    def _compile_user_code(seld, code: str, func_name: str):
        safe_globals = {
            "__builtins__": MappingProxyType({
                "range": range,
                "len": len,
                "print": print,
                "int": int,
                "str": str,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "set": set,
                "sum": sum,
                "min": min,
                "max": max,
            })
        }

        local_env = {}

        exec(code, safe_globals, local_env)

        if func_name not in local_env:
            raise ValueError(f"Функция {func_name} не найдена")
        
        function = local_env[func_name]

        if not callable(function):
            raise ValueError(f"'{func_name}' не является функцией")

        return function
    
    
    async def _run_single_test(self, solution, test: Tests) -> dict:
        input_args = json.loads(test.input_data)
        expected = json.loads(test.expected_output_data)

        if not isinstance(input_args, list):
            input_args = [input_args]

        try:
            result = await asyncio.wait_for(
                self._call_solution(solution, input_args),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            return {
                "passed": False,
                "error": "Timeout"
            }
        
        return {
            "passed": result == expected,
            "input": input_args,
            "expected": expected,
            "got": result,
        }


    async def _call_solution(self, solution, args):
        """
        Асинхронный вызов пользовательской функции
        """
        return solution(*args)