# EzraLMS - students.ezralms.com

## Overview
- **Site:** EzraLMS (Learning Management System)
- **URL:** https://students.ezralms.com
- **Framework:** Next.js with Firebase Firestore
- **Auth:** Username/Email + 6-digit PIN

---

## Credentials

| User | Username | PIN | Role |
|------|----------|-----|------|
| Jorah | Jorah | 111111 | admin |

---

## URL Routes

| Page | URL |
|------|-----|
| Login | `/login` |
| Tutor Dashboard | `/tutor-dashboard` |
| Classes | `/classes` |
| Students | `/students` |
| Calendar | `/calendar` |
| Tasks | `/tasks` |
| Staff | `/staff` |
| Test Panel | `/admin/test-panel` |
| Quiz Library | `/library` |
| Lessons | `/lessons` |
| Lesson Builder | `/lessons/builder?lesson={id}` |
| Lesson Viewer | `/lesson/{id}` |
| Lesson Editor | `/lessons/{id}/edit` |
| Subtopics | `/subtopics` |
| Games | `/games` |
| Class Detail | `/class/{id}` |

---

## Login Flow

```
1. [goto] https://students.ezralms.com/login
2. [wait] textbox "Username or Email" visible
3. [type] textbox "Username or Email" -> Jorah
4. [click] button "Continue"
5. [wait] textbox "6-Digit PIN" visible
6. [type] textbox "6-Digit PIN" -> 111111
7. [click] button "Sign In"
8. [wait] heading contains "Good Evening"
```

---

## Classes (34 Total)

| Class Name | Class ID | Subject | Section | Tutors |
|------------|----------|---------|---------|--------|
| CSCA Math | WPvmJ3YVEsOW8ZFBKoGu | Math | Batch 3 | Ezra Theodores, Ms Ewink Susanti, Mr. Budi |
| OSN Level C | DT2Rn9hWLlhSbnerbw1U | Olympiad | OSN | Ezra Theodores, BundaAliaAlwi |
| Grade 7 IB | 2jx2rGk5Y0yZ9f9ZZMaY | Math | IB | Ezra Theodores |
| OSN LEVEL B | 93yJ1p7glf8cfyWoZGeP | Math OSN | Olympiad | Ezra Theodores |
| Grade 1 Super | Bl4Vw6z5hDOfSMzfbPUr | Math | Super Kids | Ezra Theodores, Tutor1, Ms. Murni, Benaya, Arie Agung |
| Science Grade 7 | N338keGQ7Ytm7BlgEyGd | Science | Physic | Ezra Theodores |
| G7 NATIONAL PLUS | Paou5x2HmTDpJCdN2i4q | Math | BPK PENABUR | - |
| MW G7 | K6yoVSkA1ZnbfawQL3NX | - | 7 | Booji Aww, Ms Julie |
| Grade X International | QgSnQVZfgkKdPlTZxW7T | Math | IB | Ezra Theodores |
| G4 NATIONAL | SNk7dy7ONmkXV6JwUHVw | Math | National | Ezra Theodores, Benaya, Arie Agung, Ms. Murni |
| 11 IPS NASIONAL | VaZVCiWh5yVXQvD3cZwO | Math | SMA | Ezra Theodores |
| G3 NATIONAL GRADE 3 | WzpPsq4iI4GIUsi8odHR | NATIONAL CURRICULUM | NORMAL | Ezra Theodores, Benaya, Arie Agung, Ms. Murni |
| Private 9: Kendra | YhNsoQIsOMFVPwy7VdjX | Math | International: IB | Ezra Theodores |
| Grade 5 Interational | Z8np6MEIkKL7bBiCtW1W | International Curriculum | USA | Ezra Theodores |
| G11 Sociology | g8PKxn9MWChRo5h8nHN2 | Sociology | Social Science | Ezra Theodores |
| G2 NATIONAL | gwYZh3x9Qyohz15pl3U5 | Math | National | Ezra Theodores, Benaya, Arie Agung |
| Grade 9 SMPK BPK PENABUR | h7b2M8HNihF4DxoKI6AM | Math | Group | Ezra Theodores |
| Grade 1 Olympiad | jnx4aUfOcz0wa7Y9Pid3 | Math OSN | OSN | - |
| Test Class | nSmz129Pa0gtPoOTDzGc | Mathematics | A | Booji Aww |
| G5 NATIONAL | ph06TGXa49NZyWfQ7Xnz | Math | National | Ezra Theodores |
| G10 NATIONAL PLUS | qKhRl1uGpeSUEsG0kKym | Math | National Plus | Ezra Theodores, Ms Ewink Susanti |
| G8 NATIONAL PLUS | rKLckFly8YRbdHrAnu36 | Math | National Plus | Ezra Theodores |
| G6 NATIONAL | smTxhKrfhHh7VWmhzQLB | Math | National | Ezra Theodores, Benaya, Arie Agung, Ms. Murni, Syahanti |
| OSN Level A | zaqj97t0IBITIGOLTWxy | Grade 1-3 | OSN | - |
| Kelas 1 | fxKxhjW3en9yxdfx2BUJ | Math | Normal | Ezra Theodores |
| Ez Music Class | gm6M27mx1YHl06jQg2ZM | - | Intermediate | Ezra Theodores, Benaya |
| Learning AI | Bvdhog20JYSzx0K5S5I9 | AI Dev | - | Booji Aww, Ezra Theodores, Jorah |
| NICHOLAS PRIVATE | nhJBlxhNXlS1VXTI51Nb | MATH | COMPETITION | Ezra Theodores |
| ADMINISTRATOR | 78nxtDIfgqifw3KvjCPS | ADMIN TOOLS | ADMIN | Ezra Theodores, Booji Aww, Jorah, Tutor1 |
| 11 IPA NASIONAL | WHKRrz84eZoyo4jSZrDu | Math | Merdeka | Ezra Theodores |
| 12 IPA NASIONAL | yWFNchQnwJvQWaHIpgwt | Math | Science | Ezra Theodores |
| SIAP PTN | BWXNHMaouijTY9pFTkVb | Mathematics & Logic | Science | Ezra Theodores |
| SIAP PTN | sNyeHkAk3AJURG6n991y | Mathematics & Logic | Science | Ezra Theodores |
| HPS 5 Math | 2LbVwkI6vgZqd78A4lay | Math | HPS | Tutor1 |

---

## Class Page Structure

URL: `/class/{classId}`

### Elements on Class Page:
- **Tabs:** Classwork | Students | Marks
- **Filter buttons:** 📖 Subject Matter | 🧩 Quiz | 📝 Test | 🎮 Games
- **Add Topic button** - creates new topic section
- **Topic actions:** Drag to reorder | Edit | Delete
- **Sub-topic actions:** View | Add Sub-topic

### Class Actions:
- Promote class to students
- Edit class
- Delete class

---

## Creating Subtopics Flow

### Step 1: Create Topic
```
1. [goto] https://students.ezralms.com/class/{classId}
2. [click] "Add Topic" button
3. [wait] modal appears with "Topic title *" field
4. [type] "Topic title *" -> {TOPIC_NAME}
5. [click] color selector (optional)
6. [click] "Create" button
```

### Step 2: Create Sub-topic
```
1. [click] "Add Sub-topic" button on the topic
2. [wait] modal appears
3. [select] type:
   - 📖 Subject Matter -> [click] "Create New Subject Matter"
   - 🧩 Quiz -> [click] "Create New Quiz"
   - 📝 Test -> [click] "Create New Test"
   - 🎮 Games -> [click] "Create New Game"
4. [type] title -> {SUBTOPIC_NAME}
5. [click] "Create & Open Editor"
```

### Step 3: Edit Lesson in Builder
```
1. [wait] lesson builder loads at /lessons/builder?lesson={id}
2. [click] heading "Untitled Lesson" to open metadata panel
3. [type] Title -> {LESSON_TITLE}
4. [click] "Done"
5. [fill] HTML Source textarea with lesson HTML
6. [click] "Save"
```

---

## Lesson Builder

URL: `/lessons/builder?lesson={id}` or `/lessons/builder` (new lesson)

### Editor Features:
- **Code button** - shows HTML source only
- **Split button** - shows source + preview side by side
- **Preview button** - shows rendered preview only
- **Save button** - saves to Firestore
- **HTML Source textarea** - edit raw HTML

### Metadata Panel (click lesson title to open):
- Title * (required)
- Description (optional)
- Done/Cancel buttons

### IMPORTANT - Lesson Save Workflow:
1. Fill HTML content in textarea
2. Use keyboard: Ctrl+A (select all), Ctrl+C (copy), Ctrl+V (paste)
3. [click] "Save" button
4. Verify by navigating to `/lessons/{id}/edit`

### CSS Limitation:
The lesson viewer applies its own CSS that overrides custom styles. Use:
- Inline styles only (style="...")
- Simple HTML structure
- No CSS class dependencies

---

## Lesson URLs

| Purpose | URL Pattern |
|---------|-------------|
| Builder (edit) | `/lessons/builder?lesson={id}` |
| Viewer (read) | `/lesson/{id}` |
| Edit page | `/lessons/{id}/edit` |
| All lessons | `/lessons` |

---

## Sidebar Navigation

```
├── Dashboard (/tutor-dashboard)
├── Classes (/classes)
├── Calendar (/calendar)
├── Subtopics (expandable)
│   ├── Quiz Library (/library)
│   ├── Lessons (/lessons)
│   └── Games (/games)
├── Students (/students)
├── Tasks (/tasks)
├── Staff (/staff)
└── Test Panel (/admin/test-panel)
```

---

## Known Issues

1. **Lesson HTML Persistence:** HTML content saves to Firestore but lesson viewer applies sanitization that may strip some CSS. Use inline styles.

2. **Page Loading:** Some pages (Students, Tasks) take 5+ seconds to fully render. Use [wait] with longer timeouts.

3. **Modal Dialogs:** Some modals may block clicks. Use [click] with force:true if needed.

4. **Network Idle:** Avoid waiting for networkidle on this LMS - it uses Firebase long-polling which never truly idles.

---

## Selector Priority (Most Reliable First)

1. **URL navigation** - goto `/class/{id}` etc.
2. **Role selectors** - `button "Add Topic"`, `textbox "Username or Email"`
3. **Heading text** - `heading "Learning AI"`
4. **Link text** - `link "Classes"`

---

## Staff Members

| Initial | Name | Role |
|---------|------|------|
| E | Ezra Theodores | admin |
| T | Tutor1 | admin |
| J | Jorah | admin |
| B | Booji Aww | admin |
| M | Ms Ewink Susanti | tutor |

---

## Dashboard Stats

- Active Students: 64
- Sessions This Week: 0
- Renewals Needed: 7
- Total Quizzes: 299
- Total Staff: 12
- Total Classes: 34

---

## Last Updated
2026-04-23