import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
import uuid

st.set_page_config(page_title="Campus Event Planner", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

EVENTS_FILE = "data_ai/events.csv"
CHECKLIST_FILE = "data_ai/checklist_items.csv"

CATEGORIES = [
    "Catering",
    "Facilities & Service Requests",
    "Parking",
    "Campus Venue",
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
    {"category": "Catering", "item": "Submit catering order", "required": True},
    {"category": "Catering", "item": "Confirm guest headcount with caterer", "required": True},
    {"category": "Catering", "item": "Confirm guest dietary and allergy accommodations", "required": True},
    {"category": "Catering", "item": "Confirm delivery time and setup location", "required": True},
    # Linens
    {"category": "Catering", "item": "Order linens if needed", "required": False},
    # ── Facilities & Service Requests (FMD) ───────────────────────────────────
    {"category": "Facilities & Service Requests", "item": "Request room setup with a layout (tables, chairs), and equipment totals listed", "required": True},
    {"category": "Facilities & Service Requests", "item": "Confirm load-in and setup time with facilities", "required": True},
    {"category": "Facilities & Service Requests", "item": "Submit custodial services request", "required": True},
    {"category": "Facilities & Service Requests", "item": "Confirm HVAC settings for event", "required": False},
    # ── Parking ───────────────────────────────────────────────────────────────
    {"category": "Parking", "item": "Reserve parking stalls through UPD", "required": True},
    {"category": "Parking", "item": "Request guest parking permits", "required": True},
    {"category": "Parking", "item": "Request parking signage for event", "required": False},
    {"category": "Parking", "item": "Arrange shuttle service if needed", "required": False},
    {"category": "Parking", "item": "Request traffic control for large events", "required": False},
    {"category": "Parking", "item": "Confirm parking attendant coverage", "required": False},
    # ── Campus Venue ──────────────────────────────────────────────────────────
    {"category": "Campus Venue", "item": "Reserve room through 25Live", "required": True},
    {"category": "Campus Venue", "item": "Receive venue approval and confirmation from event professional", "required": True},
    {"category": "Campus Venue", "item": "Meet with Event Professional to review event logistics", "required": True},
    {"category": "Campus Venue", "item": "Confirm event-day point of contact", "required": True},
    {"category": "Campus Venue", "item": "Review event run-of-show", "required": True},
    {"category": "Campus Venue", "item": "Request AV equipment (projector, microphone, screen)", "required": False},
    {"category": "Campus Venue", "item": "Review campus protocols and event procedures", "required": True},
    # ── Outdoor (Outdoor Festival only) ───────────────────────────────────────
    {"category": "Outdoor", "item": "Develop and document rain / inclement weather plan", "required": True},
    {"category": "Outdoor", "item": "Identify indoor backup or covered venue", "required": True},
    {"category": "Outdoor", "item": "Set weather cancellation threshold and decision timeline", "required": True},
    {"category": "Outdoor", "item": "Communicate rain plan to all vendors, staff, and attendees", "required": True},
    {"category": "Outdoor", "item": "Monitor weather forecast in the days leading up to event", "required": True},
    {"category": "Outdoor", "item": "Confirm tent or canopy rentals if needed", "required": False},
    {"category": "Outdoor", "item": "Arrange generator or outdoor power source", "required": False},
    {"category": "Outdoor", "item": "Confirm outdoor lighting plan", "required": False},
    {"category": "Outdoor", "item": "Request extension cords and power strips through FMD", "required": False},
    {"category": "Outdoor", "item": "Submit service request for landscaping through FMD", "required": False},
    {"category": "Outdoor", "item": "Submit service request for pest control through FMD", "required": False},
    # ── Billing ───────────────────────────────────────────────────────────────
    {"category": "Billing", "item": "Confirm funding source and account number", "required": True},
    {"category": "Billing", "item": "Receive and review FMD estimate", "required": True},
    {"category": "Billing", "item": "Receive and review Catering estimate", "required": True},
    {"category": "Billing", "item": "Receive and review UPD estimate", "required": True},
    {"category": "Billing", "item": "Receive and review Campus Venue estimate", "required": True},
    {"category": "Billing", "item": "Collect final invoice from FMD", "required": True},
    {"category": "Billing", "item": "Collect final invoice from Catering", "required": True},
    {"category": "Billing", "item": "Collect final invoice from Parking / UPD", "required": True},
    {"category": "Billing", "item": "Collect final invoice from Campus Venue", "required": True},
]


def load_events():
    if os.path.exists(EVENTS_FILE):
        df = pd.read_csv(EVENTS_FILE)
        for col in ["catering_enabled", "parking_enabled", "rain_plan_enabled"]:
            if col not in df.columns:
                df[col] = ""
            df[col] = df[col].fillna("").astype(str)
        return df
    return pd.DataFrame(columns=["event_id", "event_name", "event_date", "location", "expected_attendance", "event_type", "created_date", "catering_enabled", "parking_enabled", "rain_plan_enabled"])


def is_enabled(val):
    return str(val).strip().lower() == "true"


def is_answered(val):
    return str(val).strip().lower() in ["true", "false"]


def add_business_days(event_date_str, n):
    try:
        d = pd.to_datetime(event_date_str).date()
    except Exception:
        return None
    count = 0
    while count < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            count += 1
    return d


def subtract_business_days(event_date_str, n):
    try:
        d = pd.to_datetime(event_date_str).date()
    except Exception:
        return None
    count = 0
    while count < n:
        d -= timedelta(days=1)
        if d.weekday() < 5:
            count += 1
    return d


def build_timeline(event_date_str, attendance, catering_on):
    today = date.today()
    rows = []

    def add_before(task, dept, days):
        d = subtract_business_days(event_date_str, days)
        if d is None:
            return
        status = "⚠️ Past Due" if d < today else ("🔴 Due Today" if d == today else "🟢 Upcoming")
        rows.append({"_date": d, "Phase": "Before Event", "Due Date": d.strftime("%a, %b %d %Y"), "Task": task, "Department": dept, "Status": status})

    def add_after(task, dept, days):
        d = add_business_days(event_date_str, days)
        if d is None:
            return
        status = "⚠️ Past Due" if d < today else ("🔴 Due Today" if d == today else "🟢 Upcoming")
        rows.append({"_date": d, "Phase": "After Event", "Due Date": d.strftime("%a, %b %d %Y"), "Task": task, "Department": dept, "Status": status})

    add_before("Reserve room / venue", "Facilities", 20)
    add_before("Request AV equipment (projector, microphone, screen)", "Campus Venue", 10)
    if int(attendance) > 50:
        add_before("Submit complex layout (>50 guests)", "Facilities", 10)
    else:
        add_before("Submit simple layout (≤49 guests)", "Facilities", 5)
    if catering_on:
        add_before("Confirm guest dietary & allergy accommodations", "Catering", 5)
        add_before("Submit catering order", "Catering", 10)
        add_before("Confirm guest headcount with caterer", "Catering", 5)
        add_before("Confirm delivery time & setup location", "Catering", 5)
    add_after("Collect final invoice from FMD", "Billing", 20)
    add_after("Collect final invoice from Catering", "Billing", 20)
    add_after("Collect final invoice from Parking / UPD", "Billing", 20)
    add_after("Collect final invoice from Campus Venue", "Billing", 20)

    rows.sort(key=lambda x: x["_date"])
    for r in rows:
        del r["_date"]
    return rows


def save_events(df):
    os.makedirs("data_ai", exist_ok=True)
    df.to_csv(EVENTS_FILE, index=False)


def load_checklist():
    if os.path.exists(CHECKLIST_FILE):
        df = pd.read_csv(CHECKLIST_FILE)
        df["category"] = df["category"].replace({"UACE": "Campus Venue", "University Events Department": "Campus Venue", "Events Dept.": "Campus Venue"})
        # Remove outdoor-only items from non-outdoor events
        if os.path.exists(EVENTS_FILE):
            ev = pd.read_csv(EVENTS_FILE)
            non_outdoor_ids = ev[ev["event_type"] != "Outdoor Festival"]["event_id"].tolist()
            outdoor_keywords = ["extension cords", "landscaping", "pest control"]
            pattern = "|".join(outdoor_keywords)
            bad = (
                df["event_id"].isin(non_outdoor_ids) &
                df["item"].str.contains(pattern, case=False, na=False)
            )
            if bad.any():
                df = df[~bad]
                df.to_csv(CHECKLIST_FILE, index=False)
        return df
    return pd.DataFrame(columns=["checklist_id", "event_id", "category", "item", "status", "notes", "required"])


def save_checklist(df):
    os.makedirs("data_ai", exist_ok=True)
    df.to_csv(CHECKLIST_FILE, index=False)


def create_event_checklist(event_id, event_type=""):
    checklist_df = load_checklist()
    new_items = []
    on_demand = {"Catering", "Parking"}  # added only when planner says Yes
    for template_item in DEFAULT_CHECKLIST:
        if template_item["category"] in on_demand:
            continue
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


def add_category_checklist(event_id, category):
    """Add checklist items for a category if not already present."""
    checklist_df = load_checklist()
    existing = checklist_df[(checklist_df["event_id"] == event_id) & (checklist_df["category"] == category)]
    if len(existing) > 0:
        return
    new_items = []
    for template_item in DEFAULT_CHECKLIST:
        if template_item["category"] == category:
            new_items.append({
                "checklist_id": str(uuid.uuid4()),
                "event_id": event_id,
                "category": category,
                "item": template_item["item"],
                "status": "Pending",
                "notes": "",
                "required": template_item["required"],
            })
    if new_items:
        updated = pd.concat([checklist_df, pd.DataFrame(new_items)], ignore_index=True)
        save_checklist(updated)


def get_completion_stats(event_id, checklist_df):
    event_items = checklist_df[checklist_df["event_id"] == event_id]
    if len(event_items) == 0:
        return {}
    stats = {}
    for cat in CATEGORIES:
        cat_items = event_items[event_items["category"] == cat]
        if len(cat_items) == 0:
            continue
        completed = len(cat_items[cat_items["status"] == "Completed"])
        total = len(cat_items)
        stats[cat] = {"completed": completed, "total": total, "pct": completed / total}
    total_completed = len(event_items[event_items["status"] == "Completed"])
    stats["Overall"] = {
        "completed": total_completed,
        "total": len(event_items),
        "pct": total_completed / len(event_items),
    }
    return stats


STATUS_EMOJI = {"Pending": "🔴", "In Progress": "🟡", "Completed": "🟢", "Not Required": "⚫"}
STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]
STATUS_OPTIONS_WITH_NR = ["Pending", "In Progress", "Completed", "Not Required"]

OPTIONAL_STATUS_ITEMS = {
    "Order linens if needed",
    "Reserve parking stalls through UPD",
    "Request guest parking permits",
    "Request parking signage for event",
    "Arrange shuttle service if needed",
    "Request traffic control for large events",
    "Confirm parking attendant coverage",
}


CONTACTS = {
    "Catering": {
        "name": "Maria Lopez",
        "title": "Catering Coordinator",
        "phone": "(510) 555-0192",
        "email": "m.lopez@pioneercatering.edu",
        "website": "https://www.pioneercatering.edu",
        "menu": "https://www.pioneercatering.edu/menu",
    },
    "Facilities & Service Requests": {
        "name": "James Thornton",
        "title": "FMD Event Services Manager",
        "phone": "(510) 555-0247",
        "email": "j.thornton@pioneerfmd.edu",
        "website": "https://www.pioneerfmd.edu",
    },
    "Parking": {
        "name": "Officer Dana Kim",
        "title": "UPD Event Parking Coordinator",
        "phone": "(510) 555-0381",
        "email": "d.kim@pioneerupd.edu",
        "website": "https://www.pioneerupd.edu",
    },
    "Campus Venue": {
        "name": "Alex Rivera",
        "title": "Campus Venue Event Professional",
        "phone": "(510) 555-0134",
        "email": "a.rivera@pioneervenue.edu",
        "website": "https://www.pioneervenue.edu",
    },
}


def render_tab_progress(items_df):
    total = len(items_df)
    if total == 0:
        return
    completed = (items_df["status"] == "Completed").sum()
    not_required = (items_df["status"] == "Not Required").sum()
    counted = total - not_required
    pct = completed / counted if counted > 0 else 0
    badge = "🟢" if pct == 1.0 else ("🟡" if pct >= 0.5 else "🔴")
    st.markdown(f"{badge} **{completed} of {counted} items completed**")
    st.progress(pct)


def render_contact_card(category):
    contact = CONTACTS.get(category)
    if not contact:
        return
    with st.expander("📞 Contact Information", expanded=False):
        st.markdown(f"**{contact['name']}** — {contact['title']}")
        st.markdown(f"📱 {contact['phone']}  &nbsp;|&nbsp;  ✉️ [{contact['email']}](mailto:{contact['email']})")
        st.markdown(f"🌐 [{contact['website']}]({contact['website']})")
        if contact.get("menu"):
            st.markdown(f"🍽️ [View Menu]({contact['menu']})")


def render_item_row(row, checklist_df):
    c1, c2, c3 = st.columns([3, 1.5, 2.5])
    with c1:
        st.markdown(f"**{row['item']}**")
        if row["required"]:
            st.caption("Required")
    with c2:
        opts = STATUS_OPTIONS_WITH_NR if row["item"] in OPTIONAL_STATUS_ITEMS else STATUS_OPTIONS
        current_status = row["status"] if row["status"] in opts else "Pending"
        new_status = st.selectbox(
            "Status", opts,
            index=opts.index(current_status),
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
            "Notes", value=current_notes, placeholder="Add a note...",
            key=f"notes_{row['checklist_id']}",
            label_visibility="collapsed",
        )
        if new_notes != current_notes:
            checklist_df.loc[checklist_df["checklist_id"] == row["checklist_id"], "notes"] = new_notes
            save_checklist(checklist_df)
    st.markdown("---")


def render_checklist_tab(category, event_id, checklist_df):
    cat_items = checklist_df[
        (checklist_df["event_id"] == event_id) & (checklist_df["category"] == category)
    ].copy()

    if len(cat_items) == 0:
        st.info("No items found for this category.")
        return

    render_tab_progress(cat_items)
    _, filter_col = st.columns([3, 1])
    show_filter = filter_col.selectbox(
        "Show", ["All", "Pending", "In Progress", "Completed"], key=f"filter_{category}"
    )
    display_items = cat_items if show_filter == "All" else cat_items[cat_items["status"] == show_filter]

    st.markdown("---")

    for _, row in display_items.iterrows():
        render_item_row(row, checklist_df)

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


OUTDOOR_RAIN_ITEM = "Develop and document rain / inclement weather plan"
OUTDOOR_RAIN_SUB_ITEMS = [
    "Set weather cancellation threshold and decision timeline",
    "Monitor weather forecast in the days leading up to event",
    "Communicate rain plan to all vendors, staff, and attendees",
]

CV_MEETING_ITEM = "Meet with Event Professional to review event logistics"
CV_SUB_ITEMS = {
    "Confirm event-day point of contact",
    "Review event run-of-show",
    "Request AV equipment (projector, microphone, screen)",
    "Review campus protocols and event procedures",
}


def render_campus_venue_tab(event_id, checklist_df):
    cv_items = checklist_df[
        (checklist_df["event_id"] == event_id) & (checklist_df["category"] == "Campus Venue")
    ].copy()

    if len(cv_items) == 0:
        st.info("No items found for this category.")
        return

    render_tab_progress(cv_items)
    _, filter_col = st.columns([3, 1])
    show_filter = filter_col.selectbox(
        "Show", ["All", "Pending", "In Progress", "Completed"], key="filter_Campus Venue"
    )

    main_items = cv_items[~cv_items["item"].isin(CV_SUB_ITEMS)]
    sub_items = cv_items[cv_items["item"].isin(CV_SUB_ITEMS)]

    if show_filter != "All":
        main_items = main_items[main_items["status"] == show_filter]
        sub_items = sub_items[sub_items["status"] == show_filter]

    st.markdown("---")

    for _, row in main_items.iterrows():
        render_item_row(row, checklist_df)
        if row["item"] == CV_MEETING_ITEM:
            with st.expander("📋 Meeting agenda items", expanded=False):
                if len(sub_items) == 0:
                    st.caption("No items match the selected filter.")
                for _, sub_row in sub_items.iterrows():
                    render_item_row(sub_row, checklist_df)

    with st.expander("➕ Add a custom checklist item"):
        with st.form("add_item_Campus Venue", clear_on_submit=True):
            new_item_name = st.text_input("Item description")
            new_item_required = st.checkbox("Mark as required")
            add_submitted = st.form_submit_button("Add Item")
            if add_submitted and new_item_name.strip():
                fresh_df = load_checklist()
                new_row = pd.DataFrame([{
                    "checklist_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "category": "Campus Venue",
                    "item": new_item_name.strip(),
                    "status": "Pending",
                    "notes": "",
                    "required": new_item_required,
                }])
                fresh_df = pd.concat([fresh_df, new_row], ignore_index=True)
                save_checklist(fresh_df)
                st.success("Item added!")
                st.rerun()


def render_outdoor_tab(event_id, checklist_df, events_df, rain_plan_val, rain_plan_on):
    outdoor_items = checklist_df[
        (checklist_df["event_id"] == event_id) & (checklist_df["category"] == "Outdoor")
    ].copy()

    render_tab_progress(outdoor_items)

    # ── Rain plan yes/no question ──────────────────────────────────────────────
    rain_index = (0 if rain_plan_on else 1) if is_answered(rain_plan_val) else None
    rain_answer = st.radio(
        "Will you have a rain / inclement weather plan?",
        ["Yes", "No"],
        index=rain_index,
        horizontal=True,
        key="rain_plan_radio",
    )
    if rain_answer is not None:
        new_val = str(rain_answer == "Yes")
        if str(rain_plan_val) != new_val:
            events_df.loc[events_df["event_id"] == event_id, "rain_plan_enabled"] = new_val
            save_events(events_df)
            st.rerun()

    if rain_plan_on:
        sub_items_df = outdoor_items[outdoor_items["item"].isin(OUTDOOR_RAIN_SUB_ITEMS)]
        ordered_rows = [
            sub_items_df[sub_items_df["item"] == name].iloc[0]
            for name in OUTDOOR_RAIN_SUB_ITEMS
            if name in sub_items_df["item"].values
        ]
        sub_items_ordered = pd.DataFrame(ordered_rows) if ordered_rows else sub_items_df.iloc[0:0]
        with st.expander("🌧️ Rain plan details", expanded=True):
            for _, sub_row in sub_items_ordered.iterrows():
                render_item_row(sub_row, checklist_df)

    # ── Other outdoor items ────────────────────────────────────────────────────
    other_items = outdoor_items[
        ~outdoor_items["item"].isin(OUTDOOR_RAIN_SUB_ITEMS) &
        (outdoor_items["item"] != OUTDOOR_RAIN_ITEM)
    ]

    if len(other_items) == 0:
        pass
    else:
        _, filter_col = st.columns([3, 1])
        show_filter = filter_col.selectbox(
            "Show", ["All", "Pending", "In Progress", "Completed"], key="filter_Outdoor"
        )
        if show_filter != "All":
            other_items = other_items[other_items["status"] == show_filter]

        st.markdown("---")
        for _, row in other_items.iterrows():
            render_item_row(row, checklist_df)

    with st.expander("➕ Add a custom checklist item"):
        with st.form("add_item_Outdoor", clear_on_submit=True):
            new_item_name = st.text_input("Item description")
            new_item_required = st.checkbox("Mark as required")
            add_submitted = st.form_submit_button("Add Item")
            if add_submitted and new_item_name.strip():
                fresh_df = load_checklist()
                new_row = pd.DataFrame([{
                    "checklist_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "category": "Outdoor",
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
st.markdown("<h1 style='text-align: center;'>🎓 Campus Event Planning Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Plan ahead and never miss a deadline with our campus stakeholders.<br>Create a seamless planning experience for all!</p>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

/* ── Global Font ──────────────────────────────────────────────────── */
html, body, [class*="css"],
p, h1, h2, h3, h4, h5, h6, li, a,
button, input, textarea, select, option,
label, th, td, caption, figcaption,
[data-testid="stMarkdownContainer"],
[data-testid="stText"],
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"],
[data-baseweb="tab"],
[data-testid="stAppViewContainer"] div {
    font-family: 'Montserrat', sans-serif !important;
}
/* Restore icon fonts — Streamlit renders icons as spans with Material Symbols */
span[data-testid*="Icon"],
.material-icons, .material-symbols-rounded, .material-symbols-outlined,
[class*="stIcon"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}

/* ── Main App Background ─────────────────────────────────────────── */
.stApp {
    background: linear-gradient(160deg, #FFF4EE 0%, #FDE8E0 40%, #FDE8F2 100%) !important;
}

/* ── Sidebar — pastel lavender → blush → peach, dark text ────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #EDD8F8 0%, #F8D0E4 45%, #FAD8C0 80%, #FAE8B8 100%) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown {
    color: #4A1840 !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(74,24,64,0.2) !important;
}
/* Sidebar primary button = selected event */
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #E8A0B8, #F0C880) !important;
    color: #4A1840 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
}
/* Sidebar secondary button = unselected */
[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(255,255,255,0.45) !important;
    border: 1px solid rgba(74,24,64,0.25) !important;
    color: #4A1840 !important;
    border-radius: 8px !important;
}
/* Sidebar progress bar */
[data-testid="stSidebar"] .stProgress > div > div > div > div {
    background: linear-gradient(90deg, #E8A0B8, #F0C880) !important;
}
[data-testid="stSidebar"] .stProgress > div > div > div {
    background: rgba(74,24,64,0.12) !important;
}

/* ── Main Headers ────────────────────────────────────────────────── */
h1 { color: #C0607A !important; letter-spacing: -0.5px; }
h2 { color: #C87858 !important; }
h3 { color: #C88848 !important; }

/* ── Metric Cards ────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(232,160,184,0.2), rgba(240,200,128,0.2)) !important;
    border: 1px solid rgba(232,160,184,0.5) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}
[data-testid="stMetricLabel"] { color: #C0607A !important; font-weight: 600 !important; font-size: 0.8rem !important; }
[data-testid="stMetricValue"] { color: #4A1840 !important; font-weight: 700 !important; }

/* ── Progress Bars (main) ────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #E8A0B8, #F0B898, #F0C880) !important;
    border-radius: 8px !important;
}
.stProgress > div > div > div {
    background: rgba(232,160,184,0.2) !important;
    border-radius: 8px !important;
}

/* ── Primary Buttons ─────────────────────────────────────────────── */
button[kind="primary"] {
    background: linear-gradient(135deg, #E8A0B8, #D888A0) !important;
    border: none !important;
    color: #4A1840 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #D888A0, #C87090) !important;
}

/* ── Secondary Buttons ───────────────────────────────────────────── */
button[kind="secondary"] {
    border: 1.5px solid #E8A0B8 !important;
    color: #C0607A !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    background: rgba(255,255,255,0.6) !important;
}
button[kind="secondary"]:hover {
    background: rgba(232,160,184,0.15) !important;
}

/* ── Tabs ────────────────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0 !important;
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
[data-baseweb="tab"] {
    color: #C0607A !important;
    font-weight: 600 !important;
    border-radius: 8px 8px 0 0 !important;
    flex: 1 1 0 !important;
    text-align: center !important;
    justify-content: center !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: rgba(232,160,184,0.15) !important;
    border-bottom: 3px solid #E8A0B8 !important;
    color: #C0607A !important;
}

/* ── Expanders ───────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid rgba(232,160,184,0.45) !important;
    border-radius: 10px !important;
    background: rgba(255,248,244,0.85) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #C0607A !important;
}

/* ── Select / Input borders ──────────────────────────────────────── */
[data-baseweb="select"] > div {
    border-color: #E8A0B8 !important;
    border-radius: 8px !important;
    background: rgba(255,248,244,0.95) !important;
}
[data-baseweb="input"] > div {
    border-color: #E8A0B8 !important;
    border-radius: 8px !important;
    background: rgba(255,248,244,0.95) !important;
}
textarea {
    border-color: #E8A0B8 !important;
    border-radius: 8px !important;
}

/* ── Alert / Info boxes ──────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left: 4px solid #E8A0B8 !important;
}

/* ── Dividers ────────────────────────────────────────────────────── */
hr {
    border-color: rgba(232,160,184,0.35) !important;
}

/* ── Main Content Text — dark terracotta everywhere ──────────────── */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] div,
[data-testid="stAppViewContainer"] small,
[data-testid="stAppViewContainer"] caption,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
.stCaption,
.stSelectbox label,
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stCheckbox label,
.stRadio label,
.stForm label,
[data-testid="stWidgetLabel"],
[data-testid="stText"],
[data-testid="stCaptionContainer"] {
    color: #6B3020 !important;
}

/* Selectbox / input typed text */
[data-baseweb="select"] span,
[data-baseweb="input"] input,
textarea {
    color: #6B3020 !important;
}

/* ── Hide Streamlit built-in toolbar / keyboard shortcut badge ───── */
[data-testid="stToolbar"],
[data-testid="stAppToolbar"],
[data-testid="stToolbarActions"],
[data-testid="stToolbarActionButton"],
[data-testid="stToolbarActionButtonIcon"],
[data-testid="stToolbarActionButtonLabel"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stBottom"],
[data-testid="stAppDeployButton"],
#MainMenu,
footer {
    display: none !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ── Force sidebar always visible, hide collapse button ─────────── */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    transform: none !important;
    min-width: 244px !important;
    width: 244px !important;
    opacity: 1 !important;
    margin-left: 0 !important;
    left: 0 !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* ── Prevent bottom overlap ──────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    padding-bottom: 2rem !important;
}
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
            st.caption(f"📅 {pd.to_datetime(ev['event_date']).strftime('%m/%d/%Y')}  ·  {ev['event_type']}")
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
                    "catering_enabled": "",
                    "parking_enabled": "",
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
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Event", selected_event["event_name"])
col2.metric("Date", pd.to_datetime(selected_event["event_date"]).strftime("%m/%d/%Y"))
col3.metric("Venue", selected_event["location"])
col4.metric("Attendance", selected_event["expected_attendance"])
_days_left = (pd.to_datetime(selected_event["event_date"]).date() - date.today()).days
col5.metric("Days Until Event", _days_left if _days_left >= 0 else f"{abs(_days_left)} days ago")

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

catering_val = selected_event["catering_enabled"]
parking_val = selected_event["parking_enabled"]
rain_plan_val = selected_event["rain_plan_enabled"]
catering_on = is_enabled(catering_val)
parking_on = is_enabled(parking_val)
rain_plan_on = is_enabled(rain_plan_val)

# Progress overview
checklist_df = load_checklist()
stats = get_completion_stats(event_id, checklist_df)
if stats:
    st.subheader("📊 Booking Progress")
    ov = stats["Overall"]
    ov_pct = int(ov["pct"] * 100)
    ov_badge = "🟢" if ov_pct == 100 else ("🟡" if ov_pct >= 50 else "🔴")
    st.markdown(f"#### {ov_badge} Overall Completion: {ov['completed']} / {ov['total']} items ({ov_pct}%)")
    st.progress(ov["pct"])

st.divider()

# ── Timeline ───────────────────────────────────────────────────────────────────
st.subheader("📅 Deadline Timeline")
st.caption("Business days (Mon–Fri) calculated from your event date.")
timeline_rows = build_timeline(
    selected_event["event_date"],
    selected_event["expected_attendance"],
    catering_on,
)
if timeline_rows:
    tl_col, _ = st.columns([2, 5])
    with tl_col:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "🟢 Upcoming", "🔴 Due Today", "⚠️ Past Due"],
            key="timeline_filter",
            label_visibility="collapsed",
        )
    filtered = timeline_rows if status_filter == "All" else [r for r in timeline_rows if r["Status"] == status_filter]

    for phase in ["Before Event", "After Event"]:
        phase_rows = [r for r in filtered if r["Phase"] == phase]
        label = f"{'📋 Before Event' if phase == 'Before Event' else '📬 After Event'} — {len(phase_rows)} item{'s' if len(phase_rows) != 1 else ''}"
        with st.expander(label, expanded=(phase == "Before Event")):
            if phase_rows:
                for row in phase_rows:
                    cols = st.columns([2, 5, 3, 2])
                    cols[0].markdown(f"**{row['Due Date']}**")
                    cols[1].markdown(row["Task"])
                    cols[2].markdown(f"*{row['Department']}*")
                    cols[3].markdown(row["Status"])
                    st.divider()
            else:
                st.caption("No items match the selected filter.")
else:
    st.info("Set an event date to generate the timeline.")

st.divider()

# ── Checklist Tabs ─────────────────────────────────────────────────────────────
is_outdoor = selected_event["event_type"] == "Outdoor Festival"

tab_defs = [
    ("🍽️ Catering", "Catering"),
    ("🏛️ Facilities & Service Requests", "Facilities & Service Requests"),
    ("🚗 Parking", "Parking"),
    ("🎓 Campus Venue", "Campus Venue"),
    ("💰 Billing", "Billing"),
]
if is_outdoor:
    tab_defs.append(("⛺ Outdoor", "Outdoor"))

_event_checklist = checklist_df[checklist_df["event_id"] == event_id]
_pending_required = _event_checklist[
    (_event_checklist["required"] == True) &
    (_event_checklist["status"] == "Pending")
]
if len(_pending_required) > 0:
    st.warning(f"⚠️ You have **{len(_pending_required)} required item{'s' if len(_pending_required) != 1 else ''}** still marked as Pending.")

tabs = st.tabs([t[0] for t in tab_defs])

for tab, (label, category) in zip(tabs, tab_defs):
    with tab:
        if category == "Catering":
            render_contact_card("Catering")
            catering_index = (0 if catering_on else 1) if is_answered(catering_val) else None
            catering_answer = st.radio(
                "Will catering be offered?",
                ["Yes", "No"],
                index=catering_index,
                horizontal=True,
                key="catering_radio",
            )
            if catering_answer is not None:
                new_val = str(catering_answer == "Yes")
                if str(catering_val) != new_val:
                    events_df.loc[events_df["event_id"] == event_id, "catering_enabled"] = new_val
                    save_events(events_df)
                    if catering_answer == "Yes":
                        add_category_checklist(event_id, "Catering")
                    st.rerun()
            if catering_on:
                st.divider()
                render_checklist_tab("Catering", event_id, checklist_df)
        elif category == "Parking":
            render_contact_card("Parking")
            parking_index = (0 if parking_on else 1) if is_answered(parking_val) else None
            parking_answer = st.radio(
                "Will parking arrangements be needed?",
                ["Yes", "No"],
                index=parking_index,
                horizontal=True,
                key="parking_radio",
            )
            if parking_answer is not None:
                new_val = str(parking_answer == "Yes")
                if str(parking_val) != new_val:
                    events_df.loc[events_df["event_id"] == event_id, "parking_enabled"] = new_val
                    save_events(events_df)
                    if parking_answer == "Yes":
                        add_category_checklist(event_id, "Parking")
                    st.rerun()
            if parking_on:
                st.divider()
                parking_df = checklist_df.copy()
                if int(selected_event["expected_attendance"]) <= 100:
                    parking_df = parking_df[parking_df["item"] != "Request traffic control for large events"]
                render_checklist_tab("Parking", event_id, parking_df)
        elif category == "Facilities & Service Requests":
            st.markdown("### 🏛️ Facilities & Service Requests (FMD)")
            render_contact_card("Facilities & Service Requests")
            render_checklist_tab(category, event_id, checklist_df)
        elif category == "Campus Venue":
            st.markdown("### 🎓 Campus Venue")
            render_contact_card("Campus Venue")
            render_campus_venue_tab(event_id, checklist_df)
        elif category == "Billing":
            st.markdown("### 💰 Billing & Estimates")
            st.info("Track cost estimates from each department. Mark as **Completed** once you have a final signed estimate.")
            render_checklist_tab(category, event_id, checklist_df)
        elif category == "Outdoor":
            st.markdown("### ⛺ Outdoor Planning")
            st.info("Complete the rain plan early so all vendors are aligned.")
            render_outdoor_tab(event_id, checklist_df, events_df, rain_plan_val, rain_plan_on)

st.divider()

with st.expander("📄 Event Summary", expanded=False):
    st.markdown(f"### {selected_event['event_name']}")
    st.markdown(f"**Date:** {pd.to_datetime(selected_event['event_date']).strftime('%m/%d/%Y')}  &nbsp;|&nbsp;  **Venue:** {selected_event['location']}  &nbsp;|&nbsp;  **Attendance:** {selected_event['expected_attendance']}")
    st.markdown("---")
    _summary_df = checklist_df[checklist_df["event_id"] == event_id]
    for cat in _summary_df["category"].unique():
        cat_rows = _summary_df[_summary_df["category"] == cat]
        completed = (cat_rows["status"] == "Completed").sum()
        total = len(cat_rows)
        st.markdown(f"**{cat}** — {completed}/{total} completed")
        for _, r in cat_rows.iterrows():
            emoji = STATUS_EMOJI.get(r["status"], "⚪")
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{emoji} {r['item']}")
    st.markdown("---")
    _notes_rows = _summary_df[_summary_df["notes"].fillna("").astype(str).str.strip() != ""]
    notes_text = f"Event Summary — {selected_event['event_name']}\n"
    notes_text += f"Date: {pd.to_datetime(selected_event['event_date']).strftime('%m/%d/%Y')} | Venue: {selected_event['location']}\n\n"
    if len(_notes_rows) > 0:
        notes_text += "NOTES\n" + "="*40 + "\n"
        for _, r in _notes_rows.iterrows():
            notes_text += f"[{r['category']}] {r['item']}\n  → {r['notes']}\n\n"
    else:
        notes_text += "No notes recorded.\n"
    st.download_button(
        "⬇️ Export Notes as Text",
        data=notes_text,
        file_name=f"{selected_event['event_name'].replace(' ', '_')}_notes.txt",
        mime="text/plain",
    )

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

with st.expander("⚠️ Danger Zone — Delete This Event"):
    st.warning(f"This will permanently delete **{selected_event['event_name']}** and all its checklist data.")
    if st.button("🗑️ Delete Event", type="secondary"):
        events_df = events_df[events_df["event_id"] != event_id]
        checklist_df = checklist_df[checklist_df["event_id"] != event_id]
        save_events(events_df)
        save_checklist(checklist_df)
        st.session_state.selected_event_id = None
        st.rerun()
