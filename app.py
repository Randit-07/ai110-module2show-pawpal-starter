import streamlit as st
from pawpal_system import ConstraintSet, OwnerProfile, PetProfile, PetTask, Scheduler, TaskRepository


def priority_label_to_score(label: str) -> int:
    """Convert UI priority labels to numeric scores used by the scheduler."""
    mapping = {"low": 1, "medium": 2, "high": 3}
    return mapping[label]


def initialize_state() -> None:
    """Create session-backed application objects once per browser session."""
    if "owner" not in st.session_state:
        st.session_state["owner"] = OwnerProfile(
            owner_id="owner-001",
            name="Jordan",
            available_minutes=90,
            preferences={"day_start_time": "08:00"},
        )
    if "task_counter" not in st.session_state:
        st.session_state["task_counter"] = 1
    if "pet_counter" not in st.session_state:
        st.session_state["pet_counter"] = 1


def build_scheduler(owner: OwnerProfile) -> Scheduler:
    """Build a scheduler from tasks currently stored across all owner pets."""
    repository = TaskRepository(owner.get_all_tasks())
    return Scheduler(task_repository=repository)


initialize_state()
owner: OwnerProfile = st.session_state["owner"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
available_minutes = st.number_input(
    "Available minutes today",
    min_value=0,
    max_value=24 * 60,
    value=int(owner.available_minutes),
    step=5,
)

owner.name = owner_name
owner.set_availability(int(available_minutes))

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form"):
    new_pet_name = st.text_input("Pet name")
    new_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    new_age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not new_pet_name.strip():
        st.error("Please enter a pet name.")
    else:
        pet_id = f"pet-{st.session_state['pet_counter']:03d}"
        st.session_state["pet_counter"] += 1
        owner.add_pet(
            PetProfile(
                pet_id=pet_id,
                name=new_pet_name.strip(),
                species=new_species,
                age_years=int(new_age),
            )
        )
        st.success(f"Added pet: {new_pet_name.strip()}")

if owner.pet_profiles:
    st.markdown("### Current pets")
    pet_rows = [
        {
            "pet_id": pet.pet_id,
            "name": pet.name,
            "species": pet.species,
            "age_years": pet.age_years,
            "task_count": len(pet.tasks),
        }
        for pet in owner.pet_profiles
    ]
    st.table(pet_rows)
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if not owner.pet_profiles:
    st.warning("Add at least one pet before creating tasks.")
else:
    pet_options = {f"{pet.name} ({pet.species})": pet for pet in owner.pet_profiles}
    with st.form("add_task_form"):
        selected_pet_label = st.selectbox("Assign task to", list(pet_options.keys()))
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox(
            "Category",
            ["exercise", "feeding", "medication", "enrichment", "grooming", "other"],
        )
        due_window = st.selectbox("Time window", ["morning", "afternoon", "evening", "night", "any"])
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        if not task_title.strip():
            st.error("Please enter a task title.")
        else:
            selected_pet = pet_options[selected_pet_label]
            task_id = f"task-{st.session_state['task_counter']:03d}"
            st.session_state["task_counter"] += 1
            selected_pet.add_task(
                PetTask(
                    task_id=task_id,
                    title=task_title.strip(),
                    category=category,
                    duration_minutes=int(duration),
                    priority=priority_label_to_score(priority_label),
                    due_window=due_window,
                )
            )
            st.success(f"Added task '{task_title.strip()}' to {selected_pet.name}.")

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.markdown("### Current tasks")
    task_rows = []
    for pet in owner.pet_profiles:
        for task in pet.tasks:
            task_rows.append(
                {
                    "pet": pet.name,
                    "title": task.title,
                    "category": task.category,
                    "due_window": task.due_window,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority,
                    "completed": task.completed,
                }
            )
    st.table(task_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a schedule from your persisted pets and tasks.")

if st.button("Generate schedule"):
    if not owner.pet_profiles:
        st.warning("Add at least one pet first.")
    elif not owner.get_all_tasks():
        st.warning("Add at least one task first.")
    else:
        scheduler = build_scheduler(owner)
        constraints = ConstraintSet(max_minutes=owner.available_minutes)
        primary_pet = owner.pet_profiles[0]
        plan = scheduler.build_plan(owner, primary_pet, scheduler.get_owner_tasks(owner), constraints)

        if not plan.scheduled_items:
            st.info("No tasks could be scheduled under current constraints.")
        else:
            st.success("Today's Schedule")
            st.caption(f"Total planned minutes: {plan.total_minutes}")
            st.table(plan.scheduled_items)
