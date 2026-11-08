# PRD: SoloCorp OS Official Website

> **ขอบเขต:** เอกสารนี้เป็น PRD ของเว็บไซต์สาธารณะ/การตลาดเท่านั้น ไม่ใช่ PRD ของ web app ที่ผู้ใช้จัดการ CEO และ department MCP. Product app roadmap ปัจจุบันอยู่ใน [`PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md`](PRD-SOLOCORP-LOCAL-FIRST-MCP-APP-MVP-v1.0.md).

| Meta | Value |
|:-----|:------|
| **Product** | SoloCorp OS Official Website |
| **Status** | Draft v1 — Future Plan (Q3–Q4 2026) |
| **Owner** | Product (โปรดัค) |
| **Design Lead** | Design (ครีเอท) |
| **Engineering Lead** | Engineering (ช่างฟูล) |
| **Content Lead** | Content Creator (เสก) |
| **Approval** | CEO (หนุมาน) |
| **Target Launch** | Q3 2026 – Q4 2026 (รอความพร้อม) |

---

## 1. Problem Statement

### ปัจจุบัน

SoloCorp OS มีเนื้อหาทางเทคนิคและแนวคิดกระจายอยู่ทั่วไป:

- **GitHub README** — จำกัดพื้นที่ ไม่สามารถเล่าเรื่องราวแบรนด์ได้
- **Brand Foundation Doc** — ใช้ภายใน ไม่มีหน้าแสดงต่อสาธารณะ
- **Legal Vault + Templates** — อยู่ลึกใน repo ไม่มีหน้าให้ download
- **Blog / News** — ไม่มีที่ publish ประกาศอย่างเป็นทางการ

### ผลกระทบ

- คนภายนอกเจอ SoloCorp OS ครั้งแรกจาก GitHub → เข้าใจแค่ code ไม่เข้าใจ vision และปรัชญา
- ไม่มี "ที่แรก" ที่ unified สำหรับทุกคนที่ต้องการรู้จักเรา
- Content marketing ไม่มี landing page ที่ anchor — ทุกแคมเปญต้องสร้างหน้าเฉพาะกิจ
- Legal templates ไม่ discoverable — คนที่อยากใช้ license ของเราหาไม่เจอ
- ไม่มี docs portal สำหรับ onboarding ผู้ใช้ใหม่

### เป้าหมาย

> เว็บไซต์นี้คือ **สถานทูตของ SoloCorp OS บนอินเทอร์เน็ต** — ทุกคนที่เจอเราควรรู้สึกว่า
> "นี่คือสิ่งที่จริงจัง มีระบบ และน่าเชื่อถือ"

---

## 2. Objectives & Success Metrics

### Objectives

| # | Objective | Stakeholder |
|:-:|:----------|:------------|
| O1 | สร้าง first impression ที่แข็งแกร่ง — คนที่มา first visit เข้าใจ SoloCorp OS ภายใน 30 วินาที | CEO, CMO |
| O2 | เป็น single source of truth สำหรับทุกเรื่องเกี่ยวกับ SoloCorp OS (docs, news, legal, brand) | CEO, Product |
| O3 | ขับเคลื่อน traffic ไปยัง GitHub repo (star, fork, contribute) | CMO, Engineering |
| O4 | สร้าง credibility สำหรับ enterprise inquiries | Sales, CEO |
| O5 | รองรับการเติบโต — เพิ่ม content, blog, docs โดยไม่ redesign ใหม่ | Product, Engineering |

### Success Metrics

| Metric | Target | Measurement |
|:-------|:-------|:------------|
| **Bounce Rate** | < 40% (first-time visitors) | Google Analytics |
| **Time on Page** | > 90 วินาที (Hero + What is SoloCorp) | GA / Plausible |
| **GitHub Stars Δ** | +20% MoM หลัง launch | GitHub API |
| **CTA Click Rate** (GitHub / Get Started) | > 8% | GA Event Tracking |
| **Pages/Session** | > 2.5 pages | GA |
| **Lighthouse Score** | > 95 (ทั้ง Desktop และ Mobile) | Lighthouse CI |
| **SEO — "AI Agent OS" ranking** | Top 5 ภายใน 90 วัน | Google Search Console |

---

## 3. Target Audience (4 Tiers)

### Tier 1: Solo Developers (~70% ของ traffic)

- **ใคร:** นักพัฒนาเดี่ยว, indie hacker, freelancer ที่กำลังเจอ limit ของ AI agent ตัวเดียว
- **Pain:** อยาก scale output แต่จ้างคนเพิ่มไม่ได้ — AI agents พังเมื่อโปรเจกต์ซับซ้อน
- **สิ่งที่ต้องการจากเว็บ:** เข้าใจ concept เร็ว → เห็น architecture → ไป GitHub → ลองใช้
- **Key Pages:** Hero → What is SoloCorp → Architecture → GitHub CTA

### Tier 2: Small Teams (~20%)

- **ใคร:** ทีม 2-10 คน, startup ระยะแรก
- **Pain:** ต้องการ organization structure โดยไม่เพิ่ม management overhead
- **สิ่งที่ต้องการจากเว็บ:** Case studies / use cases → docs → pricing (ถ้ามี)
- **Key Pages:** Docs → Blog (use cases) → Contact Sales

### Tier 3: AI Engineers / Agent Builders (~10%)

- **ใคร:** วิศวกรที่ออกแบบ multi-agent systems
- **Pain:** ปัญหา orchestration, context management, routing
- **สิ่งที่ต้องการจากเว็บ:** Technical depth → architecture detail → GitHub → docs
- **Key Pages:** Architecture → Docs → GitHub → Open Source

### Tier 4: Enterprise (Future)

- **ใคร:** องค์กรที่สนใจ AI organization design
- **สิ่งที่ต้องการจากเว็บ:** Credibility → case studies → legal → ติดต่อ
- **Key Pages:** Legal Vault → Blog → Contact

---

## 4. User Stories

### US-01: Developer รู้จัก SoloCorp OS ครั้งแรก

> "ในฐานะ **solo developer** ที่กำลังมองหา solution สำหรับ AI agent orchestration
> ฉันต้องการ **เห็น Hero section ที่สื่อสาร value proposition ภายใน 5 วินาที**
> เพื่อที่จะ **ตัดสินใจว่าใช่สิ่งที่ฉันกำลังมองหาหรือไม่**"

**Acceptance Criteria:**
- Hero มี tagline, CTA "Get Started", link "See Architecture"
- โหลด < 1.5 วินาที (LCP)
- Mobile responsive — ทุก element ดูดีบนมือถือ

### US-02: Researcher ศึกษา architecture

> "ในฐานะ **AI engineer** ที่กำลังออกแบบ multi-agent system
> ฉันต้องการ **เห็น architecture diagram และ department structure ที่ละเอียด**
> เพื่อที่จะ **ประเมินว่า SoloCorp OS ใช้กับ use case ของฉันได้ไหม**"

**Acceptance Criteria:**
- 18 departments แสดงเป็น visual overview
- Click แต่ละ department → รายละเอียด
- Pipeline flow diagram แบบ interactive
- รองรับ responsive โดย architecture diagram ยัง readable

### US-03: เรียนรู้ปรัชญาการออกแบบ

> "ในฐานะ **ผู้สนใจทั่วไป** ที่เห็น SoloCorp OS ครั้งแรก
> ฉันต้องการ **อ่าน The Way และ Core Values**
> เพื่อที่จะ **เข้าใจว่าเบื้องหลังโปรเจกต์นี้มีอะไร และเชื่อถือได้ไหม**"

**Acceptance Criteria:**
- Section "The Way" แสดง 3 แก่น: ซื่อตรง กลมกลืน พร้อม
- Quote "รากไม้แข็งแรงกว่าน้ำที่ไหลผ่าน"
- Core Values 5 ข้อแสดงละเอียด

### US-04: Download legal templates

> "ในฐานะ **developer** ที่อยากใช้ SoloCorp OS ในโปรเจกต์ commercial
> ฉันต้องการ **เข้าถึง Legal Vault และ templates ต่างๆ**
> เพื่อที่จะ **เลือก license ที่เหมาะสม และมั่นใจว่าใช้ได้ตามกฎหมาย**"

**Acceptance Criteria:**
- Legal Vault แสดง 8 templates
- Preview content ก่อน download
- Download เป็นไฟล์ .md หรือ .pdf

### US-05: ติดตามข่าวสารและ blog

> "ในฐานะ **community member** ที่สนใจ SoloCorp OS
> ฉันต้องการ **อ่าน blog / news / announcements**
> เพื่อที่จะ **ติดตามความคืบหน้าและอัปเดตล่าสุด**"

**Acceptance Criteria:**
- Blog list page แสดง title, date, preview, tag
- RSS feed support
- Searchable
- Shareable URL

### US-06: เริ่มต้นใช้งาน

> "ในฐานะ **developer** ที่ตัดสินใจลอง SoloCorp OS
> ฉันต้องการ **เห็น docs / getting started guide**
> เพื่อที่จะ **setup environment และ run pipeline แรกของฉัน**"

**Acceptance Criteria:**
- Getting Started section — step-by-step
- Link ไปยัง full docs (ถ้ามีแยก)
- Code snippets (copy button)

### US-07: ดู open source / contribute

> "ในฐานะ **open source contributor**
> ฉันต้องการ **เห็น GitHub stats, contribution guide, และ README**
> เพื่อที่จะ **decide ว่าจะ star, fork, หรือ contribute**"

**Acceptance Criteria:**
- GitHub stats: stars, forks, open issues (real-time via API)
- Link: "View on GitHub"
- Contribution guide highlight

---

## 5. Feature List

### P0 — Must Have (MVP)

| # | Feature | Description | User Story |
|:-:|:--------|:------------|:-----------|
| F1 | Hero Section | Logo + Tagline + CTA + Animation | US-01 |
| F2 | "What is SoloCorp OS" | ปรัชญา + วิสัยทัศน์ใน 2-3 ย่อหน้า | US-01 |
| F3 | Architecture Overview | 18 departments visual + pipeline flow | US-02 |
| F4 | The Way Section | ปรัชญาการออกแบบ + Core Values 5 ข้อ | US-03 |
| F5 | GitHub CTA | Stats + "View on GitHub" | US-07 |
| F6 | Responsive Design | Mobile-first, ทุก section ดูดีทุก size | US-01, US-02 |
| F7 | Dark Theme | Navy Enterprise palette | ALL |
| F8 | Navigation | Sticky nav — smooth scroll / page nav | ALL |

### P1 — Should Have (V1.1)

| # | Feature | Description | User Story |
|:-:|:--------|:------------|:-----------|
| F9 | Legal Vault | 8 templates — preview + download | US-04 |
| F10 | Blog / News | List page + individual post | US-05 |
| F11 | Getting Started | Step-by-step setup guide | US-06 |
| F12 | Contact / Community | Contact form + Discord/Twitter/X links | US-04, US-05 |
| F13 | SEO Meta | Open Graph, JSON-LD, sitemap.xml | ALL |
| F14 | i18n (EN) | ภาษาอังกฤษ สำหรับ global audience | ALL |

### P2 — Nice to Have (Post Launch)

| # | Feature | Description |
|:-:|:--------|:------------|
| F15 | Interactive Pipeline Demo | Sandbox ที่ลองรัน pipeline ได้ |
| F16 | Case Studies | ตัวอย่างการใช้งาน / use cases |
| F17 | Search | Full-text search ใน docs + blog |
| F18 | RSS Feed | สำหรับ blog posts |
| F19 | Analytics Dashboard | Public stats (stars, downloads) |
| F20 | Dark/Light Toggle | Switch theme |
| F21 | Hero Animation | Canvas/Three.js interactive background |

---

## 6. Content Architecture (Sitemap)

```
solocorp.dev/
├── index.html                    # Home — Hero + What is + The Way + Architecture Preview
├── architecture/
│   ├── overview.html             # 18 departments + pipeline diagram
│   ├── pipeline.html             # Full pipeline documentation
│   └── departments/
│       └── {dept}.html           # Per-department detail (optional)
├── the-way.html                  # ปรัชญาเต็ม + Core Values
├── docs/
│   ├── getting-started.html      # Setup guide
│   └── ...                       # (อาจเป็น subdomain หรือ separate docs site)
├── legal/
│   └── vault.html                # Legal Vault — 8 templates
├── blog/
│   ├── index.html                # Blog list
│   └── {slug}.html               # Blog post
├── community.html                # Community links + contact
├── 404.html
└── assets/
    ├── css/
    ├── js/
    ├── images/
    └── fonts/
```

### Navigation Structure (Primary)

```
[Logo]  Architecture  The Way  Docs  Legal  Blog  Community  [GitHub]
```

### Navigation Structure (Mobile — Hamburger)

- Same items + "View on GitHub" CTA แยก

---

## 7. Design Direction

### Palette (Navy Enterprise — Locked)

| Token | Hex | Usage |
|:------|:----|:------|
| `--color-base` | `#0F172A` | Background (navy) |
| `--color-surface` | `#1E293B` | Cards, sections |
| `--color-border` | `#334155` | Borders, dividers |
| `--color-accent` | `#3B82F6` | Primary accent (CTA, links) |
| `--color-indigo` | `#6366F1` | Secondary accent |
| `--color-text` | `#F8FAFC` | Primary text |
| `--color-text-muted` | `#94A3B8` | Secondary text |
| `--color-success` | `#22C55E` | Success / active state |

### Typography

- **Headers:** Inter (Variable) — `font-weight: 600-800`
- **Body:** Inter — `400`, `500`
- **Code:** JetBrains Mono
- **Thai:** Noto Sans Thai — fallback สำหรับเนื้อหาภาษาไทย
- **Scale:** `clamp()` based fluid type — `text-sm` ถึง `text-6xl`

### Design Principles

1. **Dark-first** — ไม่ใช่ light mode ที่ใส่ dark skin แต่ dark เป็น default identity
2. **Content is king** — typography และ whitespace นำสายตา ไม่ใช่ decoration
3. **Gradient accents** — `#3B82F6 → #6366F1` gradient สำหรับ hero และ dividers
4. **Glass morphism** — `backdrop-blur` สำหรับ nav และ cards (depth)
5. **Micro-interactions** — hover, transition, scroll-triggered animation
6. **Hexagon motif** — references to logo (section dividers, icons)

### Logo Variants

- **Primary:** Hexagon Nexus (light bg) — ใช้ใน nav
- **Icon:** Simplified hexagon — favicon
- **Favicon:** SVG favicon + PNG fallback

### Referenced Design Systems (Inspiration)

- **Linear.app** — dark-first, clean, typography-driven
- **Vercel** — geometric, structured, content-first
- **Stripe** — gradient accents, glass morphism
- **Anthropic** — authoritative, minimal

---

## 8. Technical Considerations

### Stack Recommendation

| Layer | Option A (แนะนำ) | Option B |
|:------|:----------------|:---------|
| **Framework** | Astro (Static Site + islands) | Next.js SSG |
| **Styling** | Tailwind CSS v4 | Panda CSS |
| **Animation** | GSAP / Framer Motion | CSS Animations |
| **Content** | Markdown (Astro Content Collections) | MDX + Frontmatter |
| **Deploy** | Cloudflare Pages / Vercel | GitHub Pages |
| **Analytics** | Plausible (privacy-first) | Google Analytics |
| **Fonts** | Google Fonts (self-hosted via `@fontsource`) | Native `font-display: swap` |

### เหตุผลที่แนะนำ Astro

1. **Zero JS by default** — static HTML → เร็วที่สุด
2. **Content Collections** — blog + docs management ง่าย
3. **Islands Architecture** — interactive components เท่าที่จำเป็น
4. **Responsive ไม่ต้องคิดมาก** — CSS-only solutions
5. **Markdown-first** — Content Creator (เสก) เขียน content เป็น .md ได้เลย

### Performance Targets

| Metric | Target |
|:-------|:-------|
| **LCP** (Largest Contentful Paint) | < 1.2s |
| **FCP** (First Contentful Paint) | < 0.8s |
| **TBT** (Total Blocking Time) | < 50ms |
| **CLS** (Cumulative Layout Shift) | < 0.05 |
| **SI** (Speed Index) | < 1.5s |
| **Total Bundle JS** | < 50KB gzipped |

### SEO Considerations

- **Semantic HTML** — `article`, `section`, `nav`, `header`, `footer`
- **JSON-LD Structured Data** — `Organization`, `WebSite`, `BlogPosting`
- **Open Graph** — `og:title`, `og:description`, `og:image` (1200×630)
- **Twitter Cards** — `summary_large_image`
- **Sitemap.xml** — auto-generated จาก routes
- **RSS Feed** — สำหรับ blog content
- **Canonical URLs** — ป้องกัน duplicate content
- **Meta robots** — ควบคุม crawl behavior
- **hreflang** — สำหรับ i18n (TH, EN)

### Accessibility (a11y)

- WCAG 2.2 AA compliance
- Keyboard-navigable
- Focus indicators
- Alt text ทุก image
- ARIA labels สำหรับ interactive elements
- Color contrast ratio > 4.5:1 (text), > 3:1 (large text)

---

## 9. Timeline Estimate

### Phase 0 — Foundation (Week 1)

| Task | Owner | Deliverable |
|:-----|:------|:------------|
| Wireframe + Mockup | Design (ครีเอท) | Figma file — 5 key pages |
| Content Writing | Content Creator (เสก) | Copy for all sections (TH + EN) |
| Logo + Asset Prep | Design (ครีเอท) | SVG, favicon, social preview |

### Phase 1 — Core Build (Week 2-3)

| Task | Owner | Deliverable |
|:-----|:------|:------------|
| Project Scaffold + Routing | Engineering (ช่างฟูล) | Astro project, Tailwind, deploy pipeline |
| Hero + What is + The Way | Engineering | First 3 sections |
| Architecture Section | Engineering + Design | Department list + pipeline diagram |
| Navigation + Footer | Engineering | Sticky nav, footer, responsive |
| Responsive + Dark Theme | Engineering | All breakpoints, theme tokens |

### Phase 2 — Content Pages (Week 3-4)

| Task | Owner | Deliverable |
|:-----|:------|:------------|
| Legal Vault | Engineering | 8 templates — preview + download |
| Blog System | Engineering | Content Collections + list + single |
| Getting Started | Engineering | Step-by-step guide with code snippets |
| i18n Support (TH + EN) | Engineering | Locale switching |

### Phase 3 — Polish & Launch (Week 4-5)

| Task | Owner | Deliverable |
|:-----|:------|:------------|
| SEO Meta + Structured Data | Engineering | JSON-LD, OG, sitemap |
| Performance Audit | QA (ทีมเทส) | Lighthouse > 95 |
| Accessibility Audit | QA | WCAG 2.2 AA |
| Content Proofread | Content Creator | Final copy review |
| Deploy | Engineering | Cloudflare Pages / Vercel |
| Launch | CEO + CMO | Official announcement |

**Total: ~5 weeks** (สามารถ parallel ได้ใน Phase 1-2)

---

## 10. Success Criteria

### Gate 1: Design Sign-off (End of Phase 0)

- [ ] CEO อนุมัติ Figma mockup
- [ ] 5 key pages: Home, Architecture, Legal Vault, Blog, Getting Started
- [ ] Mobile + Desktop variant
- [ ] Brand identity ตรงตาม Brand Foundation Doc

### Gate 2: Build Complete (End of Phase 1)

- [ ] Hero + What is + The Way + Architecture ครบ
- [ ] Responsive — test บน iPhone, iPad, Desktop 1920px
- [ ] Dark theme consistent
- [ ] Lighthouse score > 90

### Gate 3: Pre-Launch (End of Phase 2)

- [ ] Legal Vault — 8 templates download ได้
- [ ] Blog — 1-2 seed posts published
- [ ] Getting Started — step-by-step verified
- [ ] i18n ทั้ง TH และ EN
- [ ] Lighthouse > 95

### Gate 4: Launch (End of Phase 3)

- [ ] Production URL live
- [ ] Analytics installed
- [ ] SEO meta ครบทุกหน้า
- [ ] CEO + Owner approve
- [ ] Public announcement ready

---

## Appendix: Handoff Requirements

| To | What | When |
|:---|:-----|:-----|
| **Design (ครีเอท)** | Wireframe + mockup + brand spec | Phase 0 |
| **Content Creator (เสก)** | Copywriting TH + EN | Phase 0 |
| **Engineering (ช่างฟูล)** | Tech spec + component library | Phase 1 |
| **QA (ทีมเทส)** | Test plan + evidence collection | Phase 3 |
| **CMO (มาร์ค)** | Launch announcement post | Pre-launch |

---

**PRD v1 — Product (โปรดัค)**
**รอ approval จาก CEO (หนุมาน) ก่อนส่งต่อ Design และ Engineering**
