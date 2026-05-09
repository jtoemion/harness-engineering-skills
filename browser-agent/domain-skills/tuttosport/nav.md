# Tuttosport Navigation Recipes

## Homepage Navigation

```javascript
// Navigate to Tuttosport homepage
async (page) => {
  await page.goto('https://www.tuttosport.com/');
  await page.waitForLoadState('networkidle');
}
```

## Football Section Recipes

### Navigate to Football Hub
```javascript
async (page) => {
  await page.goto('https://www.tuttosport.com/football');
  await page.waitForLoadState('networkidle');
}
```

### Navigate to Team Pages
```javascript
// Juventus (most common target)
async (page) => {
  await page.goto('https://www.tuttosport.com/football/juventus');
}

async (page) => {
  await page.goto('https://www.tuttosport.com/football/inter');
}

async (page) => {
  await page.goto('https://www.tuttosport.com/football/milan');
}
```

### Navigate to League Pages
```javascript
// Serie A
async (page) => {
  await page.goto('https://www.tuttosport.com/football/serie-a');
}

// Serie B
async (page) => {
  await page.goto('https://www.tuttosport.com/football/serie-b');
}

// Champions League
async (page) => {
  await page.goto('https://www.tuttosport.com/football/champions-league');
}
```

## Motorsport Navigation

### Formula 1
```javascript
async (page) => {
  await page.goto('https://www.tuttosport.com/motorsport/formula-1');
}
```

### MotoGP
```javascript
async (page) => {
  await page.goto('https://www.tuttosport.com/motorsport/motogp');
}
```

## Basketball Navigation

### Serie A Basket
```javascript
async (page) => {
  await page.goto('https://www.tuttosport.com/basketball/serie-a');
}
```

## Search Recipe

```javascript
// Search Tuttosport
async (page, { query }) => {
  const searchUrl = `https://www.tuttosport.com/search?q=${encodeURIComponent(query)}`;
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
  await page.goto(`https://www.tuttosport.com/article/${articleId}`);
  await page.waitForLoadState('networkidle');
}
```

## Navigation by Main Menu

```javascript
// Navigate using main menu
async (page, { section }) => {
  await page.goto('https://www.tuttosport.com/');
  await page.waitForLoadState('networkidle');
  
  const menuMap = {
    'calcio': 'a[href="/football"]',
    'motori': 'a[href="/motorsport"]',
    'basket': 'a[href="/basketball"]',
    'juve': 'a[href="/football/juventus"]'
  };
  
  const selector = menuMap[section] || menuMap['calcio'];
  await page.click(selector);
  await page.waitForLoadState('networkidle');
}
```