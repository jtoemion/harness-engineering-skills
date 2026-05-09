# Selectors — students.ezralms.com

## Selector Priority Format

| Element | Primary (verified) | Fallback (candidate) | Stable? |
|---------|-------------------|---------------------|---------|
| ... | ... | ... | ... |

## Page: Login — /login

### Iframes
(none)

### Selector Priority Table

| Element | Primary | Fallback | Stable? |
|---------|---------|----------|---------|
| Username input | textbox "Username or Email" | #identifier | ✓ verified |
| Continue button | button "Continue" | button[type="button"]:has-text("Continue") | ✓ verified |
| PIN input | textbox "6-Digit PIN" | #pin | ✓ verified |
| Sign In button | button "Sign In" | button[type="submit"] | ✓ verified |

## Page: Tutor Dashboard — /tutor-dashboard

### Iframes
(none)

### Selector Priority Table

| Element | Primary | Fallback | Stable? |
|---------|---------|----------|---------|
| Sidebar: Dashboard | link "Dashboard" | a[href="/tutor-dashboard"] | ✓ verified |
| Sidebar: Classes | link "Classes" | a[href="/classes"] | ✓ verified |
| Sidebar: Calendar | link "Calendar" | a[href="/calendar"] | ✓ verified |
| Sidebar: Students | link "Students" | a[href="/students"] | ✓ verified |
| Sidebar: Tasks | link "Tasks" | a[href="/tasks"] | ✓ verified |
| Sidebar: Staff | link "Staff" | a[href="/staff"] | ✓ verified |
| Sidebar: Quiz Library | link "Quiz Library" | a[href="/library"] | ✓ verified |

## Page: Class Detail — /class/{id}

### Iframes
(none currently observed)

### Selector Priority Table

| Element | Primary | Fallback | Stable? |
|---------|---------|----------|---------|
| Tab: Classwork | tab "Classwork" | [aria-label="Classwork tab"] | ✓ verified |
| Tab: Students | tab "Students" | [aria-label="Students tab"] | ✓ verified |
| Tab: Marks | tab "Marks" | [aria-label="Marks tab"] | ? candidate |
| Filter: Subject Matter | button "📖 Subject Matter" | button:has-text("Subject Matter") | ✓ verified |
| Filter: Quiz | button "🧩 Quiz" | button:has-text("Quiz") | ✓ verified |
| Filter: Test | button "📝 Test" | button:has-text("Test") | ✓ verified |
| Filter: Games | button "🎮 Games" | button:has-text("Games") | ✓ verified |
| Add Topic button | button "Add Topic" | [data-testid="add-topic"] | ✓ verified |

### Stable UIDs (survive reload)
- Topic item: `[data-topic-id]` attribute on topic container
- Sub-topic: `[data-subtopic-id]` attribute on subtopic card

## Page: Lesson Builder — /lessons/builder

### Iframes
(none)

### Selector Priority Table

| Element | Primary | Fallback | Stable? |
|---------|---------|----------|---------|
| Code button | button "Code" | button:has-text("Code") | ✓ verified |
| Split button | button "Split" | button:has-text("Split") | ✓ verified |
| Preview button | button "Preview" | button:has-text("Preview") | ✓ verified |
| Save button | button "Save" | button:has-text("Save") | ✓ verified |
| HTML Source textarea | textarea | #html-source | ? candidate |
| Lesson title (metadata) | heading | h1 | ✓ verified |

## Notes

- All recipes use ` -> ` (ASCII) as step separator, not Unicode `→`
- Wait for element visibility before interacting — React hydration causes elements to appear after page load
- PIN field submits on Enter key — use `[press_enter] #pin` instead of clicking Sign In button (modal overlay blocks clicks)