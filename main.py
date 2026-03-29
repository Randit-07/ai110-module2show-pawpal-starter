from pawpal_system import OwnerProfile, PetProfile, PetTask, Scheduler, TaskRepository


def build_sample_data() -> tuple[OwnerProfile, Scheduler]:
	owner = OwnerProfile(
		owner_id="owner-001",
		name="Jordan",
		available_minutes=90,
		preferences={"day_start_time": "08:00"},
	)

	dog = PetProfile(pet_id="pet-001", name="Mochi", species="dog", age_years=3)
	cat = PetProfile(pet_id="pet-002", name="Luna", species="cat", age_years=5)

	owner.add_pet(dog)
	owner.add_pet(cat)

	# Add tasks out of order to verify sorting by explicit HH:MM time.
	dog.add_task(
		PetTask(
			task_id="task-001",
			title="Morning walk",
			category="exercise",
			duration_minutes=25,
			priority=3,
			due_window="morning",
			scheduled_time="09:00",
		)
	)
	cat.add_task(
		PetTask(
			task_id="task-002",
			title="Feed dinner",
			category="feeding",
			duration_minutes=10,
			priority=2,
			due_window="evening",
			scheduled_time="18:00",
		)
	)
	dog.add_task(
		PetTask(
			task_id="task-003",
			title="Give allergy medication",
			category="medication",
			duration_minutes=5,
			priority=4,
			due_window="afternoon",
			scheduled_time="12:00",
			frequency="daily",
		)
	)
	cat.add_task(
		PetTask(
			task_id="task-004",
			title="Brush coat",
			category="grooming",
			duration_minutes=15,
			priority=2,
			due_window="morning",
			scheduled_time="09:00",
		)
	)

	all_tasks = owner.get_all_tasks()
	task_repository = TaskRepository(tasks=all_tasks)
	scheduler = Scheduler(task_repository=task_repository)
	return owner, scheduler


def task_pet_name(owner: OwnerProfile, task: PetTask) -> str:
	for pet in owner.pet_profiles:
		if any(existing.task_id == task.task_id for existing in pet.tasks):
			return pet.name
	return "Unknown Pet"


def print_todays_schedule(owner: OwnerProfile, scheduler: Scheduler) -> None:
	print("Today's Schedule")
	print("=" * 16)
	print(f"Owner: {owner.name}")

	tasks = scheduler.get_owner_tasks(owner)
	if not tasks:
		print("No tasks scheduled for today.")
		return

	ordered_tasks = scheduler.sort_by_time(tasks)
	conflicts = scheduler.detect_time_conflicts(ordered_tasks)
	if conflicts:
		print("Warnings:")
		for warning in conflicts:
			print(f"- {warning}")

	for task in ordered_tasks:
		pet_name = task_pet_name(owner, task)
		print(
			f"- [{task.scheduled_time}] {task.title} for {pet_name} "
			f"({task.duration_minutes} min, priority {task.priority})"
		)


def print_filtered_views(owner: OwnerProfile, scheduler: Scheduler) -> None:
	print("\nFiltered Views")
	print("=" * 14)
	mochi_pending = scheduler.filter_owner_tasks(owner, pet_name="Mochi", completed=False)
	print("Pending tasks for Mochi:")
	for task in scheduler.sort_by_time(mochi_pending):
		print(f"- {task.scheduled_time} {task.title}")

	completed_tasks = scheduler.filter_tasks(scheduler.get_owner_tasks(owner, include_completed=True), completed=True)
	print("Completed tasks:")
	if not completed_tasks:
		print("- None")
	else:
		for task in scheduler.sort_by_time(completed_tasks):
			print(f"- {task.scheduled_time} {task.title}")


def demo_recurring_task(owner: OwnerProfile, scheduler: Scheduler) -> None:
	print("\nRecurring Task Demo")
	print("=" * 19)
	next_task = scheduler.mark_task_complete("task-003", owner)
	print("Marked 'task-003' as complete.")
	if next_task is None:
		print("- No recurring task created.")
	else:
		print(
			"- Created next occurrence: "
			f"{next_task.task_id} at {next_task.scheduled_time} on {next_task.due_date}"
		)


if __name__ == "__main__":
	owner_profile, schedule_brain = build_sample_data()
	print_todays_schedule(owner_profile, schedule_brain)
	print_filtered_views(owner_profile, schedule_brain)
	demo_recurring_task(owner_profile, schedule_brain)
