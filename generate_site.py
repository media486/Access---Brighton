"""
Access Brighton — Daily Disability News Generator
Fetches local Brighton & Hove disability news and generates a static HTML site.
"""

import anthropic
import json
import re
from datetime import datetime

client = anthropic.Anthropic()

# ── 1. Gather today's news via web search ──────────────────────────────────────

def fetch_news():
    """Ask Claude to search for Brighton disability news and return structured JSON."""
    today = datetime.now().strftime("%d %B %Y")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Today is {today}.

Search the web for the latest news about disability in Brighton, Hove, and Sussex.
Search for several different angles:
1. "Brighton disability news 2026"
2. "Brighton Hove SEND services 2026"
3. "Sussex disability community events"
4. "Brighton accessibility news"

Return ONLY a valid JSON object (no markdown, no preamble) in this exact format:
{{
  "date": "{today}",
  "headline_story": {{
    "tag": "short category label",
    "title": "Main headline",
    "body": "2-3 sentence summary of the top story",
    "source": "Source name and date"
  }},
  "secondary_stories": [
    {{
      "tag": "category",
      "title": "Story title",
      "body": "1-2 sentence summary",
      "tag_type": "orange|teal|gold|purple"
    }},
    {{
      "tag": "category",
      "title": "Story title",
      "body": "1-2 sentence summary",
      "tag_type": "orange|teal|gold|purple"
    }},
    {{
      "tag": "category",
      "title": "Story title",
      "body": "1-2 sentence summary",
      "tag_type": "orange|teal|gold|purple"
    }}
  ],
  "features": [
    {{
      "tag": "category",
      "tag_type": "orange|teal|gold|purple",
      "icon": "single emoji",
      "title": "Feature title",
      "body": "2-3 sentence feature body",
      "source": "Source · date"
    }},
    {{
      "tag": "category",
      "tag_type": "orange|teal|gold|purple",
      "icon": "single emoji",
      "title": "Feature title",
      "body": "2-3 sentence feature body",
      "source": "Source · date"
    }},
    {{
      "tag": "category",
      "tag_type": "orange|teal|gold|purple",
      "icon": "single emoji",
      "title": "Feature title",
      "body": "2-3 sentence feature body",
      "source": "Source · date"
    }}
  ],
  "events": [
    {{
      "month": "MMM",
      "day": "DD",
      "title": "Event name",
      "body": "Short description"
    }},
    {{
      "month": "MMM",
      "day": "DD",
      "title": "Event name",
      "body": "Short description"
    }},
    {{
      "month": "MMM",
      "day": "DD",
      "title": "Event name",
      "body": "Short description"
    }}
  ],
  "quote": {{
    "text": "A relevant quote about disability in Brighton or Sussex",
    "attribution": "— Person/Organisation, context"
  }}
}}

Use real, accurate information from your searches. If you cannot find enough real local news, include recent council announcements, charity updates, or accessibility news from the wider Sussex area. Never invent facts."""
        }]
    )

    # Extract text content from the response
    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    # Parse JSON from the response
    # Strip any accidental markdown fences
    clean = re.sub(r"```json|```", "", full_text).strip()
    # Find the first { and last } to extract JSON
    start = clean.find("{")
    end = clean.rfind("}") + 1
    json_str = clean[start:end]
    return json.loads(json_str)


# ── 2. Render HTML ─────────────────────────────────────────────────────────────

def render_html(data: dict) -> str:
    date_str = data.get("date", datetime.now().strftime("%d %B %Y"))
    hs = data["headline_story"]

    # Secondary stories
    secondary_html = ""
    tag_classes = {"orange": "tag-orange", "teal": "tag-teal", "gold": "tag-gold", "purple": "tag-purple"}
    for s in data.get("secondary_stories", []):
        tc = tag_classes.get(s.get("tag_type", "teal"), "tag-teal")
        secondary_html += f"""
      <div class="stack-item">
        <span class="tag {tc}">{s['tag']}</span>
        <h3>{s['title']}</h3>
        <p>{s['body']}</p>
      </div>"""

    # Features
    img_classes = {"orange": "card-img-orange", "teal": "card-img-teal", "gold": "card-img-gold", "purple": "card-img-purple"}
    features_html = ""
    for f in data.get("features", []):
        ic = img_classes.get(f.get("tag_type", "teal"), "card-img-teal")
        tc = tag_classes.get(f.get("tag_type", "teal"), "tag-teal")
        features_html += f"""
    <div class="card">
      <div class="card-img {ic}">{f.get('icon','📰')}</div>
      <span class="tag {tc}">{f['tag']}</span>
      <h3>{f['title']}</h3>
      <p>{f['body']}</p>
      <p class="byline">{f.get('source','')}</p>
    </div>"""

    # Events
    events_html = ""
    for e in data.get("events", []):
        events_html += f"""
        <div class="event-item">
          <div class="event-date">
            <div class="month">{e['month']}</div>
            <div class="day">{e['day']}</div>
          </div>
          <div class="event-info">
            <h4>{e['title']}</h4>
            <p>{e['body']}</p>
          </div>
        </div>"""

    quote = data.get("quote", {})

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Access Brighton — Disability News & Community</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,700;0,900;1,400&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #1a1a2e; --paper: #f5f0e8; --accent: #e05a2b;
    --teal: #2a7f7f; --teal-light: #e8f5f5; --gold: #c9a84c;
    --muted: #6b6b7a; --rule: #d8d0c4;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--paper); color:var(--ink); font-family:'DM Sans',sans-serif; font-size:16px; line-height:1.6; }}
  .masthead {{ background:var(--ink); color:var(--paper); text-align:center; padding:12px 20px 0; border-bottom:4px solid var(--accent); }}
  .masthead-kicker {{ font-size:11px; letter-spacing:3px; text-transform:uppercase; color:var(--gold); font-weight:500; margin-bottom:6px; }}
  .masthead h1 {{ font-family:'Fraunces',serif; font-size:clamp(2.4rem,6vw,4.2rem); font-weight:900; letter-spacing:-1px; line-height:1; color:#fff; }}
  .masthead h1 span {{ color:var(--accent); }}
  .masthead-tagline {{ font-size:12px; letter-spacing:2px; text-transform:uppercase; color:#aaa; margin:8px 0 14px; }}
  .masthead-bar {{ border-top:1px solid #333; display:flex; justify-content:center; gap:28px; padding:10px 0; flex-wrap:wrap; }}
  .masthead-bar a {{ color:#ccc; text-decoration:none; font-size:12px; letter-spacing:1.5px; text-transform:uppercase; font-weight:500; transition:color .2s; }}
  .masthead-bar a:hover {{ color:var(--accent); }}
  .datebar {{ background:var(--accent); color:#fff; font-size:11px; letter-spacing:2px; text-transform:uppercase; text-align:center; padding:6px; font-weight:600; }}
  .wrap {{ max-width:1160px; margin:0 auto; padding:0 20px; }}
  .hero-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:0; border-bottom:3px double var(--rule); margin-top:32px; }}
  .hero-main {{ padding-right:32px; border-right:1px solid var(--rule); }}
  .hero-sidebar {{ padding-left:32px; }}
  .section-label {{ font-size:10px; letter-spacing:3px; text-transform:uppercase; color:var(--accent); font-weight:700; border-top:3px solid var(--ink); padding-top:8px; margin-bottom:14px; display:block; }}
  .hero-main .headline {{ font-family:'Fraunces',serif; font-size:clamp(1.6rem,3.5vw,2.6rem); font-weight:900; line-height:1.15; margin-bottom:12px; }}
  .hero-main .deck {{ font-size:1.05rem; color:var(--muted); line-height:1.65; margin-bottom:14px; font-weight:300; }}
  .hero-main .byline {{ font-size:11px; letter-spacing:1px; text-transform:uppercase; color:var(--muted); border-top:1px solid var(--rule); padding-top:10px; margin-top:10px; }}
  .hero-img {{ width:100%; aspect-ratio:16/9; background:linear-gradient(135deg,#2a7f7f 0%,#1a5050 100%); border-radius:2px; display:flex; align-items:center; justify-content:center; font-size:56px; margin-bottom:14px; position:relative; overflow:hidden; }}
  .hero-img::after {{ content:''; position:absolute; inset:0; background:repeating-linear-gradient(45deg,transparent,transparent 3px,rgba(255,255,255,.04) 3px,rgba(255,255,255,.04) 6px); }}
  .stack-item {{ padding:16px 0; border-bottom:1px solid var(--rule); }}
  .stack-item:last-child {{ border-bottom:none; }}
  .stack-item h3 {{ font-family:'Fraunces',serif; font-size:1.1rem; font-weight:700; line-height:1.25; margin-bottom:5px; }}
  .stack-item p {{ font-size:0.88rem; color:var(--muted); line-height:1.5; }}
  .tag {{ display:inline-block; font-size:9px; letter-spacing:2px; text-transform:uppercase; font-weight:700; padding:2px 7px; border-radius:2px; margin-bottom:6px; }}
  .tag-orange {{ background:#fde8de; color:var(--accent); }}
  .tag-teal {{ background:var(--teal-light); color:var(--teal); }}
  .tag-gold {{ background:#faf0dc; color:#8a6a10; }}
  .tag-purple {{ background:#ede8f5; color:#5a3e8a; }}
  .divider {{ border:none; border-top:3px double var(--rule); margin:32px 0; }}
  .three-col {{ display:grid; grid-template-columns:repeat(3,1fr); gap:28px; margin-bottom:36px; }}
  .card-img {{ width:100%; aspect-ratio:4/3; border-radius:2px; display:flex; align-items:center; justify-content:center; font-size:40px; margin-bottom:12px; }}
  .card-img-orange {{ background:linear-gradient(135deg,#e05a2b 0%,#c04020 100%); }}
  .card-img-teal   {{ background:linear-gradient(135deg,#2a7f7f 0%,#1a5050 100%); }}
  .card-img-purple {{ background:linear-gradient(135deg,#6a4a9e 0%,#4a2a7e 100%); }}
  .card-img-gold   {{ background:linear-gradient(135deg,#c9a84c 0%,#9a7830 100%); }}
  .card h3 {{ font-family:'Fraunces',serif; font-size:1.15rem; font-weight:700; line-height:1.25; margin-bottom:8px; }}
  .card p {{ font-size:0.87rem; color:var(--muted); line-height:1.55; }}
  .card .byline {{ margin-top:10px; font-size:10px; letter-spacing:1px; text-transform:uppercase; color:#aaa; }}
  .resources-band {{ background:var(--ink); color:var(--paper); padding:32px 0; margin:36px 0; }}
  .resources-band .section-label {{ color:var(--gold); border-top-color:var(--gold); }}
  .resources-band .band-title {{ font-family:'Fraunces',serif; font-size:1.5rem; font-weight:700; color:#fff; margin-bottom:20px; }}
  .resources-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }}
  .resource-card {{ background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.1); border-radius:4px; padding:18px; transition:background .2s; }}
  .resource-card:hover {{ background:rgba(255,255,255,.1); }}
  .resource-card .r-icon {{ font-size:26px; margin-bottom:10px; }}
  .resource-card h4 {{ font-size:0.95rem; font-weight:600; color:#fff; margin-bottom:5px; }}
  .resource-card p {{ font-size:0.8rem; color:#aaa; line-height:1.45; }}
  .resource-card a {{ color:var(--gold); font-size:0.78rem; text-decoration:none; font-weight:600; }}
  .two-col {{ display:grid; grid-template-columns:2fr 1fr; gap:36px; margin-bottom:36px; }}
  .event-item {{ display:flex; gap:16px; padding:16px 0; border-bottom:1px solid var(--rule); }}
  .event-date {{ min-width:52px; text-align:center; background:var(--teal); color:#fff; border-radius:3px; padding:8px 6px; line-height:1.1; }}
  .event-date .month {{ font-size:9px; letter-spacing:2px; text-transform:uppercase; }}
  .event-date .day {{ font-family:'Fraunces',serif; font-size:1.6rem; font-weight:900; }}
  .event-info h4 {{ font-family:'Fraunces',serif; font-size:1rem; font-weight:700; margin-bottom:4px; }}
  .event-info p {{ font-size:0.83rem; color:var(--muted); }}
  .opinion-box {{ background:var(--teal-light); border-left:4px solid var(--teal); padding:22px; border-radius:0 4px 4px 0; }}
  .opinion-box .opinion-label {{ font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--teal); font-weight:700; margin-bottom:10px; }}
  .opinion-box blockquote {{ font-family:'Fraunces',serif; font-size:1.1rem; font-style:italic; font-weight:400; line-height:1.5; color:var(--ink); margin-bottom:12px; }}
  .opinion-box cite {{ font-size:0.82rem; color:var(--muted); font-style:normal; }}
  footer {{ background:#111; color:#888; padding:32px 0 20px; margin-top:48px; }}
  footer .foot-grid {{ display:grid; grid-template-columns:2fr 1fr 1fr; gap:32px; margin-bottom:24px; }}
  footer h4 {{ font-family:'Fraunces',serif; color:#fff; font-size:1rem; margin-bottom:10px; }}
  footer p, footer li {{ font-size:0.83rem; line-height:1.7; }}
  footer ul {{ list-style:none; }}
  footer a {{ color:#bbb; text-decoration:none; }}
  footer a:hover {{ color:var(--accent); }}
  .foot-bottom {{ border-top:1px solid #333; padding-top:16px; text-align:center; font-size:0.78rem; color:#555; }}
  .foot-brand {{ font-family:'Fraunces',serif; font-size:1.5rem; font-weight:900; color:#fff; margin-bottom:10px; }}
  .foot-brand span {{ color:var(--accent); }}
  .updated-badge {{ display:inline-block; background:rgba(201,168,76,.15); border:1px solid var(--gold); color:var(--gold); font-size:10px; letter-spacing:2px; text-transform:uppercase; padding:3px 10px; border-radius:2px; margin-left:12px; vertical-align:middle; }}
  @media(max-width:768px) {{
    .hero-grid {{ grid-template-columns:1fr; }}
    .hero-main {{ padding-right:0; border-right:none; border-bottom:1px solid var(--rule); padding-bottom:24px; margin-bottom:24px; }}
    .hero-sidebar {{ padding-left:0; }}
    .three-col {{ grid-template-columns:1fr; }}
    .resources-grid {{ grid-template-columns:1fr 1fr; }}
    .two-col {{ grid-template-columns:1fr; }}
    footer .foot-grid {{ grid-template-columns:1fr; }}
  }}
  @keyframes fadeUp {{ from {{ opacity:0; transform:translateY(18px); }} to {{ opacity:1; transform:translateY(0); }} }}
  .wrap > * {{ animation:fadeUp .5s ease both; }}
</style>
</head>
<body>

<div class="masthead">
  <div class="masthead-kicker">Brighton &amp; Hove</div>
  <h1>Access <span>Brighton</span></h1>
  <p class="masthead-tagline">Disability News · Community · Resources · Advocacy</p>
  <nav class="masthead-bar">
    <a href="#">News</a><a href="#">Services</a><a href="#">Events</a>
    <a href="#">SEND</a><a href="#">Accessibility</a><a href="#">Advocacy</a><a href="#">Resources</a>
  </nav>
</div>

<div class="datebar">
  {date_str}
  <span class="updated-badge">Auto-updated daily</span>
</div>

<div class="wrap" style="padding-top:32px;">
  <div class="hero-grid">
    <div class="hero-main">
      <span class="section-label">Top Story</span>
      <div class="hero-img">♿</div>
      <span class="tag tag-orange">{hs['tag']}</span>
      <h2 class="headline">{hs['title']}</h2>
      <p class="deck">{hs['body']}</p>
      <p class="byline">Source: {hs.get('source','Brighton &amp; Hove')}</p>
    </div>
    <div class="hero-sidebar">
      <span class="section-label">Also in the news</span>
      {secondary_html}
    </div>
  </div>

  <hr class="divider">
  <span class="section-label">Features</span>
  <div class="three-col">{features_html}</div>
</div>

<div class="resources-band">
  <div class="wrap">
    <span class="section-label">Local Resources</span>
    <p class="band-title">Key services &amp; support organisations in Brighton &amp; Hove</p>
    <div class="resources-grid">
      <div class="resource-card"><div class="r-icon">🗣️</div><h4>Speak Out</h4><p>Learning disability advocacy across Brighton &amp; Hove, in person and by phone.</p><br><a href="https://www.bhspeakout.org.uk" target="_blank">bhspeakout.org.uk →</a></div>
      <div class="resource-card"><div class="r-icon">👨‍👩‍👧</div><h4>Amaze Sussex</h4><p>Support for families with disabled children and young people in Brighton &amp; East Sussex.</p><br><a href="https://amazesussex.org.uk" target="_blank">amazesussex.org.uk →</a></div>
      <div class="resource-card"><div class="r-icon">🏛️</div><h4>B&amp;H City Council</h4><p>Council services for disabled adults and children: SCDS, direct payments, short breaks.</p><br><a href="https://www.brighton-hove.gov.uk" target="_blank">brighton-hove.gov.uk →</a></div>
      <div class="resource-card"><div class="r-icon">👪</div><h4>PaCC Brighton</h4><p>Parent carer forum feeding back on SEND and disability services across the city.</p><br><a href="https://paccbrighton.org.uk" target="_blank">paccbrighton.org.uk →</a></div>
    </div>
  </div>
</div>

<div class="wrap">
  <div class="two-col">
    <div>
      <span class="section-label">Community Events</span>
      <div class="events-list">{events_html}</div>
    </div>
    <div>
      <span class="section-label">Community Voice</span>
      <div class="opinion-box">
        <div class="opinion-label">Quote</div>
        <blockquote>"{quote.get('text','Inclusion means everyone.')}"</blockquote>
        <cite>{quote.get('attribution','— Brighton &amp; Hove disability community')}</cite>
      </div>
    </div>
  </div>
</div>

<footer>
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="foot-brand">Access <span>Brighton</span></div>
        <p>A community resource gathering disability news, services and events across Brighton &amp; Hove and Sussex. Updated automatically every day. Not affiliated with Brighton &amp; Hove City Council.</p>
      </div>
      <div>
        <h4>Quick Links</h4>
        <ul>
          <li><a href="https://www.brighton-hove.gov.uk">B&amp;H City Council</a></li>
          <li><a href="https://amazesussex.org.uk">Amaze Sussex</a></li>
          <li><a href="https://www.bhspeakout.org.uk">Speak Out</a></li>
          <li><a href="https://paccbrighton.org.uk">PaCC Brighton</a></li>
          <li><a href="https://www.brightonandhovenews.org">Brighton &amp; Hove News</a></li>
        </ul>
      </div>
      <div>
        <h4>Categories</h4>
        <ul>
          <li><a href="#">Council &amp; Policy</a></li>
          <li><a href="#">SEND &amp; Education</a></li>
          <li><a href="#">Accessibility</a></li>
          <li><a href="#">Community Events</a></li>
          <li><a href="#">Advocacy</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">© {datetime.now().year} Access Brighton &nbsp;·&nbsp; Community disability news for Brighton &amp; Hove &nbsp;·&nbsp; Auto-updated daily via AI</div>
  </div>
</footer>
</body>
</html>"""


# ── 3. Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔍 Fetching latest Brighton disability news...")
    data = fetch_news()
    print(f"✅ Got news for {data.get('date')}")

    print("🖊️  Rendering HTML...")
    html = render_html(data)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ index.html written successfully!")
    print(f"   Headline: {data['headline_story']['title']}")
