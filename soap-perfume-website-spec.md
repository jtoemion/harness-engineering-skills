# Soap & Perfume Website — Ideal Spec

## References
- https://www.soapmomento.com/ — handcrafted all-natural soap brand; clean editorial style, founder-forward storytelling, zero-waste positioning

---

## 1. Visual Identity & Aesthetic

### Tone
- **Handcrafted/natural brands** (soapmomento, Erbavita): earthy warm tones, editorial photography, founder-driven narrative, hand-lettering accents
- **Luxury/clean beauty** (Aesop, Glossier): minimal layout, serif typography, generous whitespace, muted palettes
- **Perfume/niche** (Commozion, Jorum Studio): dark or monochrome backgrounds, bold typography, art-gallery aesthetic

### Color Palette
| Role | Example |
|---|---|
| Background | Warm cream `#FAF7F2`, off-white `#F5F0EB` |
| Primary accent | Terracotta `#C4816A`, sage green `#8B9E7C` |
| Secondary | Deep charcoal `#2C2C2C`, warm taupe `#B8A99A` |
| Perfume/luxury | Near-black `#1A1A1A`, gold `#C9A84C` |

### Typography
- Headings: **Playfair Display** or **DM Serif Display** (editorial/luxury)
- Body: **Lato**, **Inter**, or **Source Sans 3** (readable, clean)
- Accent/labels: **Cormorant Garamond** (perfume), **caveat** (handwritten feel for soap)

### Imagery
- Hero: lifestyle photography showing product in use / natural ingredients
- Product: consistent studio shots — white or neutral background, soft shadow
- Ingredient close-ups: macro texture shots of clay, botanicals, oils
- No stock-photo feel — authenticity > polish

---

## 2. Key Page Sections

### Homepage
1. **Announcement bar** — shipping policy, subscription promo, seasonal offer
2. **Hero slideshow** — 1–3 slides; product feature or brand story with CTA ("Shop Now")
3. **Founder/brand story block** — 2–4 paragraphs; "why we exist" narrative with authentic voice (see soapmomento's "The Path to Authentic All-Natural Living")
4. **Collections grid** — category cards with icon or image (Face+Body Soap, Shampoo Bars, Eco Dish Bars, Accessories, Tallow, etc.)
5. **Best Sellers** — horizontal scroll/carousel; 4–8 products with name + price
6. **Trust signals** — "Our promise" (Clean / Healthy / Sustainable) with icons; 4–6 benefits
7. **Social proof** — star rating aggregate ("from 525 reviews"), featured testimonial
8. **Blog preview** — latest 2–3 posts
9. **Newsletter signup** — email capture with incentive (discount or free shipping)
10. **Footer** — Shop / Info / Legal / Social columns

### Shop / Collection Page
- Filter sidebar: category, price range, skin type, scent family, ingredients (e.g., "palm-oil-free", "essential oils only")
- Sort: Best Selling, Price (asc/desc), Newest, Rating
- Grid: 2–4 columns desktop, 2 columns mobile
- Quick-add to cart on hover
- Sale badges, "new" badges, "sold out" states

### Product Detail Page (PDP)
1. **Image gallery** — main image + thumbnails (2–8 images); zoom on hover; video optional
2. **Product title + star rating** (aggregate + count)
3. **Price** (with compare-at if on sale)
4. **Short description** — scent profile, key benefits
5. **Quantity selector + Add to Cart button** (sticky on mobile)
6. **Subscription / Subscribe & Save** toggle
7. **Product details accordion** — full ingredient list (INCI names), skin type suitability, how to use, care instructions
8. **Ingredients highlight** — "Key Ingredients" callout with benefits
9. **Scent notes** — top/middle/base pyramid (for perfume)
10. **FAQ accordion** — common objections (e.g., "Is this safe for sensitive skin?")
11. **Reviews section** — with photos, verified badge, filter by rating
12. **Related products** — "You may also like"
13. **Trust badges** — "Palm-oil free", "Cruelty-free", "Vegan", "Eco-packaging"

### Cart / Checkout
- Cart drawer (slide-in) or cart page
- Line items: image, name, variant, qty, price, remove
- Order summary: subtotal, shipping estimate, discount code field
- Checkout: guest + account; address autocomplete; express pay (Shop Pay, Apple Pay, Google Pay)
- SSL badge, accepted payment icons

### About / Meet the Maker
- Founder story — photo, bio, philosophy
- "Why we make it this way" — process (cold process, hot process, etc.)
- Ingredient sourcing story
- Sustainability commitments

### Blog
- Categories: Ingredient education, Skin care routines, Sustainability, Behind the scenes
- Recipe/how-to posts (e.g., "How to extend the life of your shampoo bar")
- SEO-targeted informational content

### Contact / FAQ
- Simple form or chat widget
- FAQ with search
- Shipping policy, return policy as standalone pages

---

## 3. Essential Features

### Commerce
- [ ] Shopify or WooCommerce (self-hosted flexibility)
- [ ] Inventory management with variants (scent, size)
- [ ] Real-time shipping rate calculation
- [ ] Tax calculation (Stripe Tax, TaxJar)
- [ ] Discount / promo codes
- [ ] Subscription model (reorder frequency)
- [ ] Wishlist / save for later

### Trust & Compliance
- [ ] Cookie consent banner (GDPR, CCPA)
- [ ] Privacy policy, terms of service
- [ ] Accessible: WCAG 2.1 AA (alt text, keyboard nav, color contrast)
- [ ] Age verification for fragrance alcohol content (optional popup)

### Performance
- [ ] Core Web Vitals: LCP < 2.5s, CLS < 0.1, FID < 100ms
- [ ] Lazy-load images below fold
- [ ] Responsive: mobile-first
- [ ] Image optimization: WebP, srcset
- [ ] CDN for assets

### Security
- [ ] HTTPS everywhere
- [ ] PCI-DSS compliant checkout (Stripe/Shopify handle this)
- [ ] Bot protection on forms (honeypot, CAPTCHA)

---

## 4. Constraints

| Constraint | Detail |
|---|---|
| **Ingredient regulation** | INCI naming required on EU/UK; allergen disclosure (Linalool, Limonene, etc.) |
| **Claims substantiation** | "Natural", "organic", "cruelty-free" require evidence; EU Cosmetics Regulation bans unsubstantiated claims |
| **Shipping hazmat** | Perfume/fragrance oils may be hazmat; need proper IATA labeling for air freight |
| **Packaging laws** | Extended Producer Responsibility (EPR) in EU; cosmetic packaging regulations |
| **Subscription billing** | Must disclose terms clearly; easy cancellation required |
| **Age-gating** | Some fragrance ingredients (denatured alcohol) may require age verification |
| **Photo accuracy** | Soap appearance varies batch-to-batch; don't imply identical product to stock photo |
| **Budget** | Small artisan brand — avoid over-engineering; Shopify + a well-chosen theme gets to market faster than custom build |
| **Scale** | Start with Shopify Basic; upgrade as volume demands |

---

## 5. SEO Gold Features

### Technical
- [ ] Schema.org markup: `Product`, `Offer`, `AggregateRating`, `BreadcrumbList`, `FAQPage`
- [ ] Open Graph + Twitter Card meta for all pages
- [ ] Canonical URLs (no duplicate content across variants)
- [ ] XML sitemap + `sitemap_index.xml`
- [ ] `robots.txt` with proper allow/disallow
- [ ] Core Web Vitals in green — Google uses as ranking signal
- [ ] Mobile-first indexing (responsive design)
- [ ] HTTPS + HSTS preload

### On-Page Content
- [ ] Product titles: descriptive + keyword (e.g., "Lavender & Kaolin Clay Cold Process Soap Bar — 4oz")
- [ ] Meta descriptions: unique per page, 150–160 chars, include CTA + keyword
- [ ] H1 = product/collection name; single H1 per page
- [ ] Image alt text: descriptive, keyword-included (not "IMG_1234.jpg")
- [ ] Internal linking: blog → product, collection → product, related items
- [ ] FAQ section: targets "people also ask" featured snippets
- [ ] Comparison pages: "Best soap for oily skin", "Shampoo bar vs. liquid shampoo"
- [ ] "What is cold process soap?" educational content → topical authority

### Content & Authority
- [ ] Blog with consistent publishing (ingredient deep-dives, routines, sustainability)
- [ ] Product reviews — user-generated content is ranking gold
- [ ] "How to extend the life of your soap bar" type articles (long-tail traffic)
- [ ] Backlinks: supplier relationships (ingredient brands), natural beauty directories
- [ ] Google Business Profile (local SEO for artisan brand)
- [ ] Pinterest / Instagram as visual search traffic sources

### Perfume-Specific SEO
- [ ] Scent pyramid: top/middle/base notes as structured content
- [ ] "Fragrance family" taxonomy: floral, oriental, woody, fresh, citrus, chypre, fougère
- [ ] Seasonality: "Best summer fragrances 2025" — editorial content
- [ ] Dupe / inspiration: "If you like X, try Y" — internal linking + long-tail keywords

### Local Artisan / Small Brand
- [ ] "Handmade in [city/state]" in title tag and footer
- [ ] Local business schema
- [ ] Reviews on Google Business Profile
- [ ] Press / media mentions as citations

---

## 6. Recommended Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Platform | **Shopify** | Fastest time-to-market, PCI compliant, built-in checkout, liquid theming for customization |
| Theme | **Dawn** (free, Shopify native) or **Prestige** (premium, editorial) | Clean, fast, mobile-first |
| Hosting | Shopify (managed) | No server运维 |
| Payments | Shopify Payments / Stripe | Apple Pay, Google Pay, Shop Pay |
| Reviews | **Judge.me** or **Yotpo** | Schema-ready, photo reviews |
| Subscription | **Recharge** or native Shopify Subscriptions | Handles notify/skubscribe |
| Analytics | GA4 + GTM + Shopify Analytics | |
| Email | Klaviyo | Best Shopify integration for abandoned cart, post-purchase flows |
| SEO / Speed | Shopify's built-in CDN + ShopifyQL for search analytics |

> For a custom build (React/Node, not Shopify): **Next.js + Shopify Storefront API + Stripe** — higher dev cost, full control. Not recommended for initial launch.

---

## 7. Soap vs. Perfume — Subtle Differences

| Aspect | Soap Brand | Perfume Brand |
|---|---|---|
| Hero tone | Authenticity, maker story, ingredient purity | Emotion, mood, identity, sillage |
| Product copy | Ingredient-first, skin benefit | Scent journey, memory, occasion |
| Photography | Soap in context, texture, lather | Bottle alone (art object), moody editorial |
| Subscription | "Never run out of your favorite bar" | "Your signature scent, refilled" |
| Price anchoring | "$14 bar — lasts 3–4 weeks" | 50ml / 100ml / 200ml with cost-per-ml |
| Social proof | "My skin has never felt better" | "I get compliments every time I wear this" |
| Compliance hot-spot | Allergen disclosure (EU) | IFRA compliance for fragrance materials |
