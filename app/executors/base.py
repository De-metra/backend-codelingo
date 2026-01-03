from abc import ABC, abstractmethod
from typing import Any


class CodeExecutor(ABC):

    @abstractmethod
    async def execute(
        self, 
        user_code: str,
        tests: list[Any],
    ) -> dict:
        ...