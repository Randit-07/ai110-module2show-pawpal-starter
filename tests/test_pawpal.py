from datetime import date, timedelta

from pawpal_system import OwnerProfile, PetProfile, PetTask, Scheduler, TaskRepository


def build_owner_with_scheduler() -> tuple[OwnerProfile, Scheduler, PetProfile, PetProfile]:
    owner = OwnerProfile("owner-1", "Jordan", 120)
    mochi = PetProfile("pet-1", "Mochi", "dog", 3)
    luna = PetProfile("pet-2", "Luna", "cat", 5)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(TaskRepository(owner.get_all_tasks()))
    return owner, scheduler, mochi, luna


def test_sorting_correctness_orders_tasks_chronologically() -> None:
    owner, scheduler, mochi, _ = build_owner_with_scheduler()
    mochi.add_task(PetTask("task-a", "Late", "exercise", 20, 2, "morning", scheduled_time="18:00"))
    mochi.add_task(PetTask("task-b", "Early", "feeding", 10, 1, "morning", scheduled_time="08:30"))
    mochi.add_task(PetTask("task-c", "Mid", "grooming", 15, 3, "afternoon", scheduled_time="12:00"))

    tasks = scheduler.get_owner_tasks(owner)
    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.task_id for task in sorted_tasks] == ["task-b", "task-c", "task-a"]


def test_recurrence_daily_completion_creates_next_day_task() -> None:
    owner, scheduler, mochi, _ = build_owner_with_scheduler()
    today = date.today().isoformat()
    recurring = PetTask(
        "task-r",
        "Daily meds",
        "medication",
        5,
        3,
        "morning",
        scheduled_time="09:00",
        frequency="daily",
        due_date=today,
    )
    mochi.add_task(recurring)
    scheduler.task_repository = TaskRepository(owner.get_all_tasks())

    next_task = scheduler.mark_task_complete("task-r", owner)

    assert next_task is not None
    assert recurring.completed is True
    assert next_task.due_date == (date.today() + timedelta(days=1)).isoformat()
    assert any(task.task_id == next_task.task_id for task in mochi.tasks)


def test_conflict_detection_flags_duplicate_times() -> None:
    owner, scheduler, mochi, luna = build_owner_with_scheduler()
    mochi.add_task(PetTask("task-1", "Morning walk", "exercise", 20, 2, "morning", scheduled_time="09:00"))
    luna.add_task(PetTask("task-2", "Feed", "feeding", 10, 2, "morning", scheduled_time="09:00"))

    scheduler.task_repository = TaskRepository(owner.get_all_tasks())
    conflicts = scheduler.detect_time_conflicts(scheduler.get_owner_tasks(owner))

    assert len(conflicts) == 1
    assert "Conflict at 09:00" in conflicts[0]


def test_filtering_by_pet_and_status() -> None:
    owner, scheduler, mochi, luna = build_owner_with_scheduler()
    mochi_task = PetTask("task-m", "Walk", "exercise", 20, 2, "morning", scheduled_time="08:00")
    luna_task = PetTask("task-l", "Brush", "grooming", 15, 2, "morning", scheduled_time="08:30")
    mochi.add_task(mochi_task)
    luna.add_task(luna_task)
    luna_task.mark_complete()

    only_mochi_pending = scheduler.filter_owner_tasks(owner, pet_name="Mochi", completed=False)
    completed = scheduler.filter_tasks(owner.get_all_tasks(), completed=True)

    assert [task.task_id for task in only_mochi_pending] == ["task-m"]
    assert [task.task_id for task in completed] == ["task-l"]


def test_edge_case_pet_with_no_tasks_returns_empty_list() -> None:
    owner, scheduler, _, _ = build_owner_with_scheduler()

    pending = scheduler.get_owner_tasks(owner)
    conflicts = scheduler.detect_time_conflicts(pending)

    assert pending == []
    assert conflicts == []