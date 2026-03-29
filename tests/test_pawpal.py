import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Existing tests ──────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(name="Feed", duration=10, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Walk", duration=30, priority="medium"))
    assert len(pet.tasks) == 1


# ── Improvement 7: Empty-name validation ────────────────────────────────────────

def test_set_name_rejects_empty_string():
    task = Task(name="Feed", duration=10, priority="high")
    try:
        task.set_name("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_set_name_rejects_whitespace():
    task = Task(name="Feed", duration=10, priority="high")
    try:
        task.set_name("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_pet_set_name_rejects_empty():
    pet = Pet(name="Buddy", species="Dog")
    try:
        pet.set_name("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_owner_set_name_rejects_empty():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    try:
        owner.set_name("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ── Improvement 3: Task.depends_on / set_depends_on ─────────────────────────────

def test_set_depends_on_stores_value():
    task = Task(name="Play", duration=20, priority="medium")
    task.set_depends_on("Feed")
    assert task.depends_on == "Feed"


def test_set_depends_on_clears_with_none():
    task = Task(name="Play", duration=20, priority="medium", depends_on="Feed")
    task.set_depends_on(None)
    assert task.depends_on is None


# ── Improvement 4: Frequency + set_frequency ────────────────────────────────────

def test_set_frequency_valid_values():
    task = Task(name="Walk", duration=30, priority="high")
    for freq in ("daily", "weekly", "monthly"):
        task.set_frequency(freq)
        assert task.frequency == freq


def test_set_frequency_rejects_invalid():
    task = Task(name="Walk", duration=30, priority="high")
    try:
        task.set_frequency("hourly")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_set_frequency_accepts_none():
    task = Task(name="Walk", duration=30, priority="high", frequency="daily")
    task.set_frequency(None)
    assert task.frequency is None


# ── Improvement 5: preferred_slot / set_preferred_slot ──────────────────────────

def test_set_preferred_slot_valid_values():
    task = Task(name="Feed", duration=10, priority="high")
    for slot in ("morning", "afternoon", "evening"):
        task.set_preferred_slot(slot)
        assert task.preferred_slot == slot


def test_set_preferred_slot_rejects_invalid():
    task = Task(name="Feed", duration=10, priority="high")
    try:
        task.set_preferred_slot("midnight")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ── Improvement 1: Knapsack beats greedy on a crafted example ───────────────────

def test_knapsack_beats_greedy():
    """Greedy (shortest-first within priority) would pick two 5-min medium tasks (value=20)
    and skip the 9-min high task (value=100). Knapsack picks the high task instead."""
    owner = Owner(name="Sam", time_available=[("08:00", "08:09")])
    pet = Pet(name="Rex", species="Dog")
    # Two cheap medium tasks that fit in 10 min total but fill the 9-min budget
    pet.add_task(Task(name="Groom", duration=5, priority="medium"))
    pet.add_task(Task(name="Brush", duration=5, priority="medium"))
    # One high-priority task that fits exactly
    pet.add_task(Task(name="Medication", duration=9, priority="high"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).create_schedule()
    scheduled_names = {e["task"] for e in schedule["entries"]}

    # Knapsack must select Medication (high priority) over the two medium tasks
    assert "Medication" in scheduled_names
    assert "Groom" not in scheduled_names
    assert "Brush" not in scheduled_names


# ── Improvement 3: Dependency ordering ──────────────────────────────────────────

def test_depends_on_ordering_respected():
    """'Play' depends on 'Feed' — Feed must appear before Play regardless of duration sort."""
    owner = Owner(name="Alex", time_available=[("08:00", "09:00")])
    pet = Pet(name="Milo", species="Cat")
    pet.add_task(Task(name="Play", duration=20, priority="high", depends_on="Feed"))
    pet.add_task(Task(name="Feed", duration=5, priority="high"))
    owner.add_pet(pet)

    entries = Scheduler(owner).create_schedule()["entries"]
    names_in_order = [e["task"] for e in entries]
    assert names_in_order.index("Feed") < names_in_order.index("Play")


# ── Improvement 4: Urgency scoring boosts overdue tasks ─────────────────────────

def test_overdue_task_scheduled_over_same_priority_fresh_task():
    """An overdue daily task should outvalue a same-priority task done today."""
    owner = Owner(name="Jordan", time_available=[("08:00", "08:15")])
    pet = Pet(name="Luna", species="Dog")
    # Overdue daily walk — last done 3 days ago (2× overdue)
    overdue_walk = Task(name="Walk", duration=10, priority="medium",
                        frequency="daily", last_done=datetime.now() - timedelta(days=3))
    # Fresh medium task done today
    fresh_task = Task(name="Brush", duration=10, priority="medium",
                      last_done=datetime.now())
    pet.add_task(overdue_walk)
    pet.add_task(fresh_task)
    owner.add_pet(pet)

    # Only 15 min available, each task is 10 min — both fit, so this tests value ordering
    entries = Scheduler(owner).create_schedule()["entries"]
    names_in_order = [e["task"] for e in entries]
    # Walk should appear first since it's more urgent
    assert names_in_order[0] == "Walk"


# ── Improvement 5: Slot-preference bonus ────────────────────────────────────────

def test_slot_matching_task_preferred():
    """A morning-slot task should be preferred when current_slot='morning'."""
    owner = Owner(name="Taylor", time_available=[("08:00", "08:15")])
    pet = Pet(name="Cleo", species="Cat")
    pet.add_task(Task(name="Feed", duration=10, priority="medium", preferred_slot="morning"))
    pet.add_task(Task(name="Play", duration=10, priority="medium"))
    owner.add_pet(pet)

    # Both tasks are 10 min; only one fits in 15 min (or both do — just check Feed is first)
    entries = Scheduler(owner).create_schedule(current_slot="morning")["entries"]
    names = [e["task"] for e in entries]
    assert names[0] == "Feed"


def test_create_schedule_rejects_invalid_slot():
    owner = Owner(name="Sam", time_available=[("08:00", "09:00")])
    scheduler = Scheduler(owner)
    try:
        scheduler.create_schedule(current_slot="night")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ── Improvement 8: completion_ratio ─────────────────────────────────────────────

def test_completion_ratio_all_scheduled():
    owner = Owner(name="Kim", time_available=[("08:00", "09:00")])
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(name="Walk", duration=20, priority="high"))
    pet.add_task(Task(name="Feed", duration=10, priority="high"))
    owner.add_pet(pet)

    result = Scheduler(owner).create_schedule()
    assert result["completion_ratio"] == 1.0


def test_completion_ratio_partial():
    owner = Owner(name="Kim", time_available=[("08:00", "08:15")])
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task(name="Walk", duration=10, priority="high"))
    pet.add_task(Task(name="Feed", duration=10, priority="high"))
    owner.add_pet(pet)

    result = Scheduler(owner).create_schedule()
    assert 0.0 < result["completion_ratio"] < 1.0


def test_completion_ratio_all_already_completed():
    owner = Owner(name="Kim", time_available=[("08:00", "09:00")])
    pet = Pet(name="Biscuit", species="Dog")
    task = Task(name="Walk", duration=20, priority="high")
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)

    result = Scheduler(owner).create_schedule()
    assert result["completion_ratio"] == 1.0


# ── Improvement 6: Pet grouping ─────────────────────────────────────────────────

def test_same_pet_tasks_grouped_together():
    """Same-priority tasks for the same pet should appear consecutively."""
    owner = Owner(name="Morgan", time_available=[("08:00", "10:00")])
    dog = Pet(name="Rex", species="Dog")
    cat = Pet(name="Misty", species="Cat")
    dog.add_task(Task(name="Walk", duration=30, priority="medium"))
    cat.add_task(Task(name="Feed Cat", duration=5, priority="medium"))
    dog.add_task(Task(name="Groom Dog", duration=15, priority="medium"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    entries = Scheduler(owner).create_schedule()["entries"]
    pets_in_order = [e["pet"] for e in entries]
    # Rex's tasks should not be split by Misty's task
    rex_indices = [i for i, p in enumerate(pets_in_order) if p == "Rex"]
    assert rex_indices == list(range(min(rex_indices), max(rex_indices) + 1))


# ── complete_task: recurring task logic ─────────────────────────────────────────

def test_complete_task_daily_creates_next():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", frequency="daily"))
    owner.add_pet(pet)

    next_task = Scheduler(owner).complete_task("Buddy", "Walk")

    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "daily"
    assert any(t.name == "Walk" and t.completed for t in pet.tasks)
    assert len(pet.tasks) == 2


def test_complete_task_weekly_creates_next():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Bath", duration=20, priority="medium", frequency="weekly"))
    owner.add_pet(pet)

    next_task = Scheduler(owner).complete_task("Buddy", "Bath")

    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "weekly"
    assert len(pet.tasks) == 2


def test_complete_task_monthly_returns_none():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Vet Visit", duration=60, priority="high", frequency="monthly"))
    owner.add_pet(pet)

    result = Scheduler(owner).complete_task("Buddy", "Vet Visit")

    assert result is None
    assert len(pet.tasks) == 1
    assert pet.tasks[0].completed is True


def test_complete_task_no_frequency_returns_none():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="One-off Checkup", duration=45, priority="low", frequency=None))
    owner.add_pet(pet)

    result = Scheduler(owner).complete_task("Buddy", "One-off Checkup")

    assert result is None
    assert pet.tasks[0].completed is True


def test_complete_task_raises_for_unknown_pet():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    try:
        Scheduler(owner).complete_task("Ghost", "Walk")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_complete_task_raises_for_unknown_task():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", frequency="daily"))
    owner.add_pet(pet)
    try:
        Scheduler(owner).complete_task("Buddy", "Nonexistent Task")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_complete_task_raises_if_already_completed():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    task = Task(name="Walk", duration=30, priority="high", frequency="daily")
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)
    try:
        Scheduler(owner).complete_task("Buddy", "Walk")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_complete_task_new_task_inherits_fields():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    original = Task(
        name="Walk", duration=30, priority="high",
        frequency="daily", preferred_slot="morning",
        time="07:00", depends_on="Feed"
    )
    pet.add_task(original)
    owner.add_pet(pet)

    next_task = Scheduler(owner).complete_task("Buddy", "Walk")

    assert next_task.duration == 30
    assert next_task.priority == "high"
    assert next_task.preferred_slot == "morning"
    assert next_task.time == "07:00"
    assert next_task.depends_on == "Feed"
    assert next_task.frequency == "daily"


def test_complete_task_last_done_is_recent():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", frequency="daily"))
    owner.add_pet(pet)

    before = datetime.now()
    next_task = Scheduler(owner).complete_task("Buddy", "Walk")
    after = datetime.now()

    assert before <= next_task.last_done <= after


def test_complete_task_new_task_in_filter():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    next_task = scheduler.complete_task("Buddy", "Walk")
    incomplete = scheduler.filter_tasks(completed=False, pet_name="Buddy")

    assert next_task in incomplete
    assert len(incomplete) == 1


def test_complete_task_multiple_cycles_unique_names():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    t2 = scheduler.complete_task("Buddy", "Walk")       # creates "Walk #2"
    t3 = scheduler.complete_task("Buddy", t2.name)      # creates "Walk #3"

    names = {t.name for t in pet.tasks}
    assert "Walk" in names
    assert "Walk #2" in names
    assert "Walk #3" in names
    assert len(pet.tasks) == 3


# ---------------------------------------------------------------------------
# detect_conflicts tests
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_start_time():
    """Two tasks starting at the same time should conflict."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", time="08:00"))
    pet.add_task(Task(name="Feed", duration=15, priority="medium", time="08:00"))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feed" in conflicts[0]


def test_detect_conflicts_overlapping_windows():
    """Task B starting before task A finishes should conflict."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=60, priority="high", time="08:00"))
    pet.add_task(Task(name="Feed", duration=15, priority="medium", time="08:30"))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1


def test_detect_conflicts_no_overlap():
    """Non-overlapping tasks should produce no conflicts."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", time="08:00"))
    pet.add_task(Task(name="Feed", duration=15, priority="medium", time="09:00"))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert conflicts == []


def test_detect_conflicts_cross_pet():
    """Tasks on different pets with overlapping times should conflict."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet1 = Pet(name="Buddy", species="Dog")
    pet1.add_task(Task(name="Walk", duration=30, priority="high", time="08:00"))
    pet2 = Pet(name="Whiskers", species="Cat")
    pet2.add_task(Task(name="Groom", duration=20, priority="low", time="08:10"))
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1
    assert "Buddy" in conflicts[0]
    assert "Whiskers" in conflicts[0]


def test_detect_conflicts_tasks_without_time_ignored():
    """Tasks without a time field should never appear in conflicts."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high"))
    pet.add_task(Task(name="Feed", duration=15, priority="medium"))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert conflicts == []


def test_detect_conflicts_in_schedule_dict():
    """create_schedule() should include a 'conflicts' key."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", time="08:00"))
    pet.add_task(Task(name="Feed", duration=15, priority="medium", time="08:00"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).create_schedule()
    assert "conflicts" in schedule
    assert len(schedule["conflicts"]) == 1
