from typing import Any, Dict

from app.models.models import Tasks
from app.schemas.task import TaskBase, TaskAnswer
from app.utils.uow import IUnitOfWork
from app.core.exception import LevelNotFoundError, TaskNotFoundError
from app.executors.base import ExecutorRegistry


class TaskService():
    def __init__(self, uow: IUnitOfWork, executor_registry: ExecutorRegistry):
        self.uow = uow
        self.executor_registry = executor_registry


    async def get_level_tasks(self, level_id: int) -> Dict[str, Any]:
        async with self.uow:
            level = await self.uow.level.get_by_id(level_id)
            if not level:
                raise LevelNotFoundError()
            
            tasks = await self.uow.task.get_by_level(level_id)
            if not tasks:
                raise TaskNotFoundError()
            
            tasks_data = []
            for t in tasks:
                task_info = {       # ПОД PYDANTIC???
                    "task_id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "task_type": t.type_rel.name
                }

                t_type = t.type_rel.name
                if t_type == 'choice':
                    task_info["options"] = [
                        {
                            "id": o.id,
                            "text": o.text,
                            "is_correct": o.is_correct
                        }
                        for o in t.options
                    ]
                elif t_type == 'gap':
                    task_info["gaps"] = [
                        {
                            "template": g.template,
                            "answer": g.answer
                        }
                        for g in t.gaps
                    ]
                elif t_type == 'code':
                    task_info["code"] = [
                        {
                            "id": c.id,
                            "func_name": c.func_name,
                            "template": c.template,
                            "language": c.language
                        }
                        for c in t.code
                    ]
                tasks_data.append(task_info)

            return {"level_id": level_id, "tasks": tasks_data}
        

    async def get_task_by_id(self, task_id: int) -> TaskBase:
        async with self.uow:
            task = await self.uow.task.get_by_id(task_id)

            if not task: 
                raise TaskNotFoundError()
            
            return TaskBase(
                id=task_id,
                title=task.title,
                description=task.description,
                task_type=task.type_rel.name,
                hint=task.hint                  #нужно ли отдавать hint
            )
        

    async def get_task_hint(self, task_id: int) -> Dict[str, Any]:
        async with self.uow:
            hint = await self.uow.task.get_task_hint(task_id=task_id)

            return {"hint": hint}
        

    async def submit_task(self, task_id: int, user_id: int, answer_data: TaskAnswer):
        async with self.uow:
            task = await self.uow.task.get_by_id(task_id)
            if not task:
                raise TaskNotFoundError()
            
            
            return await self._verify_answer(task, answer_data)


    async def _verify_answer(self, task: Tasks, answer_data: TaskAnswer) -> Dict[str, Any]:
        task_type = task.type_rel.name

            # "answers": [1, 3]
        if task_type == "choice":
            options = await self.uow.task.get_task_options_by_id(task.id)

            correct_ids = {o.id for o in options if o.is_correct}
            users_ids = set(answer_data.answers)

            is_correct = users_ids == correct_ids
            return {"is_correct": is_correct, "correct_options": list(correct_ids)}
        
        # "answers": ["def", "return x + y"]
        elif task_type == "gap":
            gaps = await self.uow.task.get_task_gaps_by_id(task.id)

            correct_answers = [g.answer.strip().lower() for g in gaps]
            user_answers = [a.strip().lower() for a in answer_data.answers]

            is_correct = correct_answers == user_answers
            return {"is_correct": is_correct, "correct_answers": correct_answers}
        
        # "answers": "def add(x, y):
        #                       return x+y"
        #              {
        #     "answers": "function sum(a,b,c) {\n    return a+b+c\n}"
        # } 
        elif task_type == "code":
            code_data = await self.uow.task.get_task_code_by_id(task.id)
            tests = await self.uow.task.get_task_tests_by_code_id(code_data.id)

            executor = self.executor_registry.get(code_data.language.language)

            return await executor.execute(
                user_code=answer_data.answers,
                language=code_data.language.language,
                func_name=code_data.func_name,
                tests=tests
            )

