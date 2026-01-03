from datetime import datetime, timedelta
from fastapi import HTTPException

from app.core.security import verify_password, get_password_hash, create_jwt_token
from app.models.models import Users, Users_Stats, PasswordResetCode, Users_Levels, Users_Courses
from app.schemas.level import LevelBaseReturn, LevelStatusReturn, LevelReturn, TheoryReturn
from app.schemas.task import TaskBase, TaskAnswer
from app.utils.uow import IUnitOfWork
from app.core.exception import *
from app.executors.python_executor import PythonExexcutor


class TaskService():
    def __init__(self, uow: IUnitOfWork, executor: PythonExexcutor):
        self.uow = uow
        self.executor = executor


    async def get_level_tasks(self, level_id: int):
        async with self.uow:
            level = await self.uow.level.get_by_id(level_id)

            if not level:
                raise LevelNotFoundError()
            
            tasks = await self.uow.task.get_by_level(level_id)

            if not tasks:
                raise TaskNotFoundError()
            
            tasks_data = []
            for t in tasks:
                task_info = {       #ПОД PYDANTIC???/
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
                    task_info["tests"] = [
                        {
                            "id": test.id,
                            "input_data": test.input_data,
                            "expected_output_data": test.expected_output_data,
                            "input_type": test.input_type.name if test.input_type else None,
                            "output_type": test.output_type.name if test.output_type else None,
                        }
                        for test in t.tests
                    ]
                
                tasks_data.append(task_info)

            return {"level_id": level_id, "tasks" : tasks_data}
        

    async def get_task_by_id(self, task_id: int):
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
        

    async def get_task_hint(self, task_id: int):
        async with self.uow:
            hint = await self.uow.task.get_task_hint(task_id=task_id)

            return {"hint": hint}
        

    async def submit_task(self, task_id: int, user_id: int, answer_data: TaskAnswer):
        async with self.uow:
            task = await self.uow.task.get_by_id(task_id)

            if not task:
                raise TaskNotFoundError()
            
            task_type = task.type_rel.name
            # "answers": [1, 3]
            if task_type == "choice":
                options = await self.uow.task.get_task_options_by_id(task_id)

                correct_ids = {o.id for o in options if o.is_correct}
                users_ids = set(answer_data.answers)

                is_correct = users_ids == correct_ids
                return {"is_correct": is_correct, "correct_options": list(correct_ids)}
            # "answers": ["def", "return x + y"]
            elif task_type == "gap":
                gaps = await self.uow.task.get_task_gaps_by_id(task_id)

                correct_answers = [g.answer.strip().lower() for g in gaps]
                user_answers = [a.strip().lower() for a in answer_data.answers]

                is_correct = correct_answers == user_answers
                return {"is_correct": is_correct, "correct_answers": correct_answers}
            # "answers": "def add(x, y):
            #                       return x+y"
            elif task_type == "code":
                tests = await self.uow.task.get_task_tests_by_id(task_id)

                result = await self.executor.execute(
                    user_code=answer_data.answers,
                    tests=tests,
                    func_name=task.func_name
                )
                ##ДОПИСАТЬ -------- МБ ПРОВЕРКА ИИ??
                return result 

