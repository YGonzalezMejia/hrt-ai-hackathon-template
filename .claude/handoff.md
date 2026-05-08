# Handoff — 2026-05-08

## Summary
- Fixed catering tab error (TypeError when selecting Yes) — `catering_enabled`/`parking_enabled` columns were loading as float64 from CSV; added `.fillna("").astype(str)` on load
- Reordered and renamed Catering checklist items: dietary/allergy first, submit order 10 biz days, confirm headcount 5 biz days, confirm delivery 5 biz days
- Renamed "UACE" → "University Events Department" → "Events Dept." throughout app and migrated existing CSV data each time
- Removed several Events Dept. checklist items: Submit event request (UACE), Confirm event timeline, Confirm ceremonial equipment, Coordinate VIP arrangements
- Edited items: run-of-show and campus protocols now say "with event professional"; AV equipment now says "10 business days in advance"
- Renamed FMD item to "Request room setup with a layout (tables, chairs), and equipment totals listed"
- Removed "Request post-event room breakdown and cleanup" from FMD
- Moved outdoor-only FMD items (extension cords, landscaping/pest control) to Outdoor tab, labeled "through FMD"
- Rebuilt Billing tab: removed cost estimate requests, added 4 post-event invoice items (FMD, Catering, Parking/UPD, Events Dept.) due 20 biz days after event; "Confirm funding source" moved to top
- Added `add_business_days()` helper and updated `build_timeline()` to show post-event invoice deadlines
- Redesigned timeline: grouped into "📋 Before Event" / "📬 After Event" collapsible sections + status filter dropdown (All / Upcoming / Due Today / Past Due); Before Event expanded by default
- Moved catering and parking Yes/No radios inside their respective tabs (removed standalone Services section); Catering and Parking tabs are now always visible
- Added CSS to hide Streamlit toolbar/keyboard shortcut badge using exact data-testid selectors found in JS bundle
- Added bottom padding and margin above Danger Zone to fix visual overlap
- Tabs styled to fill full width with equal spacing (flex: 1)
- Saved git checkpoint at commit `0576704`

## Current State
- **Branch:** main (2 commits ahead of origin, plus uncommitted changes to `app.py`)
- **Server:** Streamlit running on port 8501
- **App URL:** https://orange-journey-5vq59rgvjj9qf7q9r-8501.app.github.dev
- **Data files:** `data_ai/events.csv` and `data_ai/checklist_items.csv` exist with migrated data
- **Last checkpoint tag:** `checkpoint` → commit `0576704`
- **Uncommitted:** `app.py` has CSS and layout changes from this session not yet committed

## Next Steps
- Verify the keyboard/toolbar badge is fully hidden after the CSS fix (user was still seeing it at end of session)
- Verify the event details / delete event overlap is resolved
- User may want to add more outdoor checklist items (mentioned "for now" in earlier session)
- Consider a print/export view (PDF or shareable checklist summary)
- Push latest changes to GitHub origin when ready

## Key Decisions
- **Events Dept. migration:** Each rename required both a DEFAULT_CHECKLIST update AND a CSV data migration (sed + Python script) + a runtime migration guard in `load_checklist()` — pattern to follow for any future renames
- **Post-event timeline deadlines:** `add_business_days()` counts forward from event date; timeline now has both pre- and post-event phases
- **Catering/Parking always-visible tabs:** Removed conditional tab rendering; the Yes/No radio now lives inside the tab so planners always see it — checklist only appears below if Yes
- **Timeline layout:** Before Event section is expanded by default; After Event is collapsed — reduces overwhelm while keeping invoice deadlines accessible
- **Toolbar hiding:** Used exact `data-testid` values from Streamlit JS bundle (`stAppToolbar`, `stToolbarActionButton`, `stToolbarActionButtonLabel`, etc.) rather than guessing

## Watchouts
- **Existing event checklists won't get DEFAULT_CHECKLIST changes automatically** — only new events get the latest template. Use a Python migration script (as done this session) to patch existing CSV rows
- **`catering_enabled` / `parking_enabled` stored as string "True"/"False"/""** — `is_enabled()` and `is_answered()` helpers handle conversion; never compare directly with Python booleans
- **Keyboard badge CSS** — uses internal Streamlit `data-testid` attributes that may change on Streamlit upgrades; if it reappears after an upgrade, re-run the selector search in the JS bundle
- **Uncommitted changes** — `app.py` has unsaved changes not yet in the checkpoint; run `/checkpoint` at the start of next session after verifying fixes
- **2 commits ahead of origin** — changes have not been pushed to GitHub remote yet
