# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- My initial UML design separated data objects (Owner, Pet, PetTask) from orchestration objects (TaskRepository, Scheduler, PlanExplainer, DailyPlan).
- The owner profile stores available time and preferences, and the pet profile stores species-specific care notes.
- Tasks are represented as structured objects (category, duration, priority, optional due time), and are inserted/updated through a repository.
- Scheduler evaluates constraints (minutes available, priority, owner preferences, due windows) to generate a feasible daily plan.
- PlanExplainer generates human-readable reasons for why each task was chosen and ordered.

```mermaid
classDiagram
  class OwnerProfile {
    +str owner_id
    +str name
    +int available_minutes
    +dict preferences
    +set_availability(minutes)
    +set_preference(key, value)
    +get_preference(key)
  }

  class PetProfile {
    +str pet_id
    +str name
    +str species
    +int age_years
    +dict care_notes
    +update_care_note(key, value)
    +get_care_note(key)
  }

  class PetTask {
    +str task_id
    +str title
    +str category
    +int duration_minutes
    +int priority
    +str due_window
    +bool completed
    +mark_complete()
    +is_due_now(current_time)
  }

  class TaskRepository {
    +list tasks
    +add_task(task)
    +update_task(task_id, updates)
    +remove_task(task_id)
    +get_tasks_by_category(category)
    +get_pending_tasks()
  }

  class ConstraintSet {
    +int max_minutes
    +list preferred_categories
    +list blocked_time_windows
    +bool must_include_medication
    +is_task_allowed(task)
  }

  class DailyPlan {
    +str date
    +list scheduled_items
    +int total_minutes
    +add_item(task, start_time)
    +fits_time_budget(max_minutes)
  }

  class Scheduler {
    +rank_tasks(tasks, owner, pet)
    +select_tasks(tasks, constraints)
    +build_plan(owner, pet, tasks, constraints) DailyPlan
  }

  class PlanExplainer {
    +explain_task_choice(task, constraints)
    +explain_plan(plan)
  }

  OwnerProfile "1" --> "1" PetProfile : cares for
  OwnerProfile "1" --> "1" ConstraintSet : provides
  TaskRepository "1" --> "many" PetTask : stores
  Scheduler "1" --> "1" TaskRepository : reads tasks
  Scheduler "1" --> "1" ConstraintSet : applies
  Scheduler "1" --> "1" DailyPlan : produces
  PlanExplainer "1" --> "1" DailyPlan : explains
```

**b. Design changes**

- ## Did your design change during implementation?
  -
- ## If yes, describe at least one change and why you made it.
  -

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
