from pawpal_system import Owner, Pet, Task, Scheduler

# --- Build pets and tasks ---

morning_walk = Task(name="Morning Walk", duration=30, priority="high")
feed_breakfast = Task(name="Feed Breakfast", duration=10, priority="high")

buddy = Pet(name="Buddy", species="Dog")
buddy.add_task(morning_walk)
buddy.add_task(feed_breakfast)
buddy.add_task(Task(name="Brush Fur", duration=15, priority="medium"))

whiskers = Pet(name="Whiskers", species="Cat")
whiskers.add_task(Task(name="Clean Litter Box", duration=10, priority="high"))
whiskers.add_task(Task(name="Playtime", duration=20, priority="medium"))
whiskers.add_task(Task(name="Trim Nails", duration=10, priority="low"))

# --- Mark some tasks as already completed ---

morning_walk.mark_complete()
feed_breakfast.mark_complete()

# --- Build owner ---

owner = Owner(name="Alex", time_available=40)
owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Generate and print schedule ---

schedule = Scheduler(owner=owner).create_schedule()

print(f"===== Today's Schedule for {owner.name} =====")
print(f"Available time: {int(owner.time_available)} min\n")

entries = schedule["entries"]
completed = schedule["completed"]
task_w = max((len(e["task"]) for e in entries + completed), default=10)
pet_w  = max((len(e["pet"])  for e in entries + completed), default=10)
dur_w  = max((len(str(int(e["duration"]))) for e in entries + completed), default=3)

if completed:
    print("Already Completed:")
    for c in completed:
        print(
            f"  [ DONE ] {c['task']:<{task_w}} ({c['pet']}){'':<{pet_w - len(c['pet'])}} "
            f"{int(c['duration']):>{dur_w}} min"
        )
    print()

print("Scheduled Tasks:")
for entry in entries:
    print(
        f"  [{entry['priority'].upper():^6}] {entry['task']:<{task_w}} ({entry['pet']}){'':<{pet_w - len(entry['pet'])}} "
        f"{int(entry['duration']):>{dur_w}} min"
    )
print(f"\n  Total scheduled: {int(schedule['total_time_scheduled'])} / {int(schedule['time_available'])} min")

if schedule["skipped"]:
    print("\nSkipped (not enough time):")
    for s in schedule["skipped"]:
        print(
            f"  [{s['priority'].upper():^6}] {s['task']:<{task_w}} ({s['pet']}){'':<{pet_w - len(s['pet'])}} "
            f"{int(s['duration']):>{dur_w}} min"
        )