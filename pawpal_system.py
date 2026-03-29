from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class OwnerProfile:
	def __init__(
		self,
		owner_id: str,
		name: str,
		available_minutes: int,
		preferences: Optional[Dict[str, Any]] = None,
	) -> None:
		self.owner_id = owner_id
		self.name = name
		self.available_minutes = available_minutes
		self.preferences = preferences if preferences is not None else {}

	def set_availability(self, minutes: int) -> None:
		pass

	def set_preference(self, key: str, value: Any) -> None:
		pass

	def get_preference(self, key: str) -> Any:
		pass


@dataclass
class PetProfile:
	pet_id: str
	name: str
	species: str
	age_years: int
	care_notes: Dict[str, Any] = field(default_factory=dict)

	def update_care_note(self, key: str, value: Any) -> None:
		pass

	def get_care_note(self, key: str) -> Any:
		pass


@dataclass
class PetTask:
	task_id: str
	title: str
	category: str
	duration_minutes: int
	priority: int
	due_window: str
	completed: bool = False

	def mark_complete(self) -> None:
		pass

	def is_due_now(self, current_time: str) -> bool:
		pass


class TaskRepository:
	def __init__(self, tasks: Optional[List[PetTask]] = None) -> None:
		self.tasks = tasks if tasks is not None else []

	def add_task(self, task: PetTask) -> None:
		pass

	def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
		pass

	def remove_task(self, task_id: str) -> None:
		pass

	def get_tasks_by_category(self, category: str) -> List[PetTask]:
		pass

	def get_pending_tasks(self) -> List[PetTask]:
		pass


class ConstraintSet:
	def __init__(
		self,
		max_minutes: int,
		preferred_categories: Optional[List[str]] = None,
		blocked_time_windows: Optional[List[str]] = None,
		must_include_medication: bool = False,
	) -> None:
		self.max_minutes = max_minutes
		self.preferred_categories = (
			preferred_categories if preferred_categories is not None else []
		)
		self.blocked_time_windows = (
			blocked_time_windows if blocked_time_windows is not None else []
		)
		self.must_include_medication = must_include_medication

	def is_task_allowed(self, task: PetTask) -> bool:
		pass


class DailyPlan:
	def __init__(
		self,
		date: str,
		scheduled_items: Optional[List[Dict[str, Any]]] = None,
		total_minutes: int = 0,
	) -> None:
		self.date = date
		self.scheduled_items = scheduled_items if scheduled_items is not None else []
		self.total_minutes = total_minutes

	def add_item(self, task: PetTask, start_time: str) -> None:
		pass

	def fits_time_budget(self, max_minutes: int) -> bool:
		pass


class Scheduler:
	def rank_tasks(
		self, tasks: List[PetTask], owner: OwnerProfile, pet: PetProfile
	) -> List[PetTask]:
		pass

	def select_tasks(
		self, tasks: List[PetTask], constraints: ConstraintSet
	) -> List[PetTask]:
		pass

	def build_plan(
		self,
		owner: OwnerProfile,
		pet: PetProfile,
		tasks: List[PetTask],
		constraints: ConstraintSet,
	) -> DailyPlan:
		pass


class PlanExplainer:
	def explain_task_choice(self, task: PetTask, constraints: ConstraintSet) -> str:
		pass

	def explain_plan(self, plan: DailyPlan) -> str:
		pass
