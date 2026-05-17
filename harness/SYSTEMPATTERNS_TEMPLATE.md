# systemPatterns.md — Template

This template shows the Newspaper Logic format for retrospective entries in systemPatterns.md.

## Entry Format

Each retrospective entry MUST follow this structure:

```markdown
## HEADLINE: [One-line lesson]

> SUMMARY: [Core takeaway in one sentence]

<details>
<summary>Details</summary>

- **Context**: [What project/situation this arose from]
- **What went wrong**: [The specific failure]
- **The fix**: [What resolved it]
- **Prevention**: [How to avoid in future]
- **References**: [Files, lines, links]

</details>
```

## Example

```markdown
## HEADLINE: Anonymous proxy UID must use getRealUserId() in Firestore rules

> SUMMARY: When using anonymous proxy auth, all Firestore writes must pass actualUserId || uid, not bare uid.

<details>
<summary>Details</summary>

- **Context**: CreateSessionModal creating sessions via PIN login
- **What went wrong**: Passed `userProfile?.uid` as tutorId, but uid was anonymous Firebase UID
- **The fix**: Changed to `actualUserId || uid` in security rules and component code
- **Prevention**: For any task touching auth/permissions/Firestore, run the Permission Error Diagnosis Protocol
- **References**: `firestore.rules:206-208`, `CreateSessionModal.tsx:166`, `authService.ts:88-107`

</details>
```

## Migration Note

When systemPatterns.md grows past 20 entries, refactor existing entries to this format.
New entries MUST use this format from now on.
