# Handoff — 2026-05-08

## Summary
- Fixed icon rendering issue: removed `*` from font override (`* { font-family: Montserrat }`) which was breaking Streamlit's Material Icons, causing `_arrow_right` and `keyboard_double_arrow_right` to render as raw text
- Fixed sidebar disappearing: forced sidebar always visible via CSS (`transform: none`, `min-width: 244px`) and hid collapse/expand buttons — sidebar can no longer be collapsed (intentional to prevent it disappearing again)
- Made `Create Event` button match `✓ Viewing` button color by targeting `[data-testid="stFormSubmitButton"] button` in sidebar CSS
- Changed date display to MM/DD/YYYY format in metric card and sidebar event cards
- Added `initial_sidebar_state="expanded"` to `st.set_page_config()`
- Renamed "Events Dept." → "Campus Venue" throughout app, DEFAULT_CHECKLIST, CSS, timeline, billing, and CSV (with migration guard in `load_checklist()`)
- Removed outdoor-only items (extension cords, landscaping, pest control) from non-outdoor events in CSV; split "landscaping and pest control" into two separate checklist items; added runtime migration guard
- Edited parking checklist: renamed "Reserve parking lot or designated section" → "Reserve parking stalls through UPD"; removed ADA spaces, UPD coordination, confirmation number, and "Send parking instructions" items
- Made "Request traffic control for large events" only visible when expected attendance > 100
- Removed business-days text from all checklist item names (Catering, Campus Venue, Billing) — timeline Before/After Event sections handle deadline display
- Updated subtitle to "Work together with your campus stakeholders to never miss a deadline on your campus event."
- Campus Venue checklist edits: renamed approval item to "Receive venue approval and confirmation from event professional", moved to 2nd position; fixed "Review campus protocols" UACE reference in CSV
- Extracted `render_item_row()` helper; built `render_campus_venue_tab()` with a "📋 Meeting agenda items" expander nested under "Meet with Event Professional to review event logistics"
- Sub-items in Meeting agenda: removed "with event professional" suffix from "Review event run-of-show" and "Review campus protocols and event procedures"

## Current State
- **Branch:** main (3 commits ahead of origin)
- **Server:** Streamlit running on port 8501 (PID 19433)
- **App URL:** https://orange-journey-5vq59rgvjj9qf7q9r-8501.app.github.dev
- **Uncommitted changes:** `app.py` and `data_ai/checklist_items.csv` modified since last checkpoint
- **Last checkpoint tag:** `checkpoint` → commit `12f5373`

## Next Steps
- Run `/checkpoint` to save current uncommitted changes
- Consider whether the sidebar should ever be collapsible again (currently forced open)
- User may want to continue editing other checklist categories (Facilities, Billing, Outdoor)
- Consider adding a print/export view (PDF or shareable checklist summary) — mentioned in previous session
- Push latest commits to GitHub origin when ready

## Key Decisions
- **Sidebar forced open:** Instead of fighting Streamlit's localStorage-cached collapsed state, sidebar is now permanently pinned open via CSS. The toggle buttons are hidden. This is the safest UX choice given the constraints.
- **Font override scope:** Changed from `* { font-family: Montserrat !important }` to targeting specific HTML elements (p, h1, button, div, label, etc.) — this preserves Material Icons rendering in Streamlit's internal span elements
- **Campus Venue sub-items:** Implemented via `render_campus_venue_tab()` with `CV_SUB_ITEMS` set and `CV_MEETING_ITEM` constant. Sub-items are stored in the same category in the CSV; grouping is purely a display concern handled at render time
- **Traffic control conditional:** Filtered at render time (not stored differently in CSV) — item exists in CSV but is hidden when attendance ≤ 100; appears automatically if attendance is later updated
- **Business-days removed from item names:** Timeline's Before/After Event sections already show deadlines; cleaner to keep item names action-focused

## Watchouts
- **`render_item_row` is now shared:** Both `render_checklist_tab` and `render_campus_venue_tab` call it. `STATUS_EMOJI` and `STATUS_OPTIONS` are now module-level constants (not inside the function) — don't re-declare them inside functions
- **Campus Venue filter applies to both main and sub-items:** If user filters by "Completed", sub-items also filter, and the expander shows "No items match" if all sub-items are filtered out
- **Sidebar CSS uses `transform: none !important` and `min-width: 244px`** — if Streamlit upgrades and changes how it hides the sidebar (e.g., uses a different CSS property), the sidebar may break again
- **3 commits ahead of origin** — not yet pushed to GitHub remote
- **Uncommitted changes** — `app.py` and CSV have changes not yet in a checkpoint
