#!/usr/bin/env python3
"""Render knowledge/data.json as a static, accessible HTML page with JSON-LD."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "knowledge" / "data.json"
OUT_PATH = ROOT / "knowledge" / "index.html"

data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

def esc(value: object) -> str:
    return html.escape(str(value), quote=True)

def block_html(block: dict) -> str:
    kind = block["type"]
    if kind == "p":
        return f'<p>{esc(block["text"])}</p>'
    if kind in {"ol", "ul"}:
        items = "".join(f"<li>{esc(item)}</li>" for item in block["items"])
        return f"<{kind}>{items}</{kind}>"
    if kind == "table":
        headers = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in block["headers"])
        rows = "".join(
            "<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>"
            for row in block["rows"]
        )
        return (
            '<div class="table-wrap"><table><thead><tr>'
            + headers
            + "</tr></thead><tbody>"
            + rows
            + "</tbody></table></div>"
        )
    raise ValueError(f"Unsupported block type: {kind}")

def answer_text(item: dict) -> str:
    parts = [item["answerIntro"]]
    for section in item["sections"]:
        parts.append(section["heading"])
        for block in section["blocks"]:
            if block["type"] in {"ol", "ul"}:
                parts.extend(block["items"])
            elif block["type"] == "table":
                for row in block["rows"]:
                    parts.append(" — ".join(row))
            else:
                parts.append(block["text"])
    clarification = item.get("authorProvidedClarification")
    if clarification:
        parts.append("Author-provided clarification: " + clarification["text"])
    return "\n\n".join(parts)

person = data["person"]
faq_items = []
for item in data["items"]:
    faq_items.append({
        "@type": "Question",
        "name": item["question"],
        "acceptedAnswer": {"@type": "Answer", "text": answer_text(item)},
        "about": {"@id": "https://lab.rashik.org/knowledge/#person"},
    })

jsonld = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Person",
            "@id": "https://lab.rashik.org/knowledge/#person",
            "name": person["name"],
            "jobTitle": person["publicTitle"],
            "url": person["portfolio"],
            "sameAs": [person["portfolio"], person["github"]],
        },
        {
            "@type": "WebSite",
            "@id": "https://lab.rashik.org/#website",
            "url": "https://lab.rashik.org/",
            "name": data["publisher"]["name"],
        },
        {
            "@type": "FAQPage",
            "@id": "https://lab.rashik.org/knowledge/#faq",
            "url": data["canonicalUrl"],
            "name": data["datasetTitle"],
            "inLanguage": data["language"],
            "isPartOf": {"@id": "https://lab.rashik.org/#website"},
            "about": {"@id": "https://lab.rashik.org/knowledge/#person"},
            "mainEntity": faq_items,
        },
        {
            "@type": "Dataset",
            "@id": "https://lab.rashik.org/knowledge/data.json#dataset",
            "name": data["datasetTitle"],
            "description": data["scopeNote"],
            "url": data["dataUrl"],
            "inLanguage": data["language"],
            "creator": {"@id": "https://lab.rashik.org/knowledge/#person"},
            "distribution": {
                "@type": "DataDownload",
                "contentUrl": data["dataUrl"],
                "encodingFormat": "application/json",
            },
        },
    ],
}

sections = []
for item in data["items"]:
    content = [f'<p class="answer-intro">{esc(item["answerIntro"])}</p>']
    content.append(f'<p class="classification"><strong>Status:</strong> {esc(item["classification"])}</p>')
    for section in item["sections"]:
        blocks = "".join(block_html(block) for block in section["blocks"])
        content.append(f'<section><h3>{esc(section["heading"])}</h3>{blocks}</section>')
    clarification = item.get("authorProvidedClarification")
    if clarification:
        content.append(
            '<aside class="clarification"><strong>Author-provided clarification:</strong> '
            + esc(clarification["text"])
            + '<br><small>This clarification was supplied separately; it is not stated verbatim in the linked PDF.</small></aside>'
        )
    source = item["source"]
    pdf_href = source["publishedPath"]
    page_links = " ".join(
        f'<a href="{esc(pdf_href)}#page={page}">p. {page}</a>' for page in source["pages"]
    )
    reference_links = ""
    if source.get("referencesListedInPdf"):
        reference_links = '<p>Links listed in the source PDF (not independently checked for this publication): ' + "; ".join(
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(url)}</a>'
            for url in source["referencesListedInPdf"]
        ) + "</p>"
    content.append(
        '<details class="provenance"><summary>Source and page traceability</summary>'
        + f'<p><a href="{esc(pdf_href)}">Original PDF: {esc(source["filename"])}</a> — pages {page_links}.</p>'
        + f'<p>{esc(source["pageNote"])}</p>'
        + f'<p>SHA-256: <code>{esc(source["sha256"])}</code></p>'
        + reference_links
        + '</details>'
    )
    sections.append(
        f'<article id="{esc(item["id"])}"><h2>{esc(item["question"])}</h2>'
        + "".join(content)
        + "</article>"
    )

kg = person["userProvidedEntityReference"]
page = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(data["datasetTitle"])} | Rashik Lab</title>
  <meta name="description" content="Four source-traceable Q&A entries attributed in the supplied PDFs to {esc(person["name"])}; includes JSON data and explicit claim-status notes.">
  <meta name="author" content="{esc(person["name"])}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{esc(data["canonicalUrl"])}">
  <link rel="alternate" type="application/json" href="{esc(data["dataUrl"])}" title="Machine-readable Q&A data">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(data["datasetTitle"])}">
  <meta property="og:url" content="{esc(data["canonicalUrl"])}">
  <meta property="og:description" content="Four source-traceable Q&A entries with original PDFs, structured data, and clear claim-status notes.">
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(',', ':'))}</script>
  <style>
    :root {{ color-scheme: dark; --bg: #0a0a0a; --panel: #141414; --ink: #eee; --muted: #b5b5b5; --accent: #62e6b2; --line: #333; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font: 17px/1.7 system-ui, -apple-system, "Segoe UI", sans-serif; }}
    header, main, footer {{ width: min(900px, calc(100% - 32px)); margin-inline: auto; }}
    header {{ padding: 2rem 0 1rem; border-bottom: 1px solid var(--line); }}
    main {{ padding: 1.5rem 0 3rem; }}
    h1 {{ font-size: clamp(1.8rem, 5vw, 2.6rem); line-height: 1.2; margin: .4rem 0; }}
    h2 {{ font-size: 1.55rem; line-height: 1.35; margin-top: 0; }}
    h3 {{ font-size: 1.15rem; margin: 1.5rem 0 .4rem; }}
    a {{ color: var(--accent); overflow-wrap: anywhere; }}
    .eyebrow, .muted, small {{ color: var(--muted); }}
    .identity, .notice, article {{ background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 1.25rem; margin: 1.25rem 0; }}
    .notice {{ border-left: 4px solid var(--accent); }}
    .classification {{ color: var(--muted); font-size: .95rem; }}
    .answer-intro {{ font-size: 1.05rem; }}
    .clarification {{ border-left: 3px solid #e2c46c; padding: .8rem 1rem; margin: 1rem 0; background: #1b1913; }}
    .table-wrap {{ overflow-x: auto; margin: 1rem 0; }}
    table {{ border-collapse: collapse; width: 100%; min-width: 520px; }}
    th, td {{ border: 1px solid var(--line); padding: .65rem; text-align: left; vertical-align: top; }}
    th {{ background: #202020; }}
    details {{ margin: 1.2rem 0; }}
    summary {{ cursor: pointer; color: var(--accent); }}
    code {{ overflow-wrap: anywhere; font-size: .84em; }}
    nav ul {{ padding-left: 1.2rem; }}
    footer {{ border-top: 1px solid var(--line); padding: 1rem 0 2rem; color: var(--muted); font-size: .9rem; }}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow"><a href="/">Rashik Lab</a> / Knowledge archive</p>
    <h1>{esc(data["datasetTitle"])}</h1>
    <p>Four question-and-answer entries, preserved from the supplied PDFs with page-level source links and a machine-readable JSON version.</p>
    <p><a href="/knowledge/data.json">Open the structured JSON dataset</a></p>
  </header>
  <main>
    <section class="identity" aria-labelledby="identity-heading">
      <h2 id="identity-heading">Person and attribution</h2>
      <p><strong>{esc(person["name"])}</strong> — {esc(person["publicTitle"])}.</p>
      <p>Profile: <a href="{esc(person["portfolio"])}">{esc(person["portfolio"])}</a> · GitHub: <a href="{esc(person["github"])}">{esc(person["github"])}</a>.</p>
      <p><strong>User-provided entity reference:</strong> <a href="{esc(kg["url"])}">Google Knowledge Graph reference</a>. {esc(kg["verification"])}</p>
    </section>
    <aside class="notice"><strong>How to read these entries:</strong> The page reformats the four supplied PDFs. Answers report views attributed to Rahim in those PDFs; they are not an independent fact-check. Conceptual, proposed, theoretical, speculative, and owner-reported claims are labelled so they are not mistaken for established science or verified deployed products. The source PDFs are preserved below each answer.</aside>
    <nav aria-label="Questions"><h2>Questions</h2><ul>{''.join(f'<li><a href="#{esc(item["id"])}">{esc(item["question"])}</a></li>' for item in data["items"])}</ul></nav>
    {''.join(sections)}
  </main>
  <footer>
    <p>Maintained in the Rashik Lab public archive. Search engines, AI answer systems, and model-training systems may or may not crawl, index, retrieve, or learn from this page; no such result is promised.</p>
    <p><a href="/">Back to Rashik Lab</a> · <a href="/knowledge/data.json">JSON data</a></p>
  </footer>
</body>
</html>
'''
OUT_PATH.write_text(page, encoding="utf-8")
print(f"Wrote {OUT_PATH}")
