from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy import ForeignKey, String, DateTime, Boolean, text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.db import Base, int_pk, str_null_true


class PasswordResetCode(Base):
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["Users"] = relationship("Users")

class Achievments(Base):
    id: Mapped[int_pk]
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str_null_true]
    icon: Mapped[str_null_true]

    user_achievments: Mapped[list["Users_Achievments"]] = relationship(
        back_populates="achievment",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    
    def __str__(self):
        return self.title 

class Courses(Base):
    id: Mapped[int_pk]
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str_null_true]

    levels: Mapped[list["Levels"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    user_courses: Mapped[list["Users_Courses"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __str__(self):
        return f"{self.title}"

class Users(Base):
    
    id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    picture_link: Mapped[str_null_true]
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    stats: Mapped["Users_Stats"] = relationship(
        "Users_Stats", 
        back_populates="user", 
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False
    )

    levels: Mapped[list["Users_Levels"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    courses: Mapped[list["Users_Courses"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    achievments: Mapped[list["Users_Achievments"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __str__(self):
        return self.username

class Users_Stats(Base):

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None, nullable=True)
    streak: Mapped[int] = mapped_column(server_default=text('0'))
    total_xp: Mapped[int] = mapped_column(server_default=text('0'))

    user: Mapped["Users"] = relationship("Users", back_populates="stats")

class Users_Achievments(Base):

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievment_id: Mapped[int] = mapped_column(ForeignKey("achievments.id", ondelete="CASCADE"), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="achievments")
    achievment: Mapped["Achievments"] = relationship("Achievments", back_populates="user_achievments")

class Users_Courses(Base):

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    progress: Mapped[int] = mapped_column(server_default=text('0'))
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, server_default='f')
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["Users"] = relationship("Users", back_populates="courses")
    course: Mapped["Courses"] = relationship("Courses", back_populates="user_courses")


class Users_Levels(Base):
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id", ondelete="CASCADE"), nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, server_default='f')

    user: Mapped["Users"] = relationship("Users", back_populates="levels")
    level: Mapped["Levels"] = relationship("Levels", back_populates="user_levels")

class Levels(Base):
    id: Mapped[int_pk]
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str_null_true]
    theory_id: Mapped[int] = mapped_column(ForeignKey("theories.id", ondelete="CASCADE"), nullable=False)
    xp: Mapped[int]
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)

    theory: Mapped["Theories"] = relationship("Theories", back_populates="levels")
    tasks: Mapped[list["Level_Tasks"]] = relationship(
        back_populates="level",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    user_levels: Mapped[list["Users_Levels"]] = relationship(
        back_populates="level",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    course: Mapped["Courses"] = relationship("Courses", back_populates="levels")
    
    def __str__(self):
        return self.title 

class Theories(Base):
    id: Mapped[int_pk]
    description: Mapped[str] = mapped_column(String, nullable=False)

    levels: Mapped[list["Levels"]] = relationship(
        back_populates="theory",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    
    def __str__(self):
        return self.description[:50]  # или title, если появится

class Level_Tasks(Base):
    id: Mapped[int_pk]
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    num_in_order: Mapped[int]

    level: Mapped["Levels"] = relationship("Levels", back_populates="tasks")
    task: Mapped["Tasks"] = relationship("Tasks", back_populates="tasks_link")

    def __str__(self):
        return f"{self.level_id} — Task {self.task_id} (#{self.num_in_order})"

class Tasks(Base):
    id: Mapped[int_pk]
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    task_type: Mapped[int] = mapped_column(ForeignKey("tasks_types.id", ondelete="SET NULL"), nullable=False)
    hint: Mapped[str_null_true]

    template: Mapped[str_null_true]
    func_name: Mapped[str_null_true]

    tasks_link: Mapped[list["Level_Tasks"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    type_rel: Mapped["Tasks_Types"] = relationship("Tasks_Types", back_populates="tasks")
    tests: Mapped[list["Tests"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    options: Mapped[list["Tasks_Options"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    gaps: Mapped[list["Tasks_Gap"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True
        )
    
    def __str__(self):
        return self.description[:50]


class Tasks_Types(Base):
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String, nullable=False)

    tasks: Mapped[list["Tasks"]] = relationship(
        back_populates="type_rel"
        )
    
    def __str__(self):
        return self.name

class Tests(Base):
    id: Mapped[int_pk]
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    input_type_id: Mapped[int] = mapped_column(ForeignKey("data_types.id", ondelete="SET NULL"), nullable=True)
    output_type_id: Mapped[int] = mapped_column(ForeignKey("data_types.id", ondelete="SET NULL"), nullable=True)
    input_data: Mapped[str_null_true]
    expected_output_data: Mapped[str_null_true]

    task: Mapped["Tasks"] = relationship("Tasks", back_populates="tests")
    input_type: Mapped["Data_Types"] = relationship("Data_Types", foreign_keys=[input_type_id])
    output_type: Mapped["Data_Types"] = relationship("Data_Types", foreign_keys=[output_type_id])

class Data_Types(Base):
    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String, nullable=False)

    def __str__(self):
        return self.name

class Tasks_Options(Base):
    id: Mapped[int_pk]
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    is_correct: Mapped[bool] 

    task: Mapped["Tasks"] = relationship("Tasks", back_populates="options")

    def __str__(self):
        return self.text[:50]

class Tasks_Gap(Base):
    id: Mapped[int_pk]
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    template: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)

    task: Mapped["Tasks"] = relationship("Tasks", back_populates="gaps")

    def __str__(self):
        return self.template[:50]
