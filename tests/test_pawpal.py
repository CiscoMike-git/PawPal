import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Task: properties, validation, lifecycle ───────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(name="Feed", duration=10, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


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


def test_set_duration_zero_raises():
    """set_duration(0) is below the valid range [1, 240] and must raise ValueError."""
    task = Task(name="Feed", duration=10, priority="high")
    try:
        task.set_duration(0)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_set_duration_over_max_raises():
    """set_duration(240) is the valid maximum; set_duration(241) must raise ValueError."""
    task = Task(name="Feed", duration=10, priority="high")
    task.set_duration(240)
    assert task.duration == 240
    try:
        task.set_duration(241)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_set_priority_valid_values():
    task = Task(name="Feed", duration=10, priority="high")
    for p in ("low", "medium", "high"):
        task.set_priority(p)
        assert task.priority == p


def test_set_priority_rejects_invalid():
    task = Task(name="Feed", duration=10, priority="high")
    try:
        task.set_priority("urgent")
        assert False, "Expected ValueError"
    except ValueError:
        pass


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


def test_set_depends_on_stores_value():
    task = Task(name="Play", duration=20, priority="medium")
    task.set_depends_on("Feed")
    assert task.depends_on == "Feed"


def test_set_depends_on_clears_with_none():
    task = Task(name="Play", duration=20, priority="medium", depends_on="Feed")
    task.set_depends_on(None)
    assert task.depends_on is None


def test_set_last_done_stores_value():
    task = Task(name="Walk", duration=30, priority="high")
    when = datetime.now()
    task.set_last_done(when)
    assert task.last_done == when


def test_urgency_multiplier_no_frequency_returns_zero():
    """urgency_multiplier() returns 0.0 when frequency is None regardless of last_done."""
    task = Task(name="Walk", duration=30, priority="high",
                frequency=None, last_done=datetime.now() - timedelta(days=10))
    assert task.urgency_multiplier() == 0.0


def test_urgency_multiplier_on_schedule_returns_zero():
    """urgency_multiplier() returns 0.0 when task was done within its period."""
    task = Task(name="Walk", duration=30, priority="high",
                frequency="weekly", last_done=datetime.now() - timedelta(days=3))
    assert task.urgency_multiplier() == 0.0


def test_urgency_multiplier_overdue_returns_positive():
    """urgency_multiplier() returns a positive value when the task is overdue."""
    task = Task(name="Walk", duration=30, priority="high",
                frequency="daily", last_done=datetime.now() - timedelta(days=5))
    assert task.urgency_multiplier() > 0.0


def test_scheduling_value_slot_bonus_applied():
    """scheduling_value() returns a strictly higher value when the current slot matches preferred_slot."""
    task = Task(name="Feed", duration=10, priority="medium", preferred_slot="morning")
    value_match = task.scheduling_value(current_slot="morning")
    value_no_match = task.scheduling_value(current_slot="evening")
    assert value_match > value_no_match


# ── Pet: properties and task management ──────────────────────────────────────

def test_pet_set_name_rejects_empty():
    pet = Pet(name="Buddy", species="Dog")
    try:
        pet.set_name("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_pet_set_species_stores_value():
    pet = Pet(name="Buddy", species="Dog")
    pet.set_species("Cat")
    assert pet.species == "Cat"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Walk", duration=30, priority="medium"))
    assert len(pet.tasks) == 1


def test_add_task_duplicate_name_raises():
    """Adding a second task with the same name to a pet raises ValueError; pet still has one task."""
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high"))
    try:
        pet.add_task(Task(name="Walk", duration=15, priority="medium"))
        assert False, "Expected ValueError"
    except ValueError:
        pass
    assert len(pet.tasks) == 1


def test_pet_remove_task_valid():
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high"))
    pet.remove_task("Walk")
    assert len(pet.tasks) == 0


def test_pet_remove_task_not_found_raises():
    pet = Pet(name="Buddy", species="Dog")
    try:
        pet.remove_task("Nonexistent")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ── Owner: name, time windows, pet management ─────────────────────────────────

def test_owner_set_name_rejects_empty():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    try:
        owner.set_name("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_owner_add_time_window_valid():
    owner = Owner(name="Alice", time_available=[])
    owner.add_time_window("08:00", "09:00")
    assert ("08:00", "09:00") in owner.time_available


def test_owner_add_time_window_invalid_format_raises():
    owner = Owner(name="Alice", time_available=[])
    try:
        owner.add_time_window("8am", "9am")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_owner_add_time_window_end_before_start_raises():
    owner = Owner(name="Alice", time_available=[])
    try:
        owner.add_time_window("09:00", "08:00")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_owner_remove_time_window_valid():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    owner.remove_time_window("08:00", "09:00")
    assert owner.time_available == []


def test_owner_remove_time_window_not_found_raises():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    try:
        owner.remove_time_window("10:00", "11:00")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_owner_time_available_minutes_sum():
    """time_available_minutes sums all window durations correctly."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00"), ("12:00", "12:30")])
    assert owner.time_available_minutes == 90.0


def test_add_pet_duplicate_name_raises():
    """Adding a second pet with the same name raises ValueError; owner still has only one pet."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    owner.add_pet(Pet(name="Buddy", species="Dog"))
    try:
        owner.add_pet(Pet(name="Buddy", species="Cat"))
        assert False, "Expected ValueError"
    except ValueError:
        pass
    assert len(owner.pets) == 1


def test_owner_remove_pet_valid():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    owner.add_pet(Pet(name="Buddy", species="Dog"))
    owner.remove_pet("Buddy")
    assert len(owner.pets) == 0


def test_owner_remove_pet_not_found_raises():
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    try:
        owner.remove_pet("Ghost")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ── Scheduler: initialization ─────────────────────────────────────────────────

def test_scheduler_set_owner():
    scheduler = Scheduler()
    assert scheduler.owner is None
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    scheduler.set_owner(owner)
    assert scheduler.owner is owner


# ── Scheduling algorithm: knapsack, selection, metrics ───────────────────────

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

    # Only 15 min available, each task is 10 min — only one fits, so knapsack must pick the higher-value Walk
    entries = Scheduler(owner).create_schedule()["entries"]
    names_in_order = [e["task"] for e in entries]
    # Walk should appear first since it's more urgent
    assert names_in_order[0] == "Walk"


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


def test_create_schedule_no_owner_raises():
    """create_schedule() must raise ValueError when no owner is assigned."""
    try:
        Scheduler().create_schedule()
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_create_schedule_rejects_invalid_slot():
    owner = Owner(name="Sam", time_available=[("08:00", "09:00")])
    scheduler = Scheduler(owner)
    try:
        scheduler.create_schedule(current_slot="night")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_create_schedule_no_time_windows_all_skipped():
    """Owner with zero time windows: knapsack capacity is 0, all tasks land in skipped."""
    owner = Owner(name="Alice", time_available=[])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high"))
    pet.add_task(Task(name="Feed", duration=10, priority="medium"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).create_schedule()

    assert schedule["entries"] == []
    assert len(schedule["skipped"]) == 2
    assert schedule["total_time_scheduled"] == 0
    assert schedule["time_available"] == 0.0


def test_create_schedule_task_longer_than_window_is_skipped():
    """BigTask (25 min) fits the total budget (40 min) but exceeds every remaining
    window after SmallTask (15 min) fills the first 20-min window."""
    owner = Owner(name="Alice", time_available=[("08:00", "08:20"), ("09:00", "09:20")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="SmallTask", duration=15, priority="high"))
    pet.add_task(Task(name="BigTask", duration=25, priority="high"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).create_schedule()
    entry_names = {e["task"] for e in schedule["entries"]}
    skipped_map = {s["task"]: s["reason"] for s in schedule["skipped"]}

    assert "SmallTask" in entry_names
    assert "BigTask" in skipped_map
    assert skipped_map["BigTask"] == "window gap too small to place after earlier tasks"


# ── Dependency resolution ─────────────────────────────────────────────────────

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


def test_create_schedule_depends_on_nonexistent_task_no_crash():
    """A dangling depends_on reference (task not in schedule) is silently ignored; no exception raised."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", depends_on="Vet Visit"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).create_schedule()

    entry_names = [e["task"] for e in schedule["entries"]]
    assert "Walk" in entry_names


def test_create_schedule_dependency_cycle_falls_back_gracefully():
    """Feed depends on Play and Play depends on Feed (cycle). Topo-sort detects it
    and falls back to original order; both tasks must still appear in entries."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Feed", duration=10, priority="high", depends_on="Play"))
    pet.add_task(Task(name="Play", duration=10, priority="high", depends_on="Feed"))
    owner.add_pet(pet)

    schedule = Scheduler(owner).create_schedule()

    entry_names = {e["task"] for e in schedule["entries"]}
    assert "Feed" in entry_names
    assert "Play" in entry_names
    assert len(schedule["entries"]) == 2


# ── Task recurrence: complete_task ───────────────────────────────────────────

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


def test_complete_task_monthly_creates_next():
    """Monthly frequency produces a new task occurrence, mirroring daily/weekly behavior."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Flea Treatment", duration=15, priority="low", frequency="monthly"))
    owner.add_pet(pet)

    next_task = Scheduler(owner).complete_task("Buddy", "Flea Treatment")

    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "monthly"
    assert len(pet.tasks) == 2


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
    scheduler.complete_task("Buddy", t2.name)            # creates "Walk #3"

    names = {t.name for t in pet.tasks}
    assert "Walk" in names
    assert "Walk #2" in names
    assert "Walk #3" in names
    assert len(pet.tasks) == 3


def test_complete_task_new_occurrence_is_not_completed():
    """A newly created recurrence task must always start with completed=False."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", frequency="daily"))
    owner.add_pet(pet)

    next_task = Scheduler(owner).complete_task("Buddy", "Walk")
    assert next_task.completed is False


def test_complete_task_name_with_embedded_number_not_stripped():
    """'Walk 2 dogs' has no ' #N' suffix, so the full name is the base; next is 'Walk 2 dogs #2'."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk 2 dogs", duration=30, priority="high", frequency="daily"))
    owner.add_pet(pet)

    next_task = Scheduler(owner).complete_task("Buddy", "Walk 2 dogs")

    assert next_task is not None
    assert next_task.name == "Walk 2 dogs #2"


def test_complete_task_starting_name_with_hash_suffix():
    """Task named 'Feed #1' has a parseable suffix; base is 'Feed', so next is 'Feed #2' not 'Feed #1 #2'."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Feed #1", duration=10, priority="high", frequency="daily"))
    owner.add_pet(pet)

    next_task = Scheduler(owner).complete_task("Buddy", "Feed #1")

    assert next_task is not None
    assert next_task.name == "Feed #2"
    assert any(t.name == "Feed #1" and t.completed for t in pet.tasks)


# ── Conflict detection ────────────────────────────────────────────────────────

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


def test_detect_conflicts_strict_adjacency_no_conflict():
    """Task A ends exactly when task B starts (09:30); strictly adjacent tasks must NOT conflict."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", time="09:00"))
    pet.add_task(Task(name="Feed", duration=15, priority="medium", time="09:30"))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert conflicts == []


def test_detect_conflicts_three_way_overlap():
    """Three tasks all starting at the same time produce three pairwise conflict warnings."""
    owner = Owner(name="Alice", time_available=[("08:00", "10:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Walk", duration=30, priority="high", time="08:00"))
    pet.add_task(Task(name="Feed", duration=20, priority="medium", time="08:00"))
    pet.add_task(Task(name="Groom", duration=15, priority="low", time="08:00"))
    owner.add_pet(pet)

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 3


def test_detect_conflicts_no_owner_returns_empty():
    """detect_conflicts() on a scheduler with no owner must return [] without raising."""
    result = Scheduler().detect_conflicts()
    assert result == []


# ── Filter tasks ──────────────────────────────────────────────────────────────

def test_filter_tasks_completed_true():
    """filter_tasks(completed=True) returns only completed tasks across all pets."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    done = Task(name="Walk", duration=30, priority="high")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task(name="Feed", duration=10, priority="medium"))
    owner.add_pet(pet)

    result = Scheduler(owner).filter_tasks(completed=True)
    assert len(result) == 1
    assert result[0].name == "Walk"


def test_filter_tasks_no_filters_returns_all():
    """filter_tasks() with no arguments returns every task regardless of status or pet."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    pet = Pet(name="Buddy", species="Dog")
    done = Task(name="Walk", duration=30, priority="high")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task(name="Feed", duration=10, priority="medium"))
    owner.add_pet(pet)

    result = Scheduler(owner).filter_tasks()
    assert len(result) == 2


def test_filter_tasks_combined_completed_and_pet_name():
    """filter_tasks(completed=False, pet_name='Fido') returns only Fido's incomplete tasks."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    fido = Pet(name="Fido", species="Dog")
    walk = Task(name="Walk", duration=30, priority="high")
    walk.mark_complete()
    fido.add_task(walk)
    fido.add_task(Task(name="Feed", duration=10, priority="medium"))
    whiskers = Pet(name="Whiskers", species="Cat")
    whiskers.add_task(Task(name="Groom", duration=15, priority="low"))
    owner.add_pet(fido)
    owner.add_pet(whiskers)

    result = Scheduler(owner).filter_tasks(completed=False, pet_name="Fido")
    result_names = [t.name for t in result]

    assert result_names == ["Feed"]
    assert "Walk" not in result_names
    assert "Groom" not in result_names


def test_filter_tasks_no_owner_raises():
    """filter_tasks() must raise ValueError when no owner is assigned."""
    try:
        Scheduler().filter_tasks()
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_filter_tasks_unknown_pet_raises():
    """filter_tasks(pet_name='Ghost') raises ValueError if no such pet exists."""
    owner = Owner(name="Alice", time_available=[("08:00", "09:00")])
    owner.add_pet(Pet(name="Buddy", species="Dog"))
    try:
        Scheduler(owner).filter_tasks(pet_name="Ghost")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ── Sort by time ──────────────────────────────────────────────────────────────

def test_sort_by_time_chronological_order():
    """Tasks with time values are returned in ascending chronological order."""
    owner = Owner(name="Alice", time_available=[("07:00", "19:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Evening", duration=10, priority="low", time="18:00"))
    pet.add_task(Task(name="Morning", duration=10, priority="low", time="07:00"))
    pet.add_task(Task(name="Noon", duration=10, priority="low", time="12:00"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_time()
    assert [t.name for t in result] == ["Morning", "Noon", "Evening"]


def test_sort_by_time_untimed_appended_at_end():
    """Timed tasks appear first in chronological order; untimed tasks follow in insertion order."""
    owner = Owner(name="Alice", time_available=[("07:00", "19:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="A", duration=10, priority="low", time=None))
    pet.add_task(Task(name="B", duration=10, priority="low", time="09:00"))
    pet.add_task(Task(name="C", duration=10, priority="low", time=None))
    pet.add_task(Task(name="D", duration=10, priority="low", time="07:30"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_time()
    assert [t.name for t in result] == ["D", "B", "A", "C"]


def test_sort_by_time_all_untimed_preserves_order():
    """When no task has a time value, original insertion order is preserved."""
    owner = Owner(name="Alice", time_available=[("07:00", "19:00")])
    pet = Pet(name="Buddy", species="Dog")
    pet.add_task(Task(name="Feed", duration=10, priority="low"))
    pet.add_task(Task(name="Walk", duration=10, priority="low"))
    pet.add_task(Task(name="Play", duration=10, priority="low"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_time()
    assert [t.name for t in result] == ["Feed", "Walk", "Play"]


def test_sort_by_time_cross_pet_ordering():
    """Tasks from different pets with explicit times are merged into a single chronological list."""
    owner = Owner(name="Alice", time_available=[("07:00", "19:00")])
    dog = Pet(name="Rex", species="Dog")
    cat = Pet(name="Misty", species="Cat")
    dog.add_task(Task(name="Walk Rex", duration=30, priority="high", time="09:00"))
    cat.add_task(Task(name="Feed Misty", duration=10, priority="high", time="07:30"))
    dog.add_task(Task(name="Groom Rex", duration=15, priority="low", time="14:00"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    result = Scheduler(owner).sort_by_time()
    assert [t.name for t in result] == ["Feed Misty", "Walk Rex", "Groom Rex"]


def test_sort_by_time_no_owner_raises():
    """sort_by_time() must raise ValueError when no owner is assigned to the scheduler."""
    try:
        Scheduler().sort_by_time()
        assert False, "Expected ValueError"
    except ValueError:
        pass
