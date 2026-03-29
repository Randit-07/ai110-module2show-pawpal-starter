import pytest
from pawpal import Pet, Task

def test_mark_complete_changes_task_status():
    """Verify that calling mark_complete() actually changes the task's status."""
    task = Task("Feed the dog")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Buddy")
    initial_count = len(pet.tasks)
    task = Task("Walk the dog")
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1