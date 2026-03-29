from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional


class OwnerProfile:
	def __init__(
		self,
		owner_id: str,
		name: str,
		available_minutes: int,
		preferences: Optional[Dict[str, Any]] = None,
		pet_profile: Optional["PetProfile"] = None,
		constraints: Optional["ConstraintSet"] = None,
		pet_profiles: Optional[List["PetProfile"]] = None,
	) -> None:
		"""Initialize an owner profile with preferences, pets, and constraints."""
		self.owner_id = owner_id
		self.name = name
		self.available_minutes = available_minutes
		self.preferences = preferences if preferences is not None else {}
		self.pet_profile = pet_profile
		self.pet_profiles = pet_profiles if pet_profiles is not None else []
		if pet_profile is not None and all(existing.pet_id != pet_profile.pet_id for existing in self.pet_profiles):
			self.pet_profiles.append(pet_profile)
		self.constraints = constraints

	def set_availability(self, minutes: int) -> None:
		"""Update the owner's available minutes for pet care."""
		if minutes < 0:
			raise ValueError("available minutes cannot be negative")
		self.available_minutes = minutes

	def set_preference(self, key: str, value: Any) -> None:
		"""Store or update a named owner preference value."""
		self.preferences[key] = value

	def get_preference(self, key: str) -> Any:
		"""Return a stored owner preference by key if it exists."""
		return self.preferences.get(key)

	def add_pet(self, pet: "PetProfile") -> None:
		"""Add a pet to this owner while preventing duplicate pet IDs."""
		if all(existing.pet_id != pet.pet_id for existing in self.pet_profiles):
			self.pet_profiles.append(pet)
		if self.pet_profile is None:
			self.pet_profile = pet

	def remove_pet(self, pet_id: str) -> None:
		"""Remove a pet by ID and refresh the primary pet reference."""
		self.pet_profiles = [pet for pet in self.pet_profiles if pet.pet_id != pet_id]
		if self.pet_profile is not None and self.pet_profile.pet_id == pet_id:
			self.pet_profile = self.pet_profiles[0] if self.pet_profiles else None

	def get_all_tasks(self) -> List["PetTask"]:
		"""Collect all tasks across every pet owned by this owner."""
		all_tasks: List[PetTask] = []
		for pet in self.pet_profiles:
			all_tasks.extend(pet.tasks)
		return all_tasks


@dataclass
class PetProfile:
	pet_id: str
	name: str
	species: str
	age_years: int
	care_notes: Dict[str, Any] = field(default_factory=dict)
	tasks: List["PetTask"] = field(default_factory=list)

	def update_care_note(self, key: str, value: Any) -> None:
		"""Set or update a care note for this pet."""
		self.care_notes[key] = value

	def get_care_note(self, key: str) -> Any:
		"""Return a care note value for a given key if present."""
		return self.care_notes.get(key)

	def add_task(self, task: "PetTask") -> None:
		"""Attach a task to this pet if its task ID is unique."""
		if all(existing.task_id != task.task_id for existing in self.tasks):
			self.tasks.append(task)

	def remove_task(self, task_id: str) -> None:
		"""Remove a task from this pet by task ID."""
		self.tasks = [task for task in self.tasks if task.task_id != task_id]

	def get_pending_tasks(self) -> List["PetTask"]:
		"""Return this pet's tasks that are not yet completed."""
		return [task for task in self.tasks if not task.completed]


@dataclass
class PetTask:
	task_id: str
	title: str
	category: str
	duration_minutes: int
	priority: int
	due_window: str
	scheduled_time: str = "09:00"
	frequency: str = "none"
	due_date: str = field(default_factory=lambda: date.today().isoformat())
	completed: bool = False

	def mark_complete(self) -> None:
		"""Mark this task as completed."""
		self.completed = True

	def create_next_occurrence(self) -> Optional["PetTask"]:
		"""Create the next recurring task occurrence for daily or weekly frequencies."""
		frequency_lc = self.frequency.strip().lower()
		if frequency_lc not in {"daily", "weekly"}:
			return None

		base_date = datetime.strptime(self.due_date, "%Y-%m-%d").date()
		delta_days = 1 if frequency_lc == "daily" else 7
		next_due_date = (base_date + timedelta(days=delta_days)).isoformat()

		return PetTask(
			task_id=f"{self.task_id}-next-{next_due_date}",
			title=self.title,
			category=self.category,
			duration_minutes=self.duration_minutes,
			priority=self.priority,
			due_window=self.due_window,
			scheduled_time=self.scheduled_time,
			frequency=self.frequency,
			due_date=next_due_date,
			completed=False,
		)

	def is_due_now(self, current_time: str) -> bool:
		"""Check whether the task is due in the given time window."""
		if self.due_window.lower() == "any":
			return True
		return self.due_window.strip().lower() == current_time.strip().lower()


class TaskRepository:
	def __init__(self, tasks: Optional[List[PetTask]] = None) -> None:
		"""Initialize the task repository with optional preloaded tasks."""
		self.tasks = tasks if tasks is not None else []
		# Fast lookup index to avoid repeated O(n) scans for task_id operations.
		self.task_index: Dict[str, PetTask] = {task.task_id: task for task in self.tasks}

	def add_task(self, task: PetTask) -> None:
		"""Add a task to storage and index it by task ID."""
		if task.task_id in self.task_index:
			raise ValueError(f"task with id '{task.task_id}' already exists")
		self.tasks.append(task)
		self.task_index[task.task_id] = task

	def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
		"""Apply field updates to an existing task by task ID."""
		task = self.task_index.get(task_id)
		if task is None:
			raise KeyError(f"task with id '{task_id}' not found")

		for field_name, value in updates.items():
			if not hasattr(task, field_name):
				raise ValueError(f"unknown task field '{field_name}'")
			setattr(task, field_name, value)

		if "task_id" in updates:
			new_task_id = updates["task_id"]
			if new_task_id != task_id and new_task_id in self.task_index:
				raise ValueError(f"task with id '{new_task_id}' already exists")
			del self.task_index[task_id]
			self.task_index[new_task_id] = task

	def remove_task(self, task_id: str) -> None:
		"""Delete a task from both list storage and ID index."""
		task = self.task_index.pop(task_id, None)
		if task is None:
			return
		self.tasks = [existing_task for existing_task in self.tasks if existing_task.task_id != task_id]

	def get_tasks_by_category(self, category: str) -> List[PetTask]:
		"""Return all tasks that match the provided category."""
		category_lc = category.strip().lower()
		return [task for task in self.tasks if task.category.strip().lower() == category_lc]

	def get_pending_tasks(self) -> List[PetTask]:
		"""Return all tasks in the repository that are incomplete."""
		return [task for task in self.tasks if not task.completed]

	def mark_task_complete(self, task_id: str) -> Optional[PetTask]:
		"""Mark a task complete and return the next recurring occurrence if applicable."""
		task = self.task_index.get(task_id)
		if task is None:
			raise KeyError(f"task with id '{task_id}' not found")
		task.mark_complete()
		next_task = task.create_next_occurrence()
		if next_task is not None and next_task.task_id not in self.task_index:
			self.add_task(next_task)
		return next_task


class ConstraintSet:
	def __init__(
		self,
		max_minutes: int,
		preferred_categories: Optional[List[str]] = None,
		blocked_time_windows: Optional[List[str]] = None,
		must_include_medication: bool = False,
	) -> None:
		"""Initialize scheduling constraints used for task filtering."""
		self.max_minutes = max_minutes
		self.preferred_categories = (
			preferred_categories if preferred_categories is not None else []
		)
		self.blocked_time_windows = (
			blocked_time_windows if blocked_time_windows is not None else []
		)
		self.must_include_medication = must_include_medication

	def is_task_allowed(self, task: PetTask) -> bool:
		"""Return True when a task satisfies duration, category, and window rules."""
		if task.duration_minutes > self.max_minutes:
			return False

		if self.preferred_categories:
			preferred = {category.strip().lower() for category in self.preferred_categories}
			if task.category.strip().lower() not in preferred:
				return False

		if self.blocked_time_windows:
			blocked = {window.strip().lower() for window in self.blocked_time_windows}
			if task.due_window.strip().lower() in blocked:
				return False

		return True


class DailyPlan:
	def __init__(
		self,
		date: str,
		scheduled_items: Optional[List[Dict[str, Any]]] = None,
		total_minutes: int = 0,
	) -> None:
		"""Initialize a daily plan container for scheduled task items."""
		self.date = date
		self.scheduled_items = scheduled_items if scheduled_items is not None else []
		self.total_minutes = total_minutes

	def add_item(self, task: PetTask, start_time: str) -> None:
		"""Add a scheduled task item and update total planned minutes."""
		self.scheduled_items.append(
			{
				"task_id": task.task_id,
				"title": task.title,
				"category": task.category,
				"duration_minutes": task.duration_minutes,
				"priority": task.priority,
				"start_time": start_time,
				"due_window": task.due_window,
			}
		)
		self.total_minutes += task.duration_minutes

	def fits_time_budget(self, max_minutes: int) -> bool:
		"""Check whether the plan stays within a minute budget."""
		return self.total_minutes <= max_minutes


class Scheduler:
	def __init__(
		self,
		task_repository: TaskRepository,
		constraints: Optional[ConstraintSet] = None,
	) -> None:
		"""Initialize the scheduler with a task repository and optional defaults."""
		self.task_repository = task_repository
		self.constraints = constraints

	def rank_tasks(
		self, tasks: List[PetTask], owner: OwnerProfile, pet: PetProfile
	) -> List[PetTask]:
		"""Sort tasks by priority and owner preference boosts."""
		category_boosts = owner.get_preference("category_boosts") or {}

		def task_score(task: PetTask) -> tuple:
			category_bonus = int(category_boosts.get(task.category, 0))
			# Higher priority and owner preference boosts rank first; shorter tasks are tie-breakers.
			return (task.priority + category_bonus, -task.duration_minutes)

		return sorted(tasks, key=task_score, reverse=True)

	def sort_by_time(self, tasks: List[PetTask]) -> List[PetTask]:
		"""Sort tasks by HH:MM scheduled time, then by higher priority."""
		def sort_key(task: PetTask) -> tuple:
			time_value = datetime.strptime(task.scheduled_time, "%H:%M")
			return (time_value, -task.priority)

		return sorted(tasks, key=sort_key)

	def filter_tasks(
		self,
		tasks: List[PetTask],
		completed: Optional[bool] = None,
	) -> List[PetTask]:
		"""Filter tasks by optional completion status."""
		filtered: List[PetTask] = []
		for task in tasks:
			if completed is not None and task.completed != completed:
				continue
			filtered.append(task)
		return filtered

	def filter_owner_tasks(
		self,
		owner: OwnerProfile,
		pet_name: Optional[str] = None,
		completed: Optional[bool] = None,
	) -> List[PetTask]:
		"""Filter owner tasks by pet name and completion status."""
		selected_pet_ids = {
			pet.pet_id
			for pet in owner.pet_profiles
			if pet_name is None or pet.name.strip().lower() == pet_name.strip().lower()
		}

		result: List[PetTask] = []
		for pet in owner.pet_profiles:
			if pet.pet_id not in selected_pet_ids:
				continue
			for task in pet.tasks:
				if completed is not None and task.completed != completed:
					continue
				result.append(task)
		return result

	def detect_time_conflicts(self, tasks: List[PetTask]) -> List[str]:
		"""Return warnings when multiple tasks share the same scheduled HH:MM time."""
		seen: Dict[str, PetTask] = {}
		warnings: List[str] = []
		for task in self.sort_by_time(tasks):
			existing = seen.get(task.scheduled_time)
			if existing is not None:
				warnings.append(
					f"Conflict at {task.scheduled_time}: '{existing.title}' and '{task.title}'"
				)
			else:
				seen[task.scheduled_time] = task
		return warnings

	def mark_task_complete(self, task_id: str, owner: Optional[OwnerProfile] = None) -> Optional[PetTask]:
		"""Mark a task complete and attach the next recurring task to its pet when needed."""
		next_task = self.task_repository.mark_task_complete(task_id)
		if owner is None or next_task is None:
			return next_task

		for pet in owner.pet_profiles:
			if any(task.task_id == task_id for task in pet.tasks):
				pet.add_task(next_task)
				break
		return next_task

	def get_owner_tasks(self, owner: OwnerProfile, include_completed: bool = False) -> List[PetTask]:
		"""Return tasks for all pets owned by a specific owner."""
		tasks: List[PetTask] = []
		if owner.pet_profiles:
			for pet in owner.pet_profiles:
				tasks.extend(pet.tasks)
		elif owner.pet_profile is not None:
			tasks.extend(owner.pet_profile.tasks)

		if not include_completed:
			return [task for task in tasks if not task.completed]
		return tasks

	def get_all_tasks(self, include_completed: bool = False) -> List[PetTask]:
		"""Return repository tasks with optional inclusion of completed items."""
		tasks = self.task_repository.tasks
		if include_completed:
			return list(tasks)
		return [task for task in tasks if not task.completed]

	def select_tasks(
		self, tasks: List[PetTask], constraints: ConstraintSet
	) -> List[PetTask]:
		"""Choose feasible tasks under constraints and time budget."""
		selected: List[PetTask] = []
		used_minutes = 0

		for task in tasks:
			if task.completed:
				continue
			if not constraints.is_task_allowed(task):
				continue
			if used_minutes + task.duration_minutes > constraints.max_minutes:
				continue
			selected.append(task)
			used_minutes += task.duration_minutes

		if constraints.must_include_medication and selected:
			has_medication = any(task.category.strip().lower() == "medication" for task in selected)
			if not has_medication:
				for task in tasks:
					if task.completed:
						continue
					if task.category.strip().lower() != "medication":
						continue
					if not constraints.is_task_allowed(task):
						continue
					remaining_budget = constraints.max_minutes - used_minutes
					if task.duration_minutes <= remaining_budget:
						selected.append(task)
						break

		return selected

	def build_plan(
		self,
		owner: OwnerProfile,
		pet: PetProfile,
		tasks: List[PetTask],
		constraints: ConstraintSet,
	) -> DailyPlan:
		"""Build a daily plan by ranking, selecting, and time-ordering tasks."""
		ranked_tasks = self.rank_tasks(tasks, owner, pet)
		selected_tasks = self.sort_by_time(self.select_tasks(ranked_tasks, constraints))

		plan = DailyPlan(date=date.today().isoformat())
		start_time = owner.get_preference("day_start_time") or "08:00"
		current_time = datetime.strptime(start_time, "%H:%M")

		for task in selected_tasks:
			plan.add_item(task, current_time.strftime("%H:%M"))
			current_time += timedelta(minutes=task.duration_minutes)

		return plan


class PlanExplainer:
	def __init__(self, plan: Optional[DailyPlan] = None) -> None:
		"""Initialize the explainer with an optional precomputed plan."""
		self.plan = plan

	def explain_task_choice(self, task: PetTask, constraints: ConstraintSet) -> str:
		"""Generate a short explanation for why a task was selected."""
		reasons: List[str] = [
			f"priority={task.priority}",
			f"duration={task.duration_minutes}m",
			f"category={task.category}",
		]

		if constraints.preferred_categories:
			preferred = {category.strip().lower() for category in constraints.preferred_categories}
			if task.category.strip().lower() in preferred:
				reasons.append("matches preferred category")

		if constraints.must_include_medication and task.category.strip().lower() == "medication":
			reasons.append("helps satisfy medication requirement")

		return f"Selected '{task.title}' because " + ", ".join(reasons) + "."

	def explain_plan(self, plan: DailyPlan) -> str:
		"""Generate a readable summary of the full daily plan."""
		if not plan.scheduled_items:
			return "No tasks were scheduled for this plan."

		lines = [
			f"Daily plan for {plan.date}",
			f"Total scheduled time: {plan.total_minutes} minutes",
		]

		for item in plan.scheduled_items:
			lines.append(
				f"- {item['start_time']}: {item['title']} ({item['duration_minutes']}m, priority {item['priority']})"
			)

		return "\n".join(lines)
