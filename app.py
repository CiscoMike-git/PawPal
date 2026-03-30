import streamlit as st
import pandas as pd
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")


def _priority_bg(val: str) -> str:
    key = val.strip("[] ").lower()
    return {
        "high":   "background-color: #ff4b4b; color: white",
        "medium": "background-color: #ffd700; color: black",
        "low":    "background-color: #21c55d; color: white",
    }.get(key, "")


def _priority_table(rows: list, priority_col: str = "Priority") -> None:
    df = pd.DataFrame(rows)
    if priority_col in df.columns:
        st.dataframe(
            df.style.map(_priority_bg, subset=[priority_col]),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.table(rows)


def _make_tags(row: dict) -> str:
    parts = []
    if row.get("preferred_slot"):
        parts.append(f"[{row['preferred_slot']}]")
    if row.get("frequency"):
        parts.append(f"({row['frequency']})")
    if row.get("depends_on"):
        parts.append(f"after: {row['depends_on']}")
    return "  ".join(parts)


def _render_schedule(schedule: dict, owner: Owner, slot: str) -> None:
    entries   = schedule["entries"]
    completed = schedule["completed"]
    skipped   = schedule["skipped"]

    windows_str = ", ".join(f"{s}–{e}" for s, e in owner.time_available)
    st.subheader(f"Today's Schedule for {owner.name} ({slot.title()})")
    st.caption(f"Available: {int(owner.time_available_minutes)} min ({windows_str})")

    if completed:
        st.markdown("**Already Completed**")
        st.table([
            {
                "Status":   "[ DONE ]",
                "Task":     r["task"],
                "Pet":      r["pet"],
                "Duration": f"{int(r['duration'])} min",
                "Tags":     _make_tags(r),
            }
            for r in completed
        ])

    st.markdown("**Scheduled Tasks**")
    if entries:
        _priority_table([
            {
                "Time":     r["time"] if r["time"] else "??:??",
                "Priority": r["priority"].lower(),
                "Task":     r["task"],
                "Pet":      r["pet"],
                "Duration": f"{int(r['duration'])} min",
                "Tags":     _make_tags(r),
            }
            for r in entries
        ])
    else:
        st.info("No tasks could be scheduled.")
    st.caption(
        f"Total scheduled: {int(schedule['total_time_scheduled'])} / "
        f"{int(schedule['time_available'])} min"
    )

    if skipped:
        st.markdown("**Skipped (not enough time)**")
        _priority_table([
            {
                "Priority": r["priority"].lower(),
                "Task":     r["task"],
                "Pet":      r["pet"],
                "Duration": f"{int(r['duration'])} min",
                "Tags":     _make_tags(r),
            }
            for r in skipped
        ])

    for warning in schedule["conflicts"]:
        st.warning(warning)

    st.info(schedule["explanation"])


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

st.subheader("Owner")

owner_name = st.text_input("Owner name", value="Jordan").title()

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
else:
    st.session_state.owner.name = owner_name  # sync if text input changed

if st.session_state.owner.time_available:
    st.markdown("**Available Time Windows**")
    for s, e in st.session_state.owner.time_available:
        st.write(f"- {s} – {e}")
    st.caption(f"Total: {int(st.session_state.owner.time_available_minutes)} min")
else:
    st.info("No availability windows added yet.")

col_ws, col_we = st.columns(2)
with col_ws:
    win_start = st.text_input("Window start (HH:MM)", value="08:00")
with col_we:
    win_end = st.text_input("Window end (HH:MM)", value="09:00")

col_add_w, col_rem_w = st.columns(2)
with col_add_w:
    if st.button("Add window"):
        try:
            st.session_state.owner.add_time_window(win_start, win_end)
            st.rerun()
        except ValueError as e:
            st.error(str(e))
with col_rem_w:
    if st.button("Remove window"):
        try:
            st.session_state.owner.remove_time_window(win_start, win_end)
            st.rerun()
        except ValueError as e:
            st.error(str(e))


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

st.subheader("Pets")

if st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.name} ({pet.species})")
else:
    st.info("No pets added yet.")

pet_name = st.text_input("Pet name", value="Mochi").title()
species = st.selectbox("Species", ["dog", "cat", "other"])

col_add, col_rem = st.columns(2)
with col_add:
    if st.button("Add pet"):
        try:
            st.session_state.owner.add_pet(Pet(name=pet_name, species=species))
            st.rerun()
        except ValueError as e:
            st.error(str(e))
with col_rem:
    if st.button("Remove pet"):
        try:
            st.session_state.owner.remove_pet(pet_name)
            st.rerun()
        except ValueError as e:
            st.error(str(e))


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

st.subheader("Tasks")

pet_names = [p.name for p in st.session_state.owner.pets]

if pet_names:
    selected_pet_name = st.selectbox("Select pet", pet_names)

    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
    if selected_pet.tasks:
        st.write("Current tasks:")
        _priority_table([
            {
                "Task":      t.name,
                "Duration":  f"{int(t.duration)} min",
                "Priority":  t.priority,
                "Frequency": t.frequency or "—",
                "Slot":      t.preferred_slot or "—",
                "Depends on": t.depends_on or "—",
                "Done":      "✓" if t.completed else "",
            }
            for t in selected_pet.tasks
        ])
    else:
        st.info("No tasks yet for this pet. Add one below.")

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk").title()
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        frequency_opts = ["None", "daily", "weekly", "monthly"]
        frequency = st.selectbox("Frequency", frequency_opts)
        frequency = None if frequency == "None" else frequency
    with col5:
        slot_opts = ["None", "morning", "afternoon", "evening"]
        preferred_slot = st.selectbox("Preferred slot", slot_opts)
        preferred_slot = None if preferred_slot == "None" else preferred_slot
    with col6:
        depends_on_input = st.text_input("Depends on (task name)", value="").title().strip()
        existing_task_names = [t.name for t in selected_pet.tasks]
        if depends_on_input and depends_on_input not in existing_task_names:
            st.caption(f"⚠ No task named '{depends_on_input}' exists for this pet.")
        depends_on = depends_on_input or None

    if st.button("Add task"):
        try:
            selected_pet.add_task(Task(
                name=task_title,
                duration=duration,
                priority=priority,
                frequency=frequency,
                preferred_slot=preferred_slot,
                depends_on=depends_on,
            ))
            st.rerun()
        except ValueError as e:
            st.error(str(e))

    incomplete_tasks = [t for t in selected_pet.tasks if not t.completed]
    if incomplete_tasks:
        st.markdown("**Mark task as completed**")
        col_done1, col_done2 = st.columns(2)
        with col_done1:
            task_to_complete = st.selectbox(
                "Select task",
                [t.name for t in incomplete_tasks],
                key="complete_task_select",
            )
        with col_done2:
            st.write("")  # vertical alignment spacer
            st.write("")
            if st.button("Mark completed"):
                try:
                    scheduler = Scheduler(owner=st.session_state.owner)
                    scheduler.complete_task(selected_pet_name, task_to_complete)
                    st.success(f"'{task_to_complete}' marked as completed.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
else:
    st.info("Add a pet first to manage tasks.")


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

st.divider()

st.subheader("Build Schedule")

selected_slot = st.selectbox("Time slot", ["morning", "afternoon", "evening"])

if st.button("Generate schedule"):
    if not st.session_state.owner.pets:
        st.warning("Add at least one pet before generating a schedule.")
    elif not any(p.tasks for p in st.session_state.owner.pets):
        st.warning("Add at least one task before generating a schedule.")
    elif not st.session_state.owner.time_available:
        st.warning("Add at least one availability window before generating a schedule.")
    else:
        schedule = Scheduler(owner=st.session_state.owner).create_schedule(
            current_slot=selected_slot
        )
        _render_schedule(schedule, st.session_state.owner, selected_slot)
