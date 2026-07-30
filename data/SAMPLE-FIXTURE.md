# Sample saved-blueprint fixture

`sample-saved-blueprints.json` is a **committed sample fixture**, not live user
data and not something the app reads.

## What it is

Three blueprints generated on 2026-07-21 from the Card P.9 dry-run profiles
(`Profile 1/2/3`), exported through the app's own *Export all (.json)* button. All
three have an empty `project_name`. It exists so the shape of a saved blueprint is
documented by example — Build Guide 34 uses it to show what the PDF export renders
from.

## What it is not

- **Not written at runtime.** Saved blueprints live in `st.session_state` and only
  leave the machine when a user clicks the download button
  (`app/saved_blueprints.py`). Nothing in the app writes to `data/`.
- **Not user data.** No real participant's blueprint or project name is in here —
  verified against the 8-participant test round, where none of the project names
  typed appear in any tracked file.

## If you regenerate it

Load the three P.9 profiles, save each, then use *Export all (.json)* and replace
this file. Keep `project_name` empty — the field is free text and the fixture
should never carry anything that looks like real user input.
