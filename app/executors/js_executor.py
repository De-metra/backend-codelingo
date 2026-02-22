import asyncio
import json
import tempfile
import os
import subprocess
from app.executors.base import BaseExecutor
from app.models.models import Tests


class JavaScriptExecutor(BaseExecutor):
    def __init__(self, timeout: int = 2):
        self.timeout = timeout

    async def execute(self, user_code: str, tests: list[Tests], func_name: str) -> dict:
        try:
            js_file_path = self._prepare_js_file(user_code, func_name)
        except Exception as e:
            return {
                "is_correct": False,
                "error": "CompileError",
                "details": str(e),
            }

        for test in tests:
            try:
                result = await self._run_single_test(js_file_path, test, func_name)
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

    def _prepare_js_file(self, user_code: str, func_name: str) -> str:
        wrapper = f"""
            {user_code}

            try {{
                const input = JSON.parse(process.argv[2]);

                if (typeof {func_name} !== "function") {{
                    throw new Error("Function '{func_name}' not found");
                }}

                const result = {func_name}(...input);
                console.log(JSON.stringify(result));
            }} catch (err) {{
                console.error(err.toString());
                process.exit(1);
            }}
            """
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".js")
        tmp_file.write(wrapper.encode())
        tmp_file.close()
        return tmp_file.name


    async def _run_single_test(self, js_file_path: str, test: Tests, func_name: str) -> dict:
        input_args = json.loads(test.input_data)
        expected = json.loads(test.expected_output_data)

        if not isinstance(input_args, list):
            input_args = [input_args]

        process = await asyncio.create_subprocess_exec(
            "node",
            js_file_path,
            json.dumps(input_args),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            return {
                "passed": False,
                "error": "Timeout"
            }

        if process.returncode != 0:
            return {
                "passed": False,
                "error": "RuntimeError",
                "details": stderr.decode() or "JS process crashed"
            }

        try:
            result = json.loads(stdout.decode())
        except Exception as e:
            return {
                "passed": False,
                "error": "RuntimeError",
                "details": f"Invalid JSON output: {stdout.decode()}"
            }

        return {
            "passed": result == expected,
            "input": input_args,
            "expected": expected,
            "got": result,
        }

