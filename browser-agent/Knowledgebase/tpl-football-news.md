---
name: tpl-football-news
description: Templater template for new football news files
trigger: Creates properly formatted news note with frontmatter
---

<%*
// Required: Source
const source = await tp.system.suggester(
  ["FabrizioRomano", "DavidOrnstein", "BBCSport", "SkySports", "TheAthletic", "Teamtalk", "Marca", "Other"],
  ["FabrizioRomano", "DavidOrnstein", "BBCSport", "SkySports", "TheAthletic", "Teamtalk", "Marca", "Other"]
);

// News type (determines resolution_status)
const newsType = await tp.system.suggester(
  ["breaking", "transfer", "rumor", "result", "update", "analysis", "opinion"],
  ["breaking", "transfer", "rumor", "result", "update", "analysis", "opinion"]
);

// Date defaults to today
const date = tp.date.now("YYYY-MM-DD");

// For transfer/rumor: generate story_id
let story_stage = "n/a";
let rumor_id = "";

if (newsType === "transfer" || newsType === "rumor") {
  story_stage = "rumor";
  
  // Prompt for player and club
  const player = await tp.system.prompt("Player name?");
  const club = await tp.system.prompt("Club?");
  
  if (player && club) {
    const slug = (player + "-" + club).toLowerCase().replace(/[^a-z0-9]/g, "-").replace(/-+/g, "-");
    story_id = slug + "-" + date;
    rumor_id = slug + "-" + date;
    
    // Store for use in template
    tp.api.vars = { player, club, story_id, rumor_id };
  }
}

// Tags (freeform, comma-separated)
const tags = await tp.system.prompt("Tags? (comma-separated)");
-%>
---
type: news
date: <% date %>
source: <% source %>
url: 
processed: false
entities:
tags: [<% tags || newsType %>]
<% /* Add story fields if applicable */ %>
<% if (story_id) { %>
story_id: <% story_id %>
story_stage: <% story_stage %>
<% } %>
<% if (rumor_id) { %>
rumor_id: <% rumor_id %>
resolution_status: pending
<% } %>
---

# <% source %> — <% date %>

<%* 
// Auto-generate title from entities if provided
if (tp.api.vars && tp.api.vars.player) {
  const player = tp.api.vars.player;
  const club = tp.api.vars.club;
  const stage = story_stage;
-%>
## <% player %> → <% club %> (<% stage %>)

<%* 
}
// Summary section
-%>

## Summary


## Background


## Dataview Queries

### Same story timeline
```dataview
TABLE date, source, story_stage, resolution
FROM "entities/news"
WHERE story_id = "<% story_id || 'TBD' %>"
SORT date ASC
```

### Pending rumors from source
```dataview
LIST
FROM "entities/news"
WHERE source = "<% source %>" AND resolution_status = "pending"
SORT date DESC
```

### All stories involving entity
```dataview
LIST
FROM "entities/news"
WHERE contains(entities, "<% tp.api.vars.player || '' %>")
SORT date DESC
```