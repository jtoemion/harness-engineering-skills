---
type: dashboard
project: __PROJECT__
updated: __YYYY-MM-DD__
---
# __PROJECT__ Dashboard

## Active Task
[[activeContext]] — __one-line current task__

## Blockers
<!-- List current blockers -->

## Open Mistakes
```dataview
LIST FROM "02_Mistakes" WHERE status = "ACTIVE"
```

## Recent Sessions
```dataview
TABLE date, outcome, task
FROM "01_Sessions"
SORT date DESC
LIMIT 5
```

## Open Decisions
```dataview
LIST FROM "03_Patterns" WHERE type = "decision" AND status = "active"
```

## Progress
- __X__/__Y__ tasks complete
- See [[progress]]
