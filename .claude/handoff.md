# Handoff — 2026-05-07

## Summary
- Built a full multi-event campus event planning app in `app.py` from scratch
- App manages Catering, Facilities & Service Requests (FMD), Parking (UPD), UACE, and Billing checklists
- Catering and Parking are now opt-in per event (Yes/No radio buttons unlock the tab + checklist)
- Outdoor Festival event type unlocks a dedicated ⛺ Outdoor tab (rain plan, backup venue, etc.)
- Sidebar replaced dropdown with event cards showing live progress bars; past events go to a collapsible Archives section
- Event details (name, date, venue, attendance, type) are editable in-app via an expander
- Applied a pastel sunset color palette (lavender → blush → peach sidebar; warm cream main background) with Montserrat font
- All main content text set to dark terracotta (#6B3020) for readability on light pastel background
- Checklist items trimmed and refined across Catering, FMD, UACE, and Parking per user feedback
- Saved a git checkpoint at commit `1d5ae7a`

## Current State
- **Branch:** main (1 commit ahead of origin, plus uncommitted changes to `app.py` and `data_ai/events.csv`)
- **Server:** Streamlit running on port 8501
- **App URL:** https://orange-journey-5vq59rgvjj9qf7q9r-8501.app.github.dev
- **Data files:** `data_ai/events.csv` and `data_ai/checklist_items.csv` exist with live data
- **Last checkpoint tag:** `checkpoint` → commit `1d5ae7a`

## Next Steps
- Add more outdoor checklist items beyond the rain plan (user said "for now" — more to come)
- Consider adding a print/export view so planners can share a checklist summary (PDF or email)
- Potentially add a deadline/due-date field per checklist item
- User may want to add more event types or further refine checklist items per tab
- Push latest changes to GitHub origin when ready

## Key Decisions
- **Catering & Parking are opt-in:** Only shown when planner explicitly answers Yes — keeps the interface clean for events that don't need them
- **Facilities, UACE, Billing always visible:** These were decided to be required for all campus events
- **Checklist items stored per-event in CSV:** `data_ai/checklist_items.csv` uses event_id as foreign key; new events get a fresh copy of the template
- **On-demand checklist creation:** `add_category_checklist()` only adds items if that category doesn't already exist for the event — safe to call repeatedly
- **Outdoor items skip by default:** `create_event_checklist()` skips Outdoor and the opt-in categories (Catering, Parking); they are added via `add_category_checklist()` when unlocked
- **Session state for selected event:** `st.session_state.selected_event_id` tracks the active event across reruns instead of a dropdown

## Watchouts
- **Existing events in CSV won't get new checklist items** if DEFAULT_CHECKLIST is updated — only new events get the latest template. To update existing events, the user would need to delete and recreate them, or a migration function would need to be written.
- **`catering_enabled` / `parking_enabled` stored as string "True"/"False"/""** in CSV — the helpers `is_enabled()` and `is_answered()` handle the conversion. Don't compare directly with Python booleans.
- **Streamlit port 8501 may already be in use** on session resume — use `fuser -k 8501/tcp` before restarting.
- **CSS selectors may need updating** if Streamlit is upgraded — the pastel theme relies on internal `data-testid` attributes that can change between versions.
- **Data files are committed** in the checkpoint — if the user clears their test data (`data_ai/` CSVs), they'll need to recreate events from scratch.
