import json
import asyncio
from pyston import PystonClient, File
from pyston.models import Output

from app.executors.base import BaseExecutor
from app.models.models import Tests
from app.core.config import settings


class PythonExecutor(BaseExecutor):
    def __init__(self, timeout: int = 2):
        self.timeout = timeout
        self.client = PystonClient(base_url=settings.PISTON_URL)


    async def execute(self, user_code: str, tests: list[Tests], func_name: str | None = None) -> dict:
        for test in tests:
            # Формируем код. Если есть имя функции — вызываем её и ПРИНТУЕМ результат.
            # Если имени функции нет — просто запускаем код как есть.
            full_code = self._prepare_code(user_code, test, func_name)

            output = await self.client.execute("python", [File(f"{full_code}")])
 
            # Проверяем результат
            result = self._verify(output, test)
            if not result["passed"]:
                return {
                    "is_correct": False,
                    "failed_test": result
                }

        return {"is_correct": True} 
    
        
    def _prepare_code(self, user_code: str, test: Tests, func_name: str) -> str:
        if func_name:
            # Сценарий для функций 
            input_data = test.input_data
            return f"""
                {user_code}

                import json
                try:
                    # Вызываем функцию и печатаем её результат в stdout
                    args = json.loads('{input_data}')
                    result = {func_name}(*args)
                    print(json.dumps(result))
                except Exception as e:
                    import sys
                    print(f"Runtime Error: {{e}}", file=sys.stderr)
                    exit(1)
                """
        else:
            # Сценарий для принтов
            return user_code
        
    def normalize_string(self, s: str) -> str:
        if s is None:
            return ""
        # 1. Заменяем Windows-переносы на Linux-переносы
        # 2. Убираем пробелы в начале и конце всей строки
        return s.replace("\r\n", "\n").replace("\r", "\n").strip()
    
    
    def _verify(self, output: Output, test: Tests) -> dict:
        # Убираем лишние пробелы и переносы строк в начале/конце
        got = output.run_stage.stdout.strip()
        expected = test.expected_output_data.strip()

        normalized_got = self.normalize_string(got)
        normalized_expected = self.normalize_string(expected)

        return {
            "passed": normalized_got == normalized_expected,
            "input": output.run_stage.stdrr if output.run_stage.code != 0 else None,
            "expected": expected,
            "got": got
        }
    

    