from playwright.sync_api import sync_playwright
from datetime import datetime
import re
import yaml

class ArticleFilter:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = "C:/Users/jtoem/.config/opencode/skills/browser-agent/_tools/news_signals.yaml"
        
        self.filter_out_patterns = [
            'tracker', 'latest goals', 'score update', 'watchability',
            'depth charts', 'schedule', 'fixtures', 'standings',
            'tables', 'rankings', 'power rankings', 'preview',
            'talking points', 'scout report', 'stat packed',
            'by the numbers', 'form guide', 'team news',
            'predicted lineups', 'injuries', 'suspensions',
            'odds', 'betting tips', 'fantasy', 'game week',
            'match day guide'
        ]
        
        self.filter_in_signals = [
            'BREAKING', 'EXCLUSIVE', 'DONE DEAL', 'HERE WE GO',
            'SIGNED', 'SACKED', 'RELEASED', 'RESIGNS', 'RETIRES',
            'DIED', 'TRAGEDY', 'RECORD', 'MILESTONE', 'HISTORY',
            'BECOMES', 'TRANSFER COMPLETE', 'MEDICAL', 'AGREE',
            'SIGNS FOR', 'JOINS', 'LEAVES', 'SOLD', 'LOAN',
            'APPOINTED', 'DISMISSED', 'INJURED', 'COLLAPSE',
            'HOSPITALIZED', 'CHAMPION', 'QUALIFIED', 'ELIMINATED'
        ]
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config:
                    self.filter_out_patterns = config.get('filter_out', self.filter_out_patterns)
                    self.filter_in_signals = config.get('filter_in', self.filter_in_signals)
        except:
            pass
    
    def should_scrape(self, title, url=''):
        title_lower = title.lower()
        
        for pattern in self.filter_out_patterns:
            if pattern.lower() in title_lower:
                return False, f"Filtered OUT: contains '{pattern}'"
        
        for signal in self.filter_in_signals:
            if signal.lower() in title_lower:
                return True, f"Filtered IN: contains '{signal}'"
        
        if len(title) < 30 or len(title) > 150:
            return False, f"Filtered OUT: title length {len(title)}"
        
        return True, "Filtered IN: passes length check"


class ArticleScraper:
    def __init__(self, source_name, base_url, output_dir):
        self.source_name = source_name
        self.base_url = base_url
        self.output_dir = output_dir
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.filter = ArticleFilter()

    def get_article_links(self, page, homepage, selectors):
        links = []
        domain = homepage.split('/')[2]

        for selector in selectors:
            elements = page.query_selector_all(selector)
            for el in elements:
                href = el.get_attribute('href')
                if href and not href.startswith('#'):
                    if href.startswith('/'):
                        href = f"https://{domain}{href}"
                    elif not href.startswith('http'):
                        href = f"https://{domain}/{href}"

                    if domain in href or (domain in homepage and ('/articles/' in href or '/story/' in href or '/news/' in href)):
                        links.append(href)

        if len(links) < 3:
            all_links = page.query_selector_all('a')
            for l in all_links:
                href = l.get_attribute('href') or ''
                text = l.inner_text().strip()
                if '/articles/' in href and len(text) > 15:
                    full_url = f"https://{domain}{href}" if href.startswith('/') else href
                    links.append(full_url)
            for l in all_links:
                href = l.get_attribute('href') or ''
                text = l.inner_text().strip()
                if '/sport/football/' in href and 'BBC' not in text and len(text) > 20:
                    full_url = f"https://{domain}{href}" if href.startswith('/') else href
                    links.append(full_url)

        return list(set(links))[:15]

    def scrape_article(self, page, url):
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)

        title = ""
        content = ""
        author = ""
        date = ""
        image = ""
        tags = []

        try:
            title_el = page.query_selector('h1')
            if title_el:
                title = title_el.inner_text().strip()
        except:
            pass

        try:
            author_el = page.query_selector('[rel="author"], .author, .byline, [data-testid="byline"]')
            if author_el:
                author = author_el.inner_text().strip()
        except:
            pass

        try:
            date_el = page.query_selector('time[datetime], [data-testid="timestamp"], .date, .timestamp')
            if date_el:
                date = date_el.inner_text().strip()
        except:
            pass

        try:
            img_el = page.query_selector('article img, .article img, main img, [data-testid="image"] img')
            if img_el:
                image = img_el.get_attribute('src') or ""
        except:
            pass

        try:
            paragraphs = page.query_selector_all('article p, .article-body p, .story-body p, main p')
            for p in paragraphs:
                text = p.inner_text().strip()
                if len(text) > 80 and not any(n in text.lower() for n in ['sign in', 'log in', 'subscribe', 'cookie', 'privacy', 'terms']):
                    content += text + "\n\n"
        except:
            pass

        if not content or len(content) < 800:
            try:
                main = page.query_selector('article, main, [role="main"]')
                if main:
                    paragraphs = main.query_selector_all('p')
                    for p in paragraphs:
                        text = p.inner_text().strip()
                        if len(text) > 80:
                            content += text + "\n\n"
            except:
                pass

        content = self.clean_content(content)

        slug = re.sub(r'[^a-zA-Z0-9]', '-', title[:50]).lower()
        filename = f"{self.source_name}-{slug}-{self.date}.md"

        topic_tags = self.extract_tags(title, content)

        md_content = f"""---
source: {self.source_name}
url: {url}
date: {date}
author: {author}
scraped: {self.date}
tags:
{chr(10).join(f'  - {tag}' for tag in topic_tags)}
related: []
---

# {title}

**By:** {author}

**Published:** {date}

**Tags:** {' '.join(f'#{tag}' for tag in topic_tags)}

"""

        if image:
            md_content += f"![Image]({image})\n\n"

        md_content += content
        md_content += "\n\n---\n\n## Related\n"

        return filename, md_content, slug

    def extract_tags(self, title, content):
        tags = []
        text = (title + " " + content[:1000]).lower()

        tag_map = {
            'world cup': 'WorldCup2026',
            'uefa': 'UEFA',
            'europe': 'EuropeanFootball',
            'champions league': 'ChampionsLeague',
            'premier league': 'PremierLeague',
            'la liga': 'LaLiga',
            'seria': 'SerieA',
            'bundesliga': 'Bundesliga',
            'ligue 1': 'Ligue1',
            'football': 'football',
            'soccer': 'football',
            'transfer': 'Transfers',
            'ronaldo': 'Ronaldo',
            'messi': 'Messi',
            'mbappe': 'Mbappe',
            'al nassr': 'AlNassr',
            'saudi': 'SaudiProLeague',
            'portugal': 'Portugal',
            'argentina': 'Argentina',
            'brazil': 'Brazil',
            'england': 'England',
            'france': 'France',
            'germany': 'Germany',
            'italy': 'Italy',
            'spain': 'Spain',
            'qualifier': 'Qualifiers',
            'goal': 'Goals',
            'record': 'Records',
            'score': 'Goals',
        }

        for keyword, tag in tag_map.items():
            if keyword in text:
                tags.append(tag)

        return list(set(tags))[:8]

    def clean_content(self, content):
        if not content:
            return content
        lines = content.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if any(x in line.lower() for x in ['sign in', 'log in', 'subscribe now', 'cookie policy', 'privacy notice', 'terms and conditions', 'get sky sports', 'download the app', 'follow us on']):
                continue
            if line.startswith('You can now') or line.startswith('This is a modal'):
                continue
            if len(line) < 30:
                continue
            cleaned.append(line)
        return '\n\n'.join(cleaned)

    def run(self, homepage, link_selectors, max_articles=5):
        domain = homepage.split('/')[2]
        
        if not link_selectors:
            link_selectors = [
                'article a',
                'a[href*="/news/"]',
                'a[href*="/story/"]',
                'h2 a',
                'h3 a',
                '.headline a',
                '.article-card a'
            ]
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(homepage)
            page.wait_for_timeout(3000)

            links = self.get_article_links(page, homepage, link_selectors)
            print(f"Found {len(links)} article links")

            scraped_files = []
            
            for i, url in enumerate(links):
                try:
                    page.goto(url)
                    page.wait_for_timeout(1000)
                    title_el = page.query_selector('h1')
                    if not title_el:
                        continue
                    title = title_el.inner_text().strip()
                    
                    should_scrape, reason = self.filter.should_scrape(title, url)
                    print(f"Checking {i+1}: {title[:50]}... - {reason}")
                    
                    if not should_scrape:
                        continue
                    
                    filename, content, slug = self.scrape_article(page, url)
                    filepath = f"{self.output_dir}/{filename}"
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    scraped_files.append((filename, slug))
                    print(f"  SAVED: {filename}")
                    
                    if len(scraped_files) >= max_articles:
                        break
                        
                except Exception as e:
                    print(f"  Error: {e}")

            for filename, slug in scraped_files:
                self.add_related_links(f"{self.output_dir}/{filename}", scraped_files, slug)

            browser.close()

        return f"Scraped {len(scraped_files)} articles"

    def add_related_links(self, filepath, all_files, current_slug):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            related = [(slug, filename) for filename, slug in all_files if slug != current_slug][:3]

            if related:
                link_section = "\n## Related\n\n"
                for slug, filename in related:
                    note_name = filename.replace('.md', '')
                    link_section += f"- [[{note_name}]]\n"
                
                if "## Related" not in content:
                    content += link_section
                else:
                    for slug, filename in related:
                        note_name = filename.replace('.md', '')
                        if f"[[{note_name}]]" not in content:
                            content = content.replace("## Related\n\n", f"## Related\n\n- [[{note_name}]]\n")

                import re
                content = re.sub(r'related:\s*\[\s*\]', f'related:\n  - {"\n  - ".join([s for s, _ in related])}', content)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  Linked: {filepath.split('/')[-1]}")
        except Exception as e:
            print(f"  Link error: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python scrape_articles.py <source_name> <homepage> [output_dir] [max_articles]")
        sys.exit(1)

    source = sys.argv[1]
    homepage = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "."
    max_art = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    scraper = ArticleScraper(source, "", output)
    scraper.run(homepage, ['a[href*="story"]', 'a[href*="article"]', 'h2 a', 'h3 a'], max_art)