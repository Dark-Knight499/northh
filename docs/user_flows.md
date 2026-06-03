# User Flows

## Screen Tree

```
North App
│
├── Home ............................................ (start)
│   ├── [Space] → Capture
│   ├── [I]     → Browser (ideas)
│   ├── [P]     → Browser (projects)
│   ├── [D]     → Browser (domains)
│   ├── [J]     → Browser (journal)
│   ├── [T]     → Capture (journal)
│   ├── [?]     → HelpOverlay
│   └── [Q]     → exit
│
├── Capture
│   ├── mode: idea
│   ├── mode: journal                   (from [T] or context-aware [Space] in journal)
│   ├── mode: project_items             (context-aware [Space] in project drill-in)
│   ├── mode: domain_items              (context-aware [Space] in domain drill-in)
│   │
│   ├── type text → [Ctrl+S] → save ✓ → auto-pop 0.7s → back
│   ├── empty   → [Ctrl+S] → pop immediately → back
│   ├── [Esc] → cancel → back
│   └── [E]    → (journal only) open today's file in $EDITOR → back
│
├── Browser
│   ├── mode: ideas
│   │   ├── [N]      → Capture (idea)
│   │   ├── [Space]  → Capture (idea)
│   │   ├── [Enter]  → open entry in $EDITOR → reload
│   │   ├── [/]      → focus filter input → type to filter
│   │   └── [Esc]    → back
│   │
│   ├── mode: projects
│   │   ├── [N]      → NewEntry (project) → name → text → save → back
│   │   ├── [Enter]  → drill into project → Browser (project_items)
│   │   ├── [Space]  → Capture (idea — project mode not contextual)
│   │   ├── [/]      → focus filter
│   │   └── [Esc]    → back
│   │   └── project_items (drill-in)
│   │       ├── [N]      → NewEntry (project, obj_name) → text → save → back
│   │       ├── [Space]  → Capture (project_items) → saves into project
│   │       ├── [Enter]  → open entry in $EDITOR (with line#) → reload
│   │       ├── [/]      → focus filter
│   │       └── [Esc]    → back to parent browser
│   │
│   ├── mode: domains
│   │   ├── [N]      → NewEntry (domain) → name → text → save → back
│   │   ├── [Enter]  → drill into domain → Browser (domain_items)
│   │   ├── [Space]  → Capture (idea — domain mode not contextual)
│   │   ├── [/]      → focus filter
│   │   └── [Esc]    → back
│   │   └── domain_items (drill-in)
│   │       ├── [N]      → NewEntry (domain, obj_name) → text → save → back
│   │       ├── [Space]  → Capture (domain_items) → saves into domain
│   │       ├── [Enter]  → open entry in $EDITOR (with line#) → reload
│   │       ├── [/]      → focus filter
│   │       └── [Esc]    → back to parent browser
│   │
│   └── mode: journal
│       ├── [N]      → NewEntry (journal) → title → text → save → back
│       ├── [Space]  → Capture (journal) → appends to today's file
│       ├── [T]      → Capture (journal) → today's entry
│       ├── [Enter]  → open entry in $EDITOR (with line#) → reload
│       ├── [/]      → focus filter
│       └── [Esc]    → back
│
├── NewEntry
│   ├── mode: project / domain / journal
│   │   ├── step: name
│   │   │   ├── type name → [Enter] → step: text
│   │   │   ├── [Ctrl+S] → same as [Enter]
│   │   │   └── [Esc]    → cancel → back
│   │   └── step: text
│   │       ├── type text → [Ctrl+S] → save ✓ → auto-pop 0.7s → back
│   │       ├── empty   → [Ctrl+S] → pop immediately → back
│   │       ├── [Enter] → new line (TextArea default)
│   │       └── [Esc]   → cancel → pop → back
│   │
│   └── mode: project / domain (with obj_name — from drill-in)
│       └── step: text (skips name)
│           ├── type text → [Ctrl+S] → save → pop → back
│           ├── empty   → [Ctrl+S] → pop
│           ├── [Enter] → new line
│           └── [Esc]   → cancel → back
│
└── HelpOverlay
    ├── [Esc] → back
    └── [?]   → back
```

## Full Flow Walkthroughs

### Quick Capture (Space from Home)
```
Home → [Space]
  → Capture (idea)
    → [type thought]
    → [Ctrl+S]
      → green border flash "✓ saved"
      → 0.7s later pop back to Home
```

### Create Project with Entry
```
Home → [P]
  → Browser (projects)
    → [N]
      → NewEntry (project, step=name)
        → [type "my-project"] → [Enter]
          → NewEntry (project, step=text)
            → [type "first entry"] → [Ctrl+S]
              → green flash, pop to Browser
              → Browser reloads, shows new entry
        → [Esc] cancels at any step
```

### Drill into Project, Capture, Open
```
Home → [P]
  → Browser (projects)
    → [Enter] on "projA"
      → Browser (project_items, obj_name="projA")
        → [Space]
          → Capture (project_items, obj_name="projA")
            → [type "quick thought"] → [Ctrl+S]
            → pop back, browser reloads
        → [Enter] on an entry
          → suspends TUI, opens $EDITOR
          → on editor exit, browser reloads
        → [Esc] back to parent
```

### Journal Entry with Title
```
Home → [J]
  → Browser (journal)
    → [N]
      → NewEntry (journal, step=name)
        → [type "meeting notes"] → [Enter]
          → NewEntry (journal, step=text)
            → [type "discussed Q3 plans"] → [Ctrl+S]
              → appended to journal/YYYY-MM-DD.md
              → pop back to Browser
```

### Today's Journal (two paths)
```
Path A:
Home → [T]
  → Capture (journal)
    → [type "standup done"] → [Ctrl+S]
    → appended to journal/YYYY-MM-DD.md
    → pop back

Path B:
Home → [J] → Browser (journal) → [T]
  → same Capture (journal)
```

### Open Journal Entry in Editor
```
Home → [J]
  → Browser (journal)
    → [Enter] on entry
      → suspends TUI
      → opens journal/YYYY-MM-DD.md at correct line
      → editor exits → TUI resumes → browser reloads
```

### Context-Aware Capture
```
When [Space] is pressed:
  Top of stack    → Capture mode     → saves to
  ─────────────   ────────────────   ─────────────
  Home            → idea             → ideas/*.md
  Browser(ideas) → idea             → ideas/*.md
  Browser(projects) → idea          → ideas/*.md
  Browser(domains)  → idea          → ideas/*.md
  Browser(journal)  → journal       → journal/YYYY-MM-DD.md
  Browser(project_items) → project_items → projects/<name>/*.md
  Browser(domain_items)  → domain_items  → domains/<name>/*.md
```

### Keyboard Summary by Screen

| Screen      | Key       | Action                     |
|-------------|-----------|----------------------------|
| **Home**    | Space     | Quick Capture              |
|             | I         | Browse Ideas               |
|             | P         | Browse Projects            |
|             | D         | Browse Domains             |
|             | J         | Browse Journal             |
|             | T         | Today's Journal            |
|             | ?         | Help                       |
|             | Q         | Quit                       |
| **Capture** | Ctrl+S    | Save & pop                 |
|             | Esc       | Cancel                     |
|             | E         | Open editor (journal only) |
| **Browser** | N         | New entry                  |
|             | Space     | Context-aware capture      |
|             | Enter     | Open / drill in            |
|             | /         | Focus filter               |
|             | Esc       | Back                       |
|             | T         | Today (journal only)       |
| **NewEntry**| Ctrl+S    | Submit / save              |
|             | Enter     | Next step / new line       |
|             | Esc       | Cancel                     |
| **Help**    | Esc / ?   | Close                      |

## Edge Cases

- **Empty submission**: Ctrl+S with empty text → pops immediately, nothing saved
- **No focus**: Browser list highlighted via `initial_index=0` — Enter works without prior navigation
- **Rapid keys**: Sequential presses (e.g. `i escape p escape d escape`) are safe — each action completes before next
- **Filter resets**: Typing `/` focuses filter input; typing filters entries in real-time; pressing Esc blurs filter, pressing Esc again goes back
