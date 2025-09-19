"""Data Structures for LLM Agent."""

import uuid
from typing import Literal

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class Task(BaseModel):
    """Represents a single task with an instruction.

    Attributes:
        id_: Identifier for task.
        instruction: The instruction for the task.
    """

    id_: str = Field(default_factory=lambda: str(uuid.uuid4()))
    instruction: str


class TaskStep(BaseModel):
    """Represents a step within a task and its own instruction.

    Attributes:
        id_: Identifier for task step.
        task_id: ID of associated task.
        instruction: The instruction for the task.
    """

    id_: SkipJsonSchema[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    instruction: str = Field(
        description="The instruction for this step in the task.",
    )


class TaskStepResult(BaseModel):
    """The result of a task step execution.

    Attributes:
        task_step_id: The ID of the `TaskStep` that was executed.
        content: The content results of the execution.
    """

    task_step_id: str
    content: str

    def __str__(self) -> str:
        """String representation of TaskStepResult."""
        return self.content


class TaskResult(BaseModel):
    """The result of the task execution.

    Attributes:
        task_id: The ID `Task` that was executed.
        content: The content results of the task execution.
    """

    task_id: str
    content: str

    def __str__(self) -> str:
        """String representation of TaskResult."""
        return self.content


class NextStepDecision(BaseModel):
    """Structured output for TaskHandler.get_next_step()."""

    kind: Literal["next_step", "final_result"]
    content: str = Field(
        description=(
            "Content for the next step of the task execution. Or, the "
            "the final result."
        ),
    )
