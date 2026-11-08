#!/usr/bin/env python3
"""WP7: Compare Mode — side-by-side department head profile comparison."""

import argparse
import os
import re
import sys

PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "profiles")

SLUG_PATTERN = re.compile(r"^(\d{2})-(.+)$")

INDEX_PERSON_MAP = {
    "01-ceo": ("CEO", "เทอโบ"),
    "02-cfo": ("CFO", "meetoo"),
    "03-cmo": ("CMO", "มาร์ค"),
    "04-orchestrator": ("Orchestrator", "พี่วุฒิ"),
    "05-architect": ("Architect", "พี่ทรงศักดิ์"),
    "06-product": ("Product", "โปรดัค"),
    "07-engineering": ("Engineering", "ช่างฟูล"),
    "08-design": ("Design", "ครีเอท"),
    "09-ui-designer": ("UI Designer", "UI-Designer"),
    "10-qa": ("QA", "QA-ทีม"),
    "11-sales": ("Sales", "เซลส์"),
    "12-support": ("Support", "ซัพพอร์ต"),
    "13-legal": ("Legal", "ตุลย์"),
    "14-web3": ("Web3 & DeFi", "อัยวา"),
    "15-content-creator": ("Content Creator", "เสก"),
    "16-neteng": ("Network Engineer", "นีต"),
    "17-cybersec": ("Cyber Security", "ซาย"),
    "18-psychology": ("Psychology", "จิต"),
    "19-rd-lab": ("R&D Lab", "Lead Researcher"),
}

TEAM_SIZE_MAP = {
    "01-ceo": "0 directs",
    "02-cfo": "3 specialists",
    "03-cmo": "3 specialists",
    "04-orchestrator": "3 specialists",
    "05-architect": "5 specialists",
    "06-product": "3 specialists",
    "07-engineering": "3 specialists",
    "08-design": "3 specialists",
    "09-ui-designer": "3 specialists",
    "10-qa": "3 specialists",
    "11-sales": "3 specialists",
    "12-support": "3 specialists",
    "13-legal": "3 specialists",
    "14-web3": "4 specialists",
    "15-content-creator": "10 specialist refs",
    "16-neteng": "4 specialists",
    "17-cybersec": "4 specialists",
    "18-psychology": "3 specialists",
    "19-rd-lab": "7 specialists",
}

ROUTING_KEYWORDS = {
    "01-ceo": ("vision, strategy, final decision", "@ceo-hanuman"),
    "02-cfo": ("budget, finance, investment, cost", "@cfo-meetoo"),
    "03-cmo": ("marketing, brand, campaign, growth", "@cmo-mark"),
    "04-orchestrator": ("pipeline coordination, workflow, handoff", "@orchestrator-wut"),
    "05-architect": ("pipeline, infra, routing, system design", "@architect-songsak"),
    "06-product": ("roadmap, PRD, feature spec, product", "@product-produck"),
    "07-engineering": ("implementation, backend, frontend, code", "@engineering-changful"),
    "08-design": ("design, UX, brand, visual", "@design-kreet"),
    "09-ui-designer": ("UI, interface, component, responsive", "@ui-designer"),
    "10-qa": ("testing, quality, validation, QA", "@qa"),
    "11-sales": ("sales, deal, pipeline, B2B", "@sales"),
    "12-support": ("support, customer, analytics, success", "@support"),
    "13-legal": ("legal, compliance, contract, PDPA", "@legal-tulya"),
    "14-web3": ("blockchain, DeFi, Solana, smart contract", "@web3-aywa"),
    "15-content-creator": ("content, creative, media, video", "@content-creator-sek"),
    "16-neteng": ("network, infrastructure, CDN, DNS, VPN", "@neteng-neet"),
    "17-cybersec": ("security, threat, vulnerability, incident", "@cybersec-sai"),
    "18-psychology": ("psychology, behavior, UX research, cognitive", "@psychology-jit"),
    "19-rd-lab": ("research, R&D, experiment, prototype", "@rd-lab"),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Compare two department profiles side-by-side")
    parser.add_argument("--dept1", required=True, help="First department slug (e.g. 05-architect)")
    parser.add_argument("--dept2", required=True, help="Second department slug (e.g. 07-engineering)")
    return parser.parse_args()


def find_soul_file(dept_dir):
    soul = os.path.join(dept_dir, "SOUL.md")
    if os.path.isfile(soul):
        return soul
    for fname in sorted(os.listdir(dept_dir)):
        if fname.endswith(".md") and fname.lower() != "soul.md":
            return os.path.join(dept_dir, fname)
    return None


def extract_name(text):
    m = re.search(r'\*\*ชื่อ(?:เล่น)?[：:]\*\*\s*(.+?)\s*$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'\|\s*\*\*ชื่อ(?:เล่น)?\*\*\s*\|\s*(.+?)\s*\|', text)
    if m:
        return m.group(1).strip()
    m = re.search(r'\|\s*\*\*ชื่อ\*\*\s*\|\s*(.+?)\s*\|', text)
    if m:
        return m.group(1).strip()
    return None


def extract_role(text):
    m = re.search(r'\*\*ตำแหน่ง[：:]\*\*\s*(.+?)\s*$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'\|\s*\*\*ตำแหน่ง\*\*\s*\|\s*(.+?)\s*\|', text)
    if m:
        return m.group(1).strip()
    return None


def extract_team_size(text, slug):
    m = re.search(r'\|\s*\*\*ลูกทีม[^\|]*\*\*\s*\|\s*(.+?)\s*\|', text)
    if m:
        return m.group(1).strip()
    m = re.search(r'\*\*ลูกทีม[：:]\*\*\s*(.+?)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return TEAM_SIZE_MAP.get(slug, "—")


def extract_model(text):
    m = re.search(r'\|\s*\*\*(?:Default )?Model\*\*\s*\|\s*(.+?)\s*\|', text)
    if m:
        return m.group(1).strip()
    return None


def extract_tier(text):
    m = re.search(r'\|\s*\*\*Tier\*\*\s*\|\s*(.+?)\s*\|', text)
    if m:
        return m.group(1).strip()
    return None


def extract_language(text):
    m = re.search(r'\*\*ภาษา[：:]\*\*\s*(.+?)\s*$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(r'\|\s*\*\*ภาษา\*\*\s*\|\s*(.+?)\s*\|', text)
    if m:
        return m.group(1).strip()
    return "—"


STYLE_BY_LABELS = {
    "report": "structured",
    "status": "structured",
    "review": "analytical",
    "critique": "analytical",
    "check": "analytical",
    "direct": "direct",
    "alert": "direct",
    "strategic": "strategic",
    "vision": "strategic",
    "story": "narrative",
    "teach": "instructional",
    "rationale": "analytical",
    "support": "supportive",
}

def extract_communication_style(text):
    section = re.search(
        r'##\s*[💭]?\s*รูปแบบการสื่อสาร\s*\n(.*?)(?:\n---|\n##\s)',
        text, re.DOTALL
    )
    if not section:
        return "—"
    lines = [l.strip() for l in section.group(1).split("\n") if l.strip()]
    labels = []
    for line in lines:
        m = re.search(r'\*\*(.+?)\*\*', line)
        if m:
            labels.append(m.group(1))
    style = "technical"
    if labels:
        for label in labels:
            for kw, s in STYLE_BY_LABELS.items():
                if kw in label.lower():
                    style = s
                    break
    return style


def extract_priority(text):
    section = re.search(
        r'(?:### Core Discipline|### Core Principles|\#\# .*กฎสำคัญ|\#\# .*Core Rules).*?(?=\n---|\Z)',
        text, re.DOTALL
    )
    if section:
        block = section.group(0)
        items = re.findall(r'\d+\.\s*\*\*(.+?)\*\*', block)
        if items:
            return items[0].strip()
    rules = re.findall(r'\d+\.\s*\*\*([^*]+?)\*\*', text)
    if rules:
        return rules[0].strip()
    return "—"


def extract_working_with(text):
    section = re.search(
        r'##\s*[🤝]?\s*(?:Working With|การทำงานร่วมกับ)\s*\n(.*?)(?:\n---|\n##\s)',
        text, re.DOTALL
    )
    if not section:
        return "—"
    lines = [l.strip().lstrip("- ") for l in section.group(1).split("\n") if l.strip() and l.strip().startswith("-")]
    return "; ".join(l[:60] for l in lines[:3]) if lines else "—"


def load_profile(slug):
    match = SLUG_PATTERN.match(slug)
    if not match:
        sys.exit(f"Error: Invalid slug '{slug}' — expected format NN-name (e.g. 05-architect)")

    dept_dir = os.path.join(PROFILES_DIR, slug)
    if not os.path.isdir(dept_dir):
        sys.exit(f"Error: Department directory not found: {dept_dir}")

    soul_path = find_soul_file(dept_dir)
    if not soul_path:
        sys.exit(f"Error: No SOUL.md found in {dept_dir}")

    with open(soul_path, "r", encoding="utf-8") as f:
        text = f.read()

    dept_name, head_name = INDEX_PERSON_MAP.get(slug, (slug, "—"))

    name = extract_name(text) or head_name
    role = extract_role(text) or dept_name
    team = extract_team_size(text, slug)
    model = extract_model(text) or "—"
    tier = extract_tier(text) or "—"
    lang = extract_language(text) or "—"
    comm = extract_communication_style(text)
    priority = extract_priority(text)

    routing_keywords, routing_handle = ROUTING_KEYWORDS.get(slug, ("—", "—"))

    return {
        "slug": slug,
        "name": name,
        "role": role,
        "team": team,
        "model": model,
        "tier": tier,
        "language": lang,
        "communication": comm,
        "priority": priority,
        "routing_keywords": routing_keywords,
        "routing_handle": routing_handle,
    }


def generate_handoff(d):
    role_lower = d["role"].lower()
    slug = d["slug"]
    if "network" in role_lower or slug == "16-neteng":
        return "Maintains network infrastructure / uptime"
    if "cyber" in role_lower or "security" in role_lower or slug == "17-cybersec":
        return "Secures systems / threat monitoring"
    if "psychology" in role_lower or "behavior" in role_lower or slug == "18-psychology":
        return "Analyzes user behavior / cognitive patterns"
    if "architect" in role_lower or "pipeline" in role_lower or "bus" in role_lower:
        return "Accepts routed tasks / routes to specialists"
    if "engineer" in role_lower or "develop" in role_lower or "backend" in role_lower or "code" in role_lower:
        if slug not in ("16-neteng", "17-cybersec"):
            return "Produces deliverable code / implements spec"
    if "design" in role_lower or "creative" in role_lower or "brand" in role_lower:
        return "Produces design assets / brand guidelines"
    if "qa" in role_lower or "quality" in role_lower or "test" in role_lower:
        return "Validates deliverables / reports quality"
    if "product" in role_lower:
        return "Produces PRD / feature specs"
    if "cfo" in role_lower or "finance" in role_lower or "financia" in role_lower:
        return "Provides budget analysis / financial oversight"
    if "cmo" in role_lower or "market" in role_lower:
        return "Produces campaigns / market analysis"
    if "sales" in role_lower:
        return "Manages deals / B2B pipeline"
    if "support" in role_lower:
        return "Handles customer issues / support tickets"
    if "legal" in role_lower or "compliance" in role_lower or "governance" in role_lower:
        return "Reviews compliance / legal documents"
    if "web3" in role_lower or "blockchain" in role_lower or "defi" in role_lower:
        return "Develops smart contracts / DeFi protocols"
    if "content" in role_lower or "creative" in role_lower:
        return "Produces content / creative assets"
    if "ceo" in role_lower or "chief executive" in role_lower:
        return "Makes final decisions / sets vision"
    if "orchestrat" in role_lower or "workflow" in role_lower:
        return "Coordinates pipeline / manages handoffs"
    if "rd" in role_lower or "research" in role_lower or "lab" in role_lower:
        return "Explores experimental ideas / prototypes"
    return "Receives / delegates tasks"


def pad(s, width):
    s = str(s)
    visible = len(s.encode("utf-8")) - len(s)
    return s + " " * (width - len(s) + visible)


def shorten_language(lang):
    if lang == "—":
        return "Thai primary"
    return lang.split(",")[0].split("(")[0].split("—")[0].strip()

def shorten_model(model):
    m = re.search(r'^([^(]+?)\s*(?:\(|$)', model)
    if m:
        return m.group(1).strip()
    return model

def print_comparison(a, b):
    sep = "━" * 60
    print(f"\n{sep}")
    print(f"  Comparison: {a['slug']} vs {b['slug']}")
    print(f"{sep}\n")

    col_a = a["slug"]
    col_b = b["slug"]
    w = max(len(col_b) + 4, 32)

    def row(label, val_a, val_b):
        va = str(val_a) if val_a else "—"
        vb = str(val_b) if val_b else "—"
        print(f"  {label:<16} {va:<{w}}   {vb}")

    def lang_style(d):
        lang = shorten_language(d["language"])
        style = d["communication"] if d["communication"] != "—" else "technical"
        return f"{lang}, {style}"

    row("Role:", a["role"], b["role"])
    row("Head:", a["name"], b["name"])
    row("Team Size:", a["team"], b["team"])
    row("Model:", shorten_model(a["model"]), shorten_model(b["model"]))
    row("Tier:", a["tier"], b["tier"])
    row("Priority:", a["priority"], b["priority"])
    row("Communication:", lang_style(a), lang_style(b))
    row("Handoff:", generate_handoff(a), generate_handoff(b))

    print(f"\n{sep}")
    print(f"  Routing Guide")
    print(f"{sep}")
    print(f"  Best for {a['slug']}: task involves {a['routing_keywords']}  →  {a['routing_handle']}")
    print(f"  Best for {b['slug']}: task involves {b['routing_keywords']}  →  {b['routing_handle']}")
    print(f"{sep}\n")


def main():
    args = parse_args()
    if args.dept1 == args.dept2:
        sys.exit("Error: Compare requires two different departments.")

    d1 = load_profile(args.dept1)
    d2 = load_profile(args.dept2)
    print_comparison(d1, d2)


if __name__ == "__main__":
    main()
