import streamlit as st
import pandas as pd
import os
from datetime import date
import uuid

st.set_page_config(page_title="Campus Event Planner", page_icon="🎓", layout="wide")

EVENTS_FILE = "data_ai/events.csv"
CHECKLIST_FILE = "data_ai/checklist_items.csv"

CATEGORIES = [
    "Catering",
    "Facilities & Service Requests",
    "Parking",
    "UACE",
    "Billing",
    "Outdoor",
]

EVENT_TYPES = [
    "Conference",
    "Workshop",
    "Ceremony",
    "Reception",
    "Meeting",
    "Fundraiser",
    "Outdoor Festival",
    "Other",
]

DEFAULT_CHECKLIST = [
    # ── Catering ──────────────────────────────────────────────────────────────
    {"category": "Catering", "item": "Submit catering request form", "required": True},
    {"category": "Catering", "item": "Confirm guest headcount with caterer", "required": True},
    {"category": "Catering", "item": "Confirm guest dietary and allergy accommodations", "required": True},
    {"category": "Catering", "item": "Confirm delivery time and setup location", "required": True},
    {"category": "Catering", "item": "Send final headcount to caterer (10 business days before)", "required": True},
    # Linens
    {"category": "Catering", "item": "Order linens if needed", "required": False},
    # ── Facilities & Service Requests (FMD) ───────────────────────────────────
    {"category": "Facilities & Service Requests", "item": "Request room setup including layout (tables, chairs)", "required": True},
    {"category": "Facilities & Service Requests", "item": "Confirm load-in and setup time with facilities", "required": True},
    {"category": "Facilities & Service Requests", "item": "Submit custodial services request", "required": True},
    {"category": "Facilities & Service Requests", "item": "Request post-event room breakdown and cleanup", "required": True},
    {"category": "Facilities & Service Requests", "item": "Confirm HVAC settings for event", "required": False},
    {"category": "Facilities & Service Requests", "item": "Request extension cords and power strips (for outdoor events)", "required": False},
    {"category": "Facilities & Service Requests", "item": "Submit service request for landscaping and pest control (for outdoor events)", "required": False},
    # ── Parking ───────────────────────────────────────────────────────────────
    {"category": "Parking", "item": "Reserve parking lot or designated section", "required": True},
    {"category": "Parking", "item": "Request guest parking permits", "required": True},
    {"category": "Parking", "item": "Arrange ADA accessible parking spaces", "required": True},
    {"category": "Parking", "item": "Coordinate with campus parking services office (UPD)", "required": True},
    {"category": "Parking", "item": "Get parking confirmation number", "required": True},
    {"category": "Parking", "item": "Send parking instructions and map to attendees", "required": True},
    {"category": "Parking", "item": "Request parking signage for event", "required": False},
    {"category": "Parking", "item": "Arrange shuttle service if needed", "required": False},
    {"category": "Parking", "item": "Request traffic control for large events", "required": False},
    {"category": "Parking", "item": "Confirm parking attendant coverage", "required": False},
    # ── UACE ──────────────────────────────────────────────────────────────────
    {"category": "UACE", "item": "Submit event request to University Affairs Ceremonies and Events (UACE)", "required": True},
    {"category": "UACE", "item": "Reserve room through 25Live", "required": True},
    {"category": "UACE", "item": "Meet with Event Professional to review event logistics", "required": True},
    {"category": "UACE", "item": "Confirm event-day point of contact", "required": True},
    {"category": "UACE", "item": "Review event run-of-show with UACE coordinator", "required": True},
    {"category": "UACE", "item": "Confirm event timeline and schedule with UACE", "required": True},
    {"category": "UACE", "item": "Request AV equipment (projector, microphone, screen)", "required": False},
    {"category": "UACE", "item": "Confirm ceremonial equipment needs (stage, podium, banners)", "required": False},
    {"category": "UACE", "item": "Coordinate VIP or dignitary arrangements with UACE", "required": False},
    {"category": "UACE", "item": "Review campus protocols and event procedures with UACE", "required": True},
    {"category": "UACE", "item": "Get UACE event approval and confirmation", "required": True},
    # ── Outdoor (Outdoor Festival only) ───────────────────────────────────────
    {"category": "Outdoor", "item": "Develop and document rain / inclement weather plan", "required": True},
    {"category": "Outdoor", "item": "Identify indoor backup or covered venue", "required": True},
    {"category": "Outdoor", "item": "Set weather cancellation threshold and decision timeline", "required": True},
    {"category": "Outdoor", "item": "Communicate rain plan to all vendors, staff, and attendees", "required": True},
    {"category": "Outdoor", "item": "Monitor weather forecast in the days leading up to event", "required": True},
    {"category": "Outdoor", "item": "Confirm tent or canopy rentals if needed", "required": False},
    {"category": "Outdoor", "item": "Arrange generator or outdoor power source", "required": False},
    {"category": "Outdoor", "item": "Confirm outdoor lighting plan", "required": False},
    # ── Billing ───────────────────────────────────────────────────────────────
    {"category": "Billing", "item": "Request cost estimate from Facilities Management (FMD)", "required": True},
    {"category": "Billing", "item": "Receive and review FMD estimate", "required": True},
    {"category": "Billing", "item": "Request cost estimate from Catering vendor", "required": True},
    {"category": "Billing", "item": "Receive and review Catering estimate", "required": True},
    {"category": "Billing", "item": "Request cost estimate from University Police / Parking (UPD)", "required": True},
    {"category": "Billing", "item": "Receive and review UPD estimate", "required": True},
    {"category": "Billing", "item": "Request cost estimate from UACE", "required": True},
    {"category": "Billing", "item": "Receive and review UACE estimate", "required": True},
    {"category": "Billing", "item": "Confirm funding source and account number", "required": True},
    {"category": "Billing", "item": "Submit budget approval for event expenses", "required": True},
    {"category": "Billing", "item": "Collect final invoices from all vendors", "required": True},
    {"category": "Billing", "item": "Submit invoices for payment processing", "required": True},
]


def load_events():
    if os.path.exists(EVENTS_FILE):
        return pd.read_csv(EVENTS_FILE)
    return pd.DataFrame(columns=["event_id", "event_name", "event_date", "location", "expected_attendance", "event_type", "created_date"])


def save_events(df):
    os.makedirs("data_ai", exist_ok=True)
    df.to_csv(EVENTS_FILE, index=False)


def load_checklist():
    if os.path.exists(CHECKLIST_FILE):
        return pd.read_csv(CHECKLIST_FILE)
    return pd.DataFrame(columns=["checklist_id", "event_id", "category", "item", "status", "notes", "required"])


def save_checklist(df):
    os.makedirs("data_ai", exist_ok=True)
    df.to_csv(CHECKLIST_FILE, index=False)


def create_event_checklist(event_id, event_type=""):
    checklist_df = load_checklist()
    new_items = []
    for template_item in DEFAULT_CHECKLIST:
        if template_item["category"] == "Outdoor" and event_type != "Outdoor Festival":
            continue
        new_items.append({
            "checklist_id": str(uuid.uuid4()),
            "event_id": event_id,
            "category": template_item["category"],
            "item": template_item["item"],
            "status": "Pending",
            "notes": "",
            "required": template_item["required"],
        })
    updated = pd.concat([checklist_df, pd.DataFrame(new_items)], ignore_index=True)
    save_checklist(updated)


def add_outdoor_checklist(event_id):
    """Add outdoor items to an existing event that was switched to Outdoor Festival."""
    checklist_df = load_checklist()
    existing = checklist_df[(checklist_df["event_id"] == event_id) & (checklist_df["category"] == "Outdoor")]
    if len(existing) > 0:
        return  # already has outdoor items
    new_items = []
    for template_item in DEFAULT_CHECKLIST:
        if template_item["category"] == "Outdoor":
            new_items.append({
                "checklist_id": str(uuid.uuid4()),
                "event_id": event_id,
                "category": "Outdoor",
                "item": template_item["item"],
                "status": "Pending",
                "notes": "",
                "required": template_item["required"],
            })
    updated = pd.concat([checklist_df, pd.DataFrame(new_items)], ignore_index=True)
    save_checklist(updated)


def get_completion_stats(event_id, checklist_df):
    event_items = checklist_df[checklist_df["event_id"] == event_id]
    if len(event_items) == 0:
        return {}
    stats = {}
    for cat in CATEGORIES:
        cat_items = event_items[event_items["category"] == cat]
        completed = len(cat_items[cat_items["status"] == "Completed"])
        total = len(cat_items)
        stats[cat] = {"completed": completed, "total": total, "pct": completed / total if total > 0 else 0}
    total_completed = len(event_items[event_items["status"] == "Completed"])
    stats["Overall"] = {
        "completed": total_completed,
        "total": len(event_items),
        "pct": total_completed / len(event_items),
    }
    return stats


def render_checklist_tab(category, event_id, checklist_df):
    cat_items = checklist_df[
        (checklist_df["event_id"] == event_id) & (checklist_df["category"] == category)
    ].copy()

    if len(cat_items) == 0:
        st.info("No items found for this category.")
        return

    _, filter_col = st.columns([3, 1])
    show_filter = filter_col.selectbox(
        "Show", ["All", "Pending", "In Progress", "Completed"], key=f"filter_{category}"
    )
    display_items = cat_items if show_filter == "All" else cat_items[cat_items["status"] == show_filter]

    st.markdown("---")

    STATUS_EMOJI = {"Pending": "🔴", "In Progress": "🟡", "Completed": "🟢"}
    STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]

    for _, row in display_items.iterrows():
        c1, c2, c3 = st.columns([3, 1.5, 2.5])

        with c1:
            star = "⭐ " if row["required"] else ""
            st.markdown(f"**{star}{row['item']}**")
            if row["required"]:
                st.caption("Required")

        with c2:
            current_status = row["status"] if row["status"] in STATUS_OPTIONS else "Pending"
            new_status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(current_status),
                key=f"status_{row['checklist_id']}",
                label_visibility="collapsed",
            )
            st.caption(STATUS_EMOJI.get(new_status, "⚪") + " " + new_status)
            if new_status != row["status"]:
                checklist_df.loc[checklist_df["checklist_id"] == row["checklist_id"], "status"] = new_status
                save_checklist(checklist_df)
                st.rerun()

        with c3:
            current_notes = row["notes"] if pd.notna(row["notes"]) else ""
            new_notes = st.text_input(
                "Notes",
                value=current_notes,
                placeholder="Add a note...",
                key=f"notes_{row['checklist_id']}",
                label_visibility="collapsed",
            )
            if new_notes != current_notes:
                checklist_df.loc[checklist_df["checklist_id"] == row["checklist_id"], "notes"] = new_notes
                save_checklist(checklist_df)

        st.markdown("---")

    with st.expander("➕ Add a custom checklist item"):
        with st.form(f"add_item_{category}", clear_on_submit=True):
            new_item_name = st.text_input("Item description")
            new_item_required = st.checkbox("Mark as required")
            add_submitted = st.form_submit_button("Add Item")
            if add_submitted and new_item_name.strip():
                fresh_df = load_checklist()
                new_row = pd.DataFrame([{
                    "checklist_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "category": category,
                    "item": new_item_name.strip(),
                    "status": "Pending",
                    "notes": "",
                    "required": new_item_required,
                }])
                fresh_df = pd.concat([fresh_df, new_row], ignore_index=True)
                save_checklist(fresh_df)
                st.success("Item added!")
                st.rerun()


# ── Session State ──────────────────────────────────────────────────────────────
if "selected_event_id" not in st.session_state:
    st.session_state.selected_event_id = None

# ── App Shell ──────────────────────────────────────────────────────────────────
st.title("🎓 Campus Event Planning Hub")
st.markdown("Track catering, facilities, parking, UACE, and billing for all your campus events.")

st.markdown("""
<style>
div[data-testid="metric-container"] { background: #f8f9fa; border-radius: 10px; padding: 12px; }
div[data-testid="stProgress"] > div > div { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

events_df = load_events()
checklist_df = load_checklist()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 My Events")

    if len(events_df) > 0:
        checklist_df_sidebar = load_checklist()
        today_date = date.today()
        events_df["_date_parsed"] = pd.to_datetime(events_df["event_date"]).dt.date
        upcoming_df = events_df[events_df["_date_parsed"] >= today_date].sort_values("_date_parsed")
        past_df = events_df[events_df["_date_parsed"] < today_date].sort_values("_date_parsed", ascending=False)

        # Default selection to first upcoming event on first load
        if st.session_state.selected_event_id is None:
            if len(upcoming_df) > 0:
                st.session_state.selected_event_id = upcoming_df.iloc[0]["event_id"]
            elif len(past_df) > 0:
                st.session_state.selected_event_id = past_df.iloc[0]["event_id"]

        def render_event_card(ev, checklist_df_sidebar):
            s = get_completion_stats(ev["event_id"], checklist_df_sidebar)
            pct = int(s["Overall"]["pct"] * 100) if s else 0
            badge = "🟢" if pct == 100 else ("🟡" if pct >= 50 else "🔴")
            is_selected = st.session_state.selected_event_id == ev["event_id"]
            st.markdown(f"**{ev['event_name']}**")
            st.caption(f"📅 {ev['event_date']}  ·  {ev['event_type']}")
            st.progress(pct / 100, text=f"{badge} {pct}% complete")
            if st.button(
                "✓ Viewing" if is_selected else "View →",
                key=f"sel_{ev['event_id']}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state.selected_event_id = ev["event_id"]
                st.rerun()
            st.markdown("---")

        # Upcoming events
        if len(upcoming_df) > 0:
            st.markdown("**Upcoming Events**")
            for _, ev in upcoming_df.iterrows():
                render_event_card(ev, checklist_df_sidebar)
        else:
            st.info("No upcoming events.")

        # Archives
        if len(past_df) > 0:
            with st.expander(f"🗂️ Archives ({len(past_df)} past event{'s' if len(past_df) != 1 else ''})"):
                for _, ev in past_df.iterrows():
                    render_event_card(ev, checklist_df_sidebar)
    else:
        st.info("No events yet. Create your first event below!")

    st.divider()
    st.subheader("➕ Create New Event")

    with st.form("new_event_form", clear_on_submit=True):
        new_name = st.text_input("Event Name *")
        new_date = st.date_input("Event Date *", min_value=date.today())
        new_location = st.text_input("Location / Venue *")
        new_attendance = st.number_input("Expected Attendance *", min_value=1, value=50)
        new_type = st.selectbox("Event Type", EVENT_TYPES)
        form_submitted = st.form_submit_button("Create Event", use_container_width=True, type="primary")

        if form_submitted:
            if not new_name.strip() or not new_location.strip():
                st.error("Event name and location are required.")
            elif new_name.strip() in events_df["event_name"].tolist():
                st.error("An event with this name already exists.")
            else:
                event_id = str(uuid.uuid4())
                new_row = pd.DataFrame([{
                    "event_id": event_id,
                    "event_name": new_name.strip(),
                    "event_date": str(new_date),
                    "location": new_location.strip(),
                    "expected_attendance": int(new_attendance),
                    "event_type": new_type,
                    "created_date": str(date.today()),
                }])
                events_df = pd.concat([events_df, new_row], ignore_index=True)
                save_events(events_df)
                create_event_checklist(event_id, new_type)
                st.success(f"'{new_name.strip()}' created!")
                st.rerun()

# ── Main Content ───────────────────────────────────────────────────────────────
if len(events_df) == 0 or st.session_state.selected_event_id is None:
    st.info("👈 Create your first event using the sidebar to get started!")
    st.stop()

if st.session_state.selected_event_id not in events_df["event_id"].values:
    st.session_state.selected_event_id = None
    st.rerun()

selected_event = events_df[events_df["event_id"] == st.session_state.selected_event_id].iloc[0]
event_id = selected_event["event_id"]
checklist_df = load_checklist()

# Event summary bar
col1, col2, col3, col4 = st.columns(4)
col1.metric("Event", selected_event["event_name"])
col2.metric("Date", selected_event["event_date"])
col3.metric("Venue", selected_event["location"])
col4.metric("Attendance", selected_event["expected_attendance"])

with st.expander("✏️ Edit Event Details"):
    with st.form("edit_event_form"):
        edit_name = st.text_input("Event Name", value=selected_event["event_name"])
        edit_date = st.date_input("Event Date", value=pd.to_datetime(selected_event["event_date"]).date())
        edit_location = st.text_input("Location / Venue", value=selected_event["location"])
        edit_attendance = st.number_input("Expected Attendance", min_value=1, value=int(selected_event["expected_attendance"]))
        edit_type = st.selectbox(
            "Event Type",
            EVENT_TYPES,
            index=EVENT_TYPES.index(selected_event["event_type"]) if selected_event["event_type"] in EVENT_TYPES else 0,
        )
        save_edits = st.form_submit_button("Save Changes", type="primary")
        if save_edits:
            if not edit_name.strip() or not edit_location.strip():
                st.error("Event name and location are required.")
            elif edit_name.strip() != selected_event["event_name"] and edit_name.strip() in events_df["event_name"].tolist():
                st.error("Another event already has that name.")
            else:
                events_df.loc[events_df["event_id"] == event_id, "event_name"] = edit_name.strip()
                events_df.loc[events_df["event_id"] == event_id, "event_date"] = str(edit_date)
                events_df.loc[events_df["event_id"] == event_id, "location"] = edit_location.strip()
                events_df.loc[events_df["event_id"] == event_id, "expected_attendance"] = int(edit_attendance)
                events_df.loc[events_df["event_id"] == event_id, "event_type"] = edit_type
                save_events(events_df)
                if edit_type == "Outdoor Festival":
                    add_outdoor_checklist(event_id)
                st.success("Event details updated!")
                st.rerun()

st.divider()

# Progress overview
stats = get_completion_stats(event_id, checklist_df)
if stats:
    st.subheader("📊 Booking Progress")

    icons = {
        "Overall": "🎯",
        "Catering": "🍽️",
        "Facilities & Service Requests": "🏛️",
        "Parking": "🚗",
        "UACE": "🎓",
        "Billing": "💰",
        "Outdoor": "⛺",
    }
    short = {
        "Overall": "Overall",
        "Catering": "Catering",
        "Facilities & Service Requests": "Facilities",
        "Parking": "Parking",
        "UACE": "UACE",
        "Billing": "Billing",
        "Outdoor": "Outdoor",
    }

    # Overall on its own row
    ov = stats["Overall"]
    ov_pct = int(ov["pct"] * 100)
    ov_badge = "🟢" if ov_pct == 100 else ("🟡" if ov_pct >= 50 else "🔴")
    st.markdown(f"#### {ov_badge} Overall Completion: {ov['completed']} / {ov['total']} items ({ov_pct}%)")
    st.progress(ov["pct"])
    st.markdown("")

    is_outdoor = selected_event["event_type"] == "Outdoor Festival"
    cat_order = ["Catering", "Facilities & Service Requests", "Parking", "UACE", "Billing"]
    if is_outdoor:
        cat_order.append("Outdoor")
    prog_cols = st.columns(len(cat_order))
    for i, cat in enumerate(cat_order):
        s = stats.get(cat, {"completed": 0, "total": 0, "pct": 0})
        with prog_cols[i]:
            st.metric(f"{icons[cat]} {short[cat]}", f"{s['completed']} / {s['total']}")
            st.progress(s["pct"])

st.divider()

# ── Checklist Tabs ─────────────────────────────────────────────────────────────
is_outdoor = selected_event["event_type"] == "Outdoor Festival"
tab_labels = ["🍽️ Catering", "🏛️ Facilities & Service Requests", "🚗 Parking", "🎓 UACE", "💰 Billing"]
if is_outdoor:
    tab_labels.append("⛺ Outdoor")

tabs = st.tabs(tab_labels)

with tabs[0]:
    st.markdown("### 🍽️ Catering")
    render_checklist_tab("Catering", event_id, checklist_df)

with tabs[1]:
    st.markdown("### 🏛️ Facilities & Service Requests (FMD)")
    render_checklist_tab("Facilities & Service Requests", event_id, checklist_df)

with tabs[2]:
    st.markdown("### 🚗 Parking (UPD)")
    render_checklist_tab("Parking", event_id, checklist_df)

with tabs[3]:
    st.markdown("### 🎓 University Affairs Ceremonies and Events (UACE)")
    render_checklist_tab("UACE", event_id, checklist_df)

with tabs[4]:
    st.markdown("### 💰 Billing & Estimates")
    st.info("Track cost estimates received from each department. Mark as **Completed** once you have a final signed estimate.")
    render_checklist_tab("Billing", event_id, checklist_df)

if is_outdoor:
    with tabs[5]:
        st.markdown("### ⛺ Outdoor Planning")
        st.info("These items apply because this event is an **Outdoor Festival**. Complete the rain plan early so all vendors are aligned.")
        render_checklist_tab("Outdoor", event_id, checklist_df)

st.divider()

with st.expander("⚠️ Danger Zone — Delete This Event"):
    st.warning(f"This will permanently delete **{selected_event['event_name']}** and all its checklist data.")
    if st.button("🗑️ Delete Event", type="secondary"):
        events_df = events_df[events_df["event_id"] != event_id]
        checklist_df = checklist_df[checklist_df["event_id"] != event_id]
        save_events(events_df)
        save_checklist(checklist_df)
        st.session_state.selected_event_id = None
        st.rerun()
