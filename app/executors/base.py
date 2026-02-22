from abc import ABC, abstractmethod
from typing import Any


class BaseExecutor(ABC):

    @abstractmethod
    async def execute(
        self, 
        user_code: str,
        tests: list[Any],
        func_name: str
    ) -> dict:
        ...

class ExecutorRegistry:
    def __init__(self):
        self.executors = {}

    def register(self, language: str, executor: BaseExecutor):
        self.executors[language] = executor

    def get(self, language: str) -> BaseExecutor|None:
        return self.executors.get(language)
    
