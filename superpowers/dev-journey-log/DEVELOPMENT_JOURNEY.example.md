# Development Journey

> Append-only log of every meaningful change to this project.
> Never edit or delete past entries — only append. Newest entries go at the top.

---

## Changelog

### [2025-06-14] — Add Profile Picture Upload

**Type:** feature
**Status:** completed
**Files Changed:**
- `components/ProfilePage.jsx` — Added avatar upload section with preview
- `routes/user.js` — Added `POST /api/user/avatar` endpoint
- `middleware/upload.js` — Created multer config for image uploads (5MB max, jpg/png only)
- `services/storage.js` — Added `uploadToS3()` helper
- `package.json` — Added `multer` and `@aws-sdk/client-s3`

**Summary:**
Users can now upload a profile picture from the settings page. The image is validated on the
server (type and size), uploaded to S3, and the URL is saved to the users table. The avatar
appears immediately in the nav bar after upload without a page refresh.

**Impact:**
AWS S3 credentials must be present in `.env` (`AWS_BUCKET`, `AWS_REGION`, `AWS_ACCESS_KEY`,
`AWS_SECRET_KEY`). Existing users without avatars will show a default placeholder icon.

**Trace:**
Builds on `[2025-06-10] — Add User Settings Page`

---

### [2025-06-12] — Fix JWT Expiry Not Refreshing Session

**Type:** fix
**Status:** completed
**Files Changed:**
- `middleware/validateToken.js` — Added token refresh logic when token is within 10min of expiry
- `routes/auth.js` — Added `POST /api/auth/refresh` endpoint
- `hooks/useAuth.js` — Frontend now reads `x-refreshed-token` header and updates stored token

**Summary:**
Users were being logged out mid-session when their JWT expired after 1 hour. The middleware now
checks if the token is close to expiring and issues a new one transparently. The frontend picks
up the refreshed token from the response header and replaces the stored one automatically.

**Impact:**
Sessions now remain active as long as the user is using the app. Idle sessions still expire.
No database changes required.

**Trace:**
Fixes bug introduced in `[2025-06-10] — Add POST /api/auth/login Route`

---

### [2025-06-11] — Add User Settings Page

**Type:** feature
**Status:** completed
**Files Changed:**
- `pages/SettingsPage.jsx` — Created settings page with name and email update form
- `components/SettingsForm.jsx` — Form component with validation
- `routes/user.js` — Added `GET /api/user/me` and `PATCH /api/user/me` endpoints
- `app.js` — Registered user router under `/api/user`
- `router.js` — Added `/settings` frontend route

**Summary:**
Users can now view and update their display name and email from a dedicated settings page.
Changes are saved via a PATCH request and reflected immediately in the UI. Email changes
require the new address to be unique in the database.

**Impact:**
The `/settings` route is protected — unauthenticated users are redirected to `/login`.
No BREAKING changes to existing routes.

**Trace:**
N/A

---

### [2025-06-10] — Add POST /api/auth/login Route

**Type:** feature
**Status:** completed
**Files Changed:**
- `routes/auth.js` — Created new file with login and logout handlers
- `middleware/validateToken.js` — Added JWT validation middleware
- `app.js` — Registered auth router under `/api/auth`
- `package.json` — Added `jsonwebtoken` and `bcrypt`

**Summary:**
Implemented a login endpoint that accepts email and password, validates credentials against
the users table, and returns a signed JWT on success. A logout endpoint clears the token.
This enables authenticated sessions across the app.

**Impact:**
All protected routes must now use the `validateToken` middleware. The JWT secret must be
set in `.env` as `JWT_SECRET`. No existing routes were broken.

**Trace:**
N/A

---

### [2025-06-09] — Initial Project Scaffold

**Type:** feature
**Status:** completed
**Files Changed:**
- `app.js` — Express server setup
- `router.js` — React Router base config
- `package.json` — Project dependencies (express, react, react-dom, vite)
- `vite.config.js` — Vite dev server config
- `.env.example` — Environment variable template
- `README.md` — Project overview and setup instructions

**Summary:**
Created the base project structure. Express handles the API on port 3001, Vite serves the
React frontend on port 5173 with proxy to the API. ESLint and Prettier configured.

**Impact:**
N/A — initial setup.

**Trace:**
N/A

---
