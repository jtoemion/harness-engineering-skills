# Feature Map

> Living map of every user-facing feature and interaction flow in this app.
> Updated in-place whenever features change. Mark removed features [REMOVED] — never delete them.

---

## Authentication
> Handles user login and logout. All other pages require a valid session.
> Route: `/login` | Component: `LoginPage.jsx`

### Login
> Allows an existing user to authenticate and receive a session token.

**Component Hierarchy:**
- [Page] `LoginPage`
  - [Component] `LoginForm`
    - [Input] Email field
    - [Input] Password field
    - [Button] "Sign In"
  - [Component] `ErrorBanner` (renders on failed login)

**Interaction Flow:**
```
User → types email and password
     → clicks "Sign In"
          → [validates] both fields are filled
               ✗ empty → [renders] red border on empty field → stops
               ✓ filled → [calls] POST /api/auth/login
                              ✗ 401 Unauthorized → [renders] ErrorBanner "Invalid email or password"
                              ✗ 500 Server Error → [renders] ErrorBanner "Something went wrong, try again"
                              ✓ 200 OK → [stores] JWT in localStorage
                                       → [redirects] to /dashboard
```

**Connected To:**
- API: `POST /api/auth/login` — validates credentials, returns signed JWT
- State: `authStore.token` and `authStore.user` set on success
- Side Effects: Redirect to `/dashboard`, welcome toast "Welcome back, {name}!"

**Added:** 2025-06-10 | **Updated:** 2025-06-12 | **Status:** active

---

### Logout
> Ends the user's session and returns them to the login screen.

**Component Hierarchy:**
- [Layout] `NavBar`
  - [Button] "Log Out" (top-right corner)

**Interaction Flow:**
```
User → clicks "Log Out" in the nav bar
     → [calls] POST /api/auth/logout
          → [clears] JWT from localStorage
          → [clears] authStore state
          → [redirects] to /login
```

**Connected To:**
- API: `POST /api/auth/logout` — invalidates server-side session record
- State: `authStore` fully reset
- Side Effects: Redirect to `/login`

**Added:** 2025-06-10 | **Updated:** 2025-06-10 | **Status:** active

---

## Dashboard
> The main landing page after login. Shows an overview of the user's activity and quick actions.
> Route: `/dashboard` | Component: `DashboardPage.jsx`

### Activity Feed
> Displays a list of the user's recent actions in reverse chronological order.

**Component Hierarchy:**
- [Page] `DashboardPage`
  - [Component] `ActivityFeed`
    - [Component] `ActivityCard` (one per event)
    - [Component] `EmptyState` (renders when no activity exists)

**Interaction Flow:**
```
User → arrives at /dashboard
     → [calls] GET /api/activity?limit=20
          ✗ error → [renders] inline error message "Couldn't load activity"
          ✓ success → [renders] list of ActivityCard components
                           → each card shows: action type, timestamp, brief description
     → clicks an ActivityCard
          → [redirects] to the relevant detail page for that activity
```

**Connected To:**
- API: `GET /api/activity?limit=20` — returns last 20 activity events for current user
- State: `activityStore.feed` populated on load
- Side Effects: None

**Added:** 2025-06-11 | **Updated:** 2025-06-11 | **Status:** active

---

## Settings
> Lets the user manage their account details and preferences.
> Route: `/settings` | Component: `SettingsPage.jsx`

### Update Profile Info
> Allows the user to change their display name and email address.

**Component Hierarchy:**
- [Page] `SettingsPage`
  - [Component] `SettingsForm`
    - [Input] Display name field (pre-filled)
    - [Input] Email field (pre-filled)
    - [Button] "Save Changes"
  - [Component] `SuccessBanner` (renders on save)
  - [Component] `ErrorBanner` (renders on failure)

**Interaction Flow:**
```
User → navigates to /settings
     → [calls] GET /api/user/me → [renders] current name and email in form fields
     → edits name or email
     → clicks "Save Changes"
          → [validates] name is not empty, email is valid format
               ✗ invalid → [renders] inline field errors → stops
               ✓ valid → [calls] PATCH /api/user/me
                              ✗ 409 Conflict → [renders] ErrorBanner "That email is already in use"
                              ✗ 500 → [renders] ErrorBanner "Couldn't save, please try again"
                              ✓ 200 OK → [renders] SuccessBanner "Profile updated"
                                       → [updates] name shown in NavBar immediately
```

**Connected To:**
- API: `GET /api/user/me` — loads current user data
- API: `PATCH /api/user/me` — saves name and/or email changes
- State: `authStore.user.name` and `authStore.user.email` updated on success
- Side Effects: NavBar display name refreshes without page reload

**Added:** 2025-06-11 | **Updated:** 2025-06-11 | **Status:** active

---

### Upload Profile Picture
> Lets the user upload a custom avatar image.

**Component Hierarchy:**
- [Page] `SettingsPage`
  - [Component] `AvatarUploader`
    - [Element] Avatar preview image
    - [Element] "Upload Photo" button (triggers file picker)
    - [Element] Hidden `<input type="file">` (jpg/png, max 5MB)

**Interaction Flow:**
```
User → clicks "Upload Photo"
     → [renders] OS file picker dialog
     → selects an image file
          → [validates] file is jpg or png AND under 5MB
               ✗ wrong type or too large → [renders] inline error "Please use a JPG or PNG under 5MB"
               ✓ valid → [renders] preview of selected image below the button
     → clicks "Save Changes"
          → [calls] POST /api/user/avatar (multipart/form-data)
               ✗ upload fails → [renders] ErrorBanner "Upload failed, please try again"
               ✓ 200 OK → [renders] new avatar in NavBar immediately
                        → [renders] SuccessBanner "Profile picture updated"
```

**Connected To:**
- API: `POST /api/user/avatar` — uploads image to S3, saves URL to users table
- State: `authStore.user.avatarUrl` updated on success
- Side Effects: NavBar avatar refreshes without page reload. Requires AWS S3 env vars.

**Added:** 2025-06-14 | **Updated:** 2025-06-14 | **Status:** active

---
