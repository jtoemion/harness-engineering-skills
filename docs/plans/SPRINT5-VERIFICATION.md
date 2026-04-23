# Sprint 5 Verification Checklist

## Per-Project Verification (forgeWhisper, LP-bmw, LPPastpapr, n8n-ytdlp-setup, question-extractor)

For each project:

### Boot Verification
- [ ] .memory/ symlink/junction points to 00_Memory/
- [ ] All 5 canonical files in 00_Memory/ have valid YAML frontmatter
- [ ] Frontmatter has correct project_code
- [ ] 01_Sessions/, 02_Mistakes/, 03_Patterns/, 04_Index/ directories exist
- [ ] Dashboard.md renders in Obsidian (if app open)

### Session Close Verification
- [ ] Can create a test session note in 01_Sessions/
- [ ] Can update activeContext.md
- [ ] Can update progress.md
- [ ] Atomic close staging directory created and cleaned up

### Vault Structure Verification
- [ ] .obsidian/ directory exists with app.json + appearance.json
- [ ] .gitignore exists with correct entries
- [ ] 05_Templates/ has all 10 template files

### Obsidian Graph Verification
- [ ] Open project vault in Obsidian
- [ ] Verify graph shows correct node types
- [ ] Verify [[links]] resolve
- [ ] Verify Dashboard Dataview queries render

### Cross-Project Verification
- [ ] Global vault at AntigravityV is accessible
- [ ] Projects.md in global vault lists all migrated projects
- [ ] Can query global vault for patterns

## Global Vault Verification
- [ ] 00_Global/Mistakes/, Patterns/, Decisions/ exist
- [ ] 02_Index/ has Projects.md, Mistakes.md, Patterns.md
- [ ] Dataview queries work in global vault