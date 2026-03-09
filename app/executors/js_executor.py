import json
from pyston import PystonClient, File
from pyston.models import Output
from app.executors.base import BaseExecutor
from app.models.models import Tests
from app.core.config import settings

class JavaScriptExecutor(BaseExecutor):
    def __init__(self, timeout: int = 2):
        self.timeout = timeout
        self.client = PystonClient(base_url=settings.PISTON_URL) # Инициализируем клиента Piston

    async def execute(self, user_code: str, tests: list[Tests], func_name: str = None) -> dict:
        for test in tests:
            try:
                # 1. Формируем код для отправки в Piston
                full_code = self._prepare_code(user_code, test, func_name)

                # 2. Выполняем через Piston API
                # "*" заставит Piston выбрать последнюю доступную версию Node.js
                output = await self.client.execute("javascript", [File(f"{full_code}")])
            except Exception as e:
                return {
                    "is_correct": False,
                    "error": "ExecutorError",
                    "details": str(e),
                }

            # 3. Проверяем результат выполнения конкретного теста
            result = self._process_output(output, test, is_function=(func_name is not None))
            
            if not result["passed"]:
                return {
                    "is_correct": False,
                    "failed_test": result,
                }

        return {"is_correct": True}

    def _prepare_code(self, user_code: str, test: Tests, func_name: str) -> str:
        if func_name:
            # Сценарий для ФУНКЦИЙ: оборачиваем в try-catch и вызываем
            return f"""
                {user_code}

                try {{
                    const args = {test.input_data}; // input_data это JSON-строка типа "[1, 2]"
                    if (typeof {func_name} !== 'function') {{
                        throw new Error("Function '{func_name}' is not defined");
                    }}
                    const result = {func_name}(...(Array.isArray(args) ? args : [args]));
                    console.log(JSON.stringify(result));
                }} catch (err) {{
                    console.error(err.message);
                    process.exit(1);
                }}
                """
        else:
            # Сценарий для ПРИНТОВ: просто запускаем код пользователя
            return user_code

    def _process_output(self, output: Output, test: Tests, is_function: bool) -> dict:
        expected_raw = test.expected_output_data.strip()
        stdout = output.run_stage.stdout
        stderr = output.run_stage.stdrr

        # Если код завершился с ошибкой (например, SyntaxError или наш process.exit(1))
        if output.run_stage.code != 0 or stderr:
            return {
                "passed": False,
                "error": "RuntimeError",
                "details": stderr or "Unknown JS error"
            }

        if is_function:
            # Для функций мы сравниваем как объекты (JSON)
            try:
                got_obj = json.loads(stdout)
                expected_obj = json.loads(expected_raw)
                passed = (got_obj == expected_obj)
                got_val = got_obj
            except:
                # Если вдруг в консоль нападало лишнего и JSON не парсится
                passed = (stdout == expected_raw)
                got_val = stdout
        else:
            # Для простых задач на вывод сравниваем просто строки
            passed = (stdout == expected_raw)
            got_val = stdout

        return {
            "passed": passed,
            "input": test.input_data,
            "expected": expected_raw,
            "got": got_val,
        }