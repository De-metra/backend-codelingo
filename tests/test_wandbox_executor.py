import pytest

from app.executors.wandbox_executor import WandboxExecutor

# @pytest.mark.asyncio
# class TestWanboxExecutor:

#     async def test_executor_simple_func(self):  # false
#         executor = WandboxExecutor()

#         user_code = """
#             def sum_numbers(a, b):
#                 return a+b
#         """

#         tests = [
#             type("Tests", (), {
#                 "input_data": [2, 3],
#                 "expected_output_data": 5
#             })
#         ]

#         result = await executor.execute(user_code, tests, "sum_numbers", "python")
#         assert result["is_correct"] is True