# x.com Failures

## 2026-04-25

### Unicode encoding error on Windows

**Error:** `'charmap' codec can't encode character '\u2705' in position 2`

**Cause:** Windows console doesn't support UTF-8 emojis by default.

**Status:** ✅ Fixed - encode/decode with `errors='replace'` before writing to file.

### Selector 'article' returns items but with encoding issues

**Error:** Articles extracted but text contains garbled characters due to Windows cp1252 encoding.

**Status:** ✅ Fixed - added UTF-8 replacement in `_save_tweets`.

### Duplicate tweets extracted

**Cause:** Multiple selectors returning same articles, and same articles appearing multiple times.

**Status:** ⚠️ Needs fix - should deduplicate by link/tweet text.

## Historical (Resolved)

| Issue | Status |
|-------|--------|
| browser_get_tabs returns array | ✅ Fixed |
| JSON parsing without encoding | ✅ Fixed |
| browser_evaluate unknown tool | ✅ Workaround: use browser_query |
| browser_snapshot chrome:// URL | ✅ Fixed: claim tab first |