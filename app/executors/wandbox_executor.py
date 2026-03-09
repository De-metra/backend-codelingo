import httpx

from app.core.config import settings
from app.models.models import Tests


class WandboxExecutor:
    def __init__(self):
        self.api_url = settings.WANDBOX_URL
        self.timeout = httpx.Timeout(25.0, connect=5.0)

        self.compilers = {
            "python": "cpython-3.11.10",
            "javascript": "nodejs-20.17.0"
        }
 

    def _normalize(self, text: str) -> str:
        """Убираем \r и лишние пробелы по краям"""
        if not text:
            return ""
        return text.replace("\r\n", "\n").replace("\r", "\n").strip()      


    def _prepare_full_code(self, user_code: str, test_input: str, func_name: str, language: str) -> str:
        if func_name:
            if language == "python":
                # Для Python оборачиваем в print()
                return f"{user_code}\n\nprint({func_name}(*{test_input}))"
            
            elif language == "javascript":
                # Для JS оборачиваем в console.log()
                return f"{user_code}\n\nconsole.log({func_name}(...{test_input}));"
        
        # Если это просто скрипт (пользователь сам должен написать print)
        return user_code


    async def execute(self, user_code: str, tests: list[Tests], func_name: str, language: str) -> dict:
        compiler = self.compilers.get(language)
        if not compiler:
            return {"error": f"Language {language} not supported"}
        
        async with httpx.AsyncClient() as client:
            for test in tests:
                try:
                    full_code = self._prepare_full_code(
                        user_code=user_code,
                        test_input=test.input_data, 
                        func_name=func_name,
                        language=language
                    )

                    payload = {
                        "compiler": compiler,
                        "code": full_code,
                        "save": False  # Не сохранять код в постоянное хранилище Wandbox
                    }

                    response = await client.post(self.api_url, json=payload, timeout=self.timeout)
                    response.raise_for_status()
                    data = response.json()

                    status = data.get("status")
                    stdout = self._normalize(data.get("program_output", ""))
                    stderr = self._normalize(data.get("program_error", ""))
                    expected = self._normalize(test.expected_output_data)

                    if status != "0" and stderr:
                        return {"is_correct": False, "error": stderr}

                    if stdout != expected:
                        return {
                            "is_correct": False, 
                            "failed_test": {
                                "input": test.input_data,
                                "expected": expected,
                                "got": stdout
                            }
                        }

                except Exception as e:
                    return {"is_correct": False, "error": f"Wandbox API error: {str(e)}"}

            return {"is_correct": True}