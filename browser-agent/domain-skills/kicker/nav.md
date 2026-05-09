# Kicker Navigation Recipes

## Homepage Navigation

```javascript
// Navigate to Kicker homepage
async (page) => {
  await page.goto('https://www.kicker.de/');
  await page.waitForLoadState('networkidle');
}
```

## Football Section Recipes

### Navigate to Football Hub

```javascript
async (page) => {
  await page.goto('https://www.kicker.de/fussball/');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to Bundesliga

```javascript
// Bundesliga standings/match schedule
async (page) => {
  await page.goto('https://www.kicker.de/bundesliga/spielplan');
  await page.waitForLoadState('networkidle');
}

// Bundesliga matches live
async (page) => {
  await page.goto('https://www.kicker.de/bundesliga/live-ticker');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to 2. Bundesliga

```javascript
async (page) => {
  await page.goto('https://www.kicker.de/2-bundesliga/spielplan');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to DFB-Pokal

```javascript
async (page) => {
  await page.goto('https://www.kicker.de/dfb-pokal/spielplan');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to Champions League

```javascript
async (page) => {
  await page.goto('https://www.kicker.de/champions-league/spielplan');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to Europa League

```javascript
async (page) => {
  await page.goto('https://www.kicker.de/europa-league/spielplan');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to Transfer News

```javascript
async (page) => {
  await page.goto('https://www.kicker.de/transfers');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to National Team

```javascript
// German National Team
async (page) => {
  await page.goto('https://www.kicker.de/deutschland');
  await page.waitForLoadState('networkidle');
}

// DFB Team news
async (page) => {
  await page.goto('https://www.kicker.de/dfb-pokal/deutschland');
  await page.waitForLoadState('networkidle');
}
```

## Search Recipe

```javascript
// Search Kicker
async (page, { query }) => {
  const searchUrl = `https://www.kicker.de/suche?q=${encodeURIComponent(query)}`;
  await page.goto(searchUrl);
  await page.waitForLoadState('networkidle');
}
```

## Common Article Navigation

```javascript
// Click first article on section page
async (page) => {
  const articleLinks = await page.locator('article a, [data-article] a, .article-item a').all();
  if (articleLinks.length > 0) {
    await articleLinks[0].click();
    await page.waitForLoadState('networkidle');
  }
}

// Navigate to specific article by URL pattern
async (page, { articleId }) => {
  await page.goto(`https://www.kicker.de/article/${articleId}`);
  await page.waitForLoadState('networkidle');
}
```

## Navigation by Main Menu

```javascript
// Navigate using main menu
async (page, { section }) => {
  await page.goto('https://www.kicker.de/');
  await page.waitForLoadState('networkidle');
  
  const menuMap = {
    'fussball': 'a[href="/fussball"]',
    'bundesliga': 'a[href="/bundesliga"]',
    '2-bundesliga': 'a[href="/2-bundesliga"]',
    'dfb-pokal': 'a[href="/dfb-pokal"]',
    'champions-league': 'a[href="/champions-league"]',
    'transfers': 'a[href="/transfers"]'
  };
  
  const selector = menuMap[section] || menuMap['fussball'];
  await page.click(selector);
  await page.waitForLoadState('networkidle');
}
```

## Team-Specific Pages

```javascript
// Bayern Munich
async (page) => {
  await page.goto('https://www.kicker.de/fc-bayern-muenchen/spielplan');
  await page.waitForLoadState('networkidle');
}

// Borussia Dortmund
async (page) => {
  await page.goto('https://www.kicker.de/borussia-dortmund/spielplan');
  await page.waitForLoadState('networkidle');
}

// RB Leipzig
async (page) => {
  await page.goto('https://www.kicker.de/rb-leipzig/spielplan');
  await page.waitForLoadState('networkidle');
}

// Other common teams
async (page, { team }) => {
  const teamUrls = {
    'bayern': 'fc-bayern-muenchen',
    'dortmund': 'borussia-dortmund',
    'leipzig': 'rb-leipzig',
    'leverkusen': 'bayer-04-leverkusen',
    'gladbach': 'borussia-moenchengladbach',
    'wolfsburg': 'vfl-wolfsburg',
    'frankfurt': 'eintracht-frankfurt',
    'union': '1-fc-union-berlin',
    'hertha': 'hertha-bsc',
    'sc Freiburg': 'sc-freiburg',
    'mainz': '1-fc-mainz-05',
    'koeln': '1-fc-koeln',
    'bremen': 'werder-bremen',
    'hoffenheim': 'tsg-1899-hoffenheim',
    'bochum': 'vfl-bochum',
    'darmstadt': 'sv-darmstadt-98'
  };
  
  const teamSlug = teamUrls[team.toLowerCase()];
  if (teamSlug) {
    await page.goto(`https://www.kicker.de/${teamSlug}/spielplan`);
    await page.waitForLoadState('networkidle');
  }
}
```

## Match Center

```javascript
// Live ticker / live score
async (page) => {
  await page.goto('https://www.kicker.de/liveticker');
  await page.waitForLoadState('networkidle');
}

// Match center for specific game
async (page, { matchId }) => {
  await page.goto(`https://www.kicker.de/liveticker/${matchId}`);
  await page.waitForLoadState('networkidle');
}
```

## Bundesliga Specific Recipes

### Get Matchday

```javascript
// Current Bundesliga matchday
async (page) => {
  await page.goto('https://www.kicker.de/bundesliga/spieltag/meisterstadt/34');
  await page.waitForLoadState('networkidle');
}
```

### Get Table/Standings

```javascript
// Bundesliga table
async (page) => {
  await page.goto('https://www.kicker.de/bundesliga/staende');
  await page.waitForLoadState('networkidle');
}
```