#!/usr/bin/env python3
"""
Portfolio Admin — simple server-rendered admin panel.
Run: python admin.py   →   http://localhost:8888
"""
import json, re
from pathlib import Path
import yaml
import uvicorn
from fastapi import FastAPI, Form, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

ROOT        = Path(__file__).parent
CONTENT_DIR = ROOT / "src" / "content"
PUBLIC_DIR  = ROOT / "public"

TYPES = {
    "projects": {
        "label": "Projects",
        "fields": [
            {"name":"title",       "type":"text",     "required":True,  "label":"Title"},
            {"name":"description", "type":"textarea", "required":True,  "label":"Description"},
            {"name":"date",        "type":"date",     "required":True,  "label":"Date"},
            {"name":"status",      "type":"select",   "label":"Status",     "options":["completed","in-progress","archived"]},
            {"name":"category",    "type":"text",     "label":"Category"},
            {"name":"github",      "type":"text",     "label":"GitHub URL"},
            {"name":"demo",        "type":"text",     "label":"Demo URL"},
            {"name":"thumbnail",   "type":"image",    "label":"Thumbnail", "folder":"images/projects"},
            {"name":"techStack",   "type":"tags",     "label":"Tech Stack (comma-separated)"},
            {"name":"tags",        "type":"tags",     "label":"Tags (comma-separated)"},
            {"name":"featured",    "type":"checkbox", "label":"Featured on homepage"},
        ],
    },
    "blog": {
        "label": "Blog",
        "fields": [
            {"name":"title",       "type":"text",     "required":True,  "label":"Title"},
            {"name":"description", "type":"textarea", "required":True,  "label":"Description"},
            {"name":"date",        "type":"date",     "required":True,  "label":"Date"},
            {"name":"thumbnail",   "type":"image",    "label":"Thumbnail", "folder":"images/blog"},
            {"name":"tags",        "type":"tags",     "label":"Tags (comma-separated)"},
            {"name":"featured",    "type":"checkbox", "label":"Featured"},
            {"name":"draft",       "type":"checkbox", "label":"Draft (hidden from site)"},
        ],
    },
    "talks": {
        "label": "Talks",
        "fields": [
            {"name":"title",       "type":"text",     "required":True, "label":"Title"},
            {"name":"description", "type":"textarea", "required":True, "label":"Description"},
            {"name":"date",        "type":"date",     "required":True, "label":"Date"},
            {"name":"event",       "type":"text",     "required":True, "label":"Event Name"},
            {"name":"location",    "type":"text",     "label":"Location"},
            {"name":"linkedin",    "type":"text",     "label":"LinkedIn Post URL"},
            {"name":"slides",      "type":"text",     "label":"Slides URL"},
            {"name":"video",       "type":"text",     "label":"YouTube URL"},
            {"name":"thumbnail",   "type":"image",    "label":"Thumbnail", "folder":"images/talks"},
            {"name":"tags",        "type":"tags",     "label":"Tags (comma-separated)"},
            {"name":"featured",    "type":"checkbox", "label":"Featured"},
        ],
    },
    "certificates": {
        "label": "Certificates",
        "fields": [
            {"name":"title",         "type":"text",    "required":True, "label":"Certificate Name"},
            {"name":"issuer",        "type":"text",    "required":True, "label":"Issuer"},
            {"name":"date",          "type":"date",    "required":True, "label":"Issue Date"},
            {"name":"expiry",        "type":"date",    "label":"Expiry Date"},
            {"name":"credentialId",  "type":"text",    "label":"Credential ID"},
            {"name":"credentialUrl", "type":"text",    "label":"Verification URL"},
            {"name":"thumbnail",     "type":"image",   "label":"Badge Image", "folder":"certificates"},
            {"name":"tags",          "type":"tags",    "label":"Tags (comma-separated)"},
            {"name":"featured",      "type":"checkbox","label":"Featured"},
        ],
    },
    "timeline": {
        "label": "Timeline",
        "fields": [
            {"name":"title",        "type":"text",     "required":True, "label":"Title"},
            {"name":"date",         "type":"date",     "required":True, "label":"Date"},
            {"name":"description",  "type":"textarea", "required":True, "label":"Description"},
            {"name":"type",         "type":"select",   "label":"Type", "options":["work","education","achievement","project","other"]},
            {"name":"organization", "type":"text",     "label":"Organization"},
            {"name":"location",     "type":"text",     "label":"Location"},
            {"name":"tags",         "type":"tags",     "label":"Tags (comma-separated)"},
        ],
    },
    "competitions": {
        "label": "Competitions",
        "fields": [
            {"name":"title",       "type":"text",     "required":True, "label":"Competition Title"},
            {"name":"description", "type":"textarea", "required":True, "label":"Description"},
            {"name":"date",        "type":"date",     "required":True, "label":"Date"},
            {"name":"event",       "type":"text",     "required":True, "label":"Event Name"},
            {"name":"organizer",   "type":"text",     "label":"Organizer"},
            {"name":"location",    "type":"text",     "label":"Location"},
            {"name":"result",      "type":"text",     "label":"Result (e.g. Winner)"},
            {"name":"team",        "type":"text",     "label":"Team Name"},
            {"name":"teamSize",    "type":"number",   "label":"Team Size"},
            {"name":"project",     "type":"text",     "label":"What was built"},
            {"name":"github",      "type":"text",     "label":"GitHub URL"},
            {"name":"linkedin",    "type":"text",     "label":"LinkedIn Post URL"},
            {"name":"certificate", "type":"text",     "label":"Certificate URL"},
            {"name":"thumbnail",   "type":"image",    "label":"Thumbnail", "folder":"images/competitions"},
            {"name":"tags",        "type":"tags",     "label":"Tags (comma-separated)"},
            {"name":"featured",    "type":"checkbox", "label":"Featured"},
        ],
    },
    "experience": {
        "label": "Experience",
        "fields": [
            {"name":"title",       "type":"text",     "required":True, "label":"Job Title"},
            {"name":"company",     "type":"text",     "required":True, "label":"Company"},
            {"name":"location",    "type":"text",     "label":"Location"},
            {"name":"startDate",   "type":"date",     "required":True, "label":"Start Date"},
            {"name":"endDate",     "type":"date",     "label":"End Date"},
            {"name":"current",     "type":"checkbox", "label":"Currently working here"},
            {"name":"description", "type":"textarea", "required":True, "label":"Description"},
            {"name":"tags",        "type":"tags",     "label":"Tags (comma-separated)"},
            {"name":"order",       "type":"number",   "label":"Display order"},
        ],
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def content_dir(ctype: str) -> Path:
    return CONTENT_DIR / ctype

def parse_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            return {"id": path.stem, **fm, "_body": parts[2].strip()}
    return {"id": path.stem, "_body": text.strip()}

def write_md(path: Path, data: dict):
    body = data.pop("_body", "")
    data.pop("id", None)
    clean = {}
    for k, v in data.items():
        if v is None or v == "" or v == []:
            continue
        clean[k] = v
    fm = yaml.dump(clean, allow_unicode=True, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm}---\n\n{body}\n", encoding="utf-8")

def safe_slug(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9-]", "-", title.lower())).strip("-")[:50]

def list_entries(ctype: str) -> list:
    d = content_dir(ctype)
    if not d.exists():
        return []
    return sorted([parse_md(f) for f in d.glob("*.md")],
                  key=lambda x: str(x.get("date", "")), reverse=True)

def h(text) -> str:
    return str(text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

# ── Timeline sync ──────────────────────────────────────────────────────────────
TIMELINE_DIR = CONTENT_DIR / "timeline"

def timeline_path(ctype: str, eid: str, date: str) -> Path:
    """Deterministic timeline filename: sync-{ctype}-{eid}.md"""
    return TIMELINE_DIR / f"sync-{ctype}-{eid}.md"

def build_timeline_entry(ctype: str, eid: str, data: dict) -> dict | None:
    """Return timeline frontmatter dict for a given entry, or None if not syncable."""
    title = data.get("title", eid)

    if ctype == "competitions":
        date = str(data.get("date", ""))
        if not date:
            return None
        result = data.get("result", "")
        event  = data.get("event", "")
        prefix = f"{result} — " if result else ""
        desc   = data.get("description", "") or f"{result} at {event}." if result and event else f"Competed in {event or title}."
        return {
            "title":        f"{prefix}{title}",
            "date":         date,
            "type":         "achievement",
            "organization": data.get("organizer", event) or event,
            "location":     data.get("location", ""),
            "description":  desc,
            "tags":         data.get("tags", []),
        }

    if ctype == "experience":
        date = str(data.get("startDate", ""))
        if not date:
            return None
        company = data.get("company", "")
        desc    = data.get("description", "") or f"{title} at {company}."
        return {
            "title":        f"{title} — {company}",
            "date":         date,
            "type":         "work",
            "organization": company,
            "location":     data.get("location", ""),
            "description":  desc,
            "tags":         data.get("tags", []),
        }

    if ctype == "certificates":
        date = str(data.get("date", ""))
        if not date:
            return None
        issuer = data.get("issuer", "")
        desc   = data.get("description", "") or f"Completed {title}" + (f" by {issuer}." if issuer else ".")
        return {
            "title":        f"Certified — {title}" + (f" ({issuer})" if issuer else ""),
            "date":         date,
            "type":         "achievement",
            "organization": issuer,
            "description":  desc,
            "tags":         data.get("tags", []),
        }

    return None

def sync_timeline(ctype: str, eid: str, data: dict):
    """Write or overwrite the synced timeline entry for this content item."""
    entry = build_timeline_entry(ctype, eid, data)
    if entry is None:
        return
    TIMELINE_DIR.mkdir(parents=True, exist_ok=True)
    p = timeline_path(ctype, eid, entry["date"])
    write_md(p, dict(entry))

def unsync_timeline(ctype: str, eid: str):
    """Remove the synced timeline entry when the source entry is deleted."""
    p = timeline_path(ctype, eid, "")
    if p.exists():
        p.unlink()

# ── HTML shell ─────────────────────────────────────────────────────────────────
CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font: 14px/1.5 system-ui, sans-serif; background: #111; color: #e4e4e7; min-height: 100vh; }
a { color: #a1a1aa; text-decoration: none; }
a:hover { color: #fff; }

nav { background: #0d0d0d; border-bottom: 1px solid #222; padding: 10px 20px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
nav .brand { color: #22c55e; font-family: monospace; font-weight: 700; margin-right: 12px; font-size: 13px; }
nav a { padding: 5px 12px; border-radius: 5px; font-size: 13px; border: 1px solid transparent; }
nav a:hover { background: #1a1a1a; border-color: #2a2a2a; color: #e4e4e7; }
nav a.active { background: #0a1a0a; border-color: #22c55e40; color: #22c55e; }

.container { max-width: 900px; margin: 0 auto; padding: 24px 16px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-header h1 { font-size: 18px; color: #f4f4f5; }

table { width: 100%; border-collapse: collapse; background: #0d0d0d; border-radius: 8px; overflow: hidden; border: 1px solid #222; }
th { text-align: left; padding: 10px 14px; font-size: 11px; color: #52525b; text-transform: uppercase; letter-spacing: .06em; border-bottom: 1px solid #1e1e1e; background: #0a0a0a; }
td { padding: 11px 14px; border-bottom: 1px solid #1a1a1a; font-size: 13px; vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #141414; }
.id-cell { font-family: monospace; font-size: 11px; color: #52525b; }
.date-cell { font-family: monospace; font-size: 12px; color: #71717a; white-space: nowrap; }

.btn { display: inline-block; padding: 6px 14px; border-radius: 6px; font-size: 13px; cursor: pointer; border: none; font-weight: 500; text-decoration: none; }
.btn-green { background: #22c55e; color: #000; }
.btn-green:hover { background: #16a34a; color: #000; }
.btn-ghost { background: transparent; border: 1px solid #2a2a2a; color: #71717a; }
.btn-ghost:hover { border-color: #444; color: #e4e4e7; }
.btn-red { background: #ef444420; border: 1px solid #ef444440; color: #ef4444; }
.btn-red:hover { background: #ef444440; }
.btn-sm { padding: 3px 10px; font-size: 12px; }

.form-card { background: #0d0d0d; border: 1px solid #222; border-radius: 10px; padding: 28px; max-width: 700px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 11px; color: #52525b; margin-bottom: 6px; text-transform: uppercase; letter-spacing: .06em; font-weight: 600; }
.field label .req { color: #ef4444; }
input[type=text], input[type=date], input[type=number], input[type=url], textarea, select {
  width: 100%; padding: 8px 10px; background: #1a1a1a; border: 1px solid #2a2a2a;
  border-radius: 6px; color: #f4f4f5; font-size: 13px; font-family: inherit; outline: none;
}
input:focus, textarea:focus, select:focus { border-color: #22c55e; }
input[type=date] { color-scheme: dark; }
textarea { resize: vertical; min-height: 80px; }
.chk-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; }
.chk-row input { width: auto; accent-color: #22c55e; }
.chk-row label { font-size: 13px; color: #a1a1aa; text-transform: none; letter-spacing: 0; }

.form-actions { display: flex; gap: 10px; margin-top: 24px; padding-top: 20px; border-top: 1px solid #1e1e1e; }
.body-section { margin-top: 20px; padding-top: 20px; border-top: 1px solid #1e1e1e; }
.body-section label { display: block; font-size: 11px; color: #52525b; text-transform: uppercase; letter-spacing: .06em; font-weight: 600; margin-bottom: 8px; }
.empty { text-align: center; padding: 60px 20px; color: #3f3f46; }

.flash { padding: 10px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 13px; }
.flash.ok  { background: #22c55e18; border: 1px solid #22c55e40; color: #22c55e; }
.flash.err { background: #ef444418; border: 1px solid #ef444440; color: #ef4444; }

.img-field { display: flex; flex-direction: column; gap: 8px; }
.img-preview { width: 120px; height: 80px; object-fit: cover; border-radius: 6px; border: 1px solid #2a2a2a; display: block; }
.img-placeholder { width: 120px; height: 80px; border-radius: 6px; border: 1px dashed #2a2a2a; display: flex; align-items: center; justify-content: center; color: #3f3f46; font-size: 11px; }
.img-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.img-path-input { flex: 1; min-width: 160px; }
input[type=file] { background: #1a1a1a; border: 1px dashed #2a2a2a; border-radius: 6px; padding: 6px 10px; color: #71717a; font-size: 12px; cursor: pointer; width: auto; }
input[type=file]:hover { border-color: #22c55e; color: #22c55e; }
"""

def shell(title: str, body: str, active_type: str = "") -> str:
    nav_links = "".join(
        f'<a href="/{k}" class="{"active" if k == active_type else ""}">{v["label"]}</a>'
        for k, v in TYPES.items()
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)} — Admin</title>
<style>{CSS}</style>
<script>
function previewFile(input, prevId, pathId) {{
  const file = input.files[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const prev = document.getElementById(prevId);
  if (prev.tagName === 'IMG') {{
    prev.src = url;
  }} else {{
    const img = document.createElement('img');
    img.className = 'img-preview';
    img.id = prevId;
    img.src = url;
    prev.replaceWith(img);
  }}
  document.getElementById(pathId).value = file.name + ' (uploading on save...)';
}}
</script>
</head>
<body>
<nav>
  <span class="brand">/z3roday ~ admin</span>
  {nav_links}
</nav>
<div class="container">{body}</div>
</body>
</html>"""

def render_field(f: dict, val) -> str:
    name = f["name"]
    label = f["label"]
    req = f.get("required", False)
    req_html = '<span class="req"> *</span>' if req else ""
    ftype = f.get("type", "text")

    if ftype == "checkbox":
        checked = "checked" if val else ""
        return f'<div class="chk-row"><input type="checkbox" name="{h(name)}" id="f-{h(name)}" value="true" {checked}><label for="f-{h(name)}">{h(label)}</label></div>'

    if ftype == "textarea":
        return f'<div class="field"><label for="f-{h(name)}">{h(label)}{req_html}</label><textarea name="{h(name)}" id="f-{h(name)}" {"required" if req else ""}>{h(val or "")}</textarea></div>'

    if ftype == "select":
        opts = "".join(
            f'<option value="{h(o)}" {"selected" if str(val or "") == o else ""}>{h(o)}</option>'
            for o in f.get("options", [])
        )
        return f'<div class="field"><label for="f-{h(name)}">{h(label)}</label><select name="{h(name)}" id="f-{h(name)}">{opts}</select></div>'

    if ftype == "tags":
        tag_str = ", ".join(val) if isinstance(val, list) else (val or "")
        return f'<div class="field"><label for="f-{h(name)}">{h(label)}</label><input type="text" name="{h(name)}" id="f-{h(name)}" value="{h(tag_str)}" placeholder="tag1, tag2, tag3"></div>'

    if ftype == "date":
        date_val = str(val)[:10] if val else ""
        return f'<div class="field"><label for="f-{h(name)}">{h(label)}{req_html}</label><input type="date" name="{h(name)}" id="f-{h(name)}" value="{h(date_val)}" {"required" if req else ""}></div>'

    if ftype == "number":
        return f'<div class="field"><label for="f-{h(name)}">{h(label)}</label><input type="number" name="{h(name)}" id="f-{h(name)}" value="{h(val if val is not None else "")}"></div>'

    if ftype == "image":
        preview = (f'<img class="img-preview" src="{h(val)}" id="prev-{h(name)}">'
                   if val else f'<div class="img-placeholder" id="prev-{h(name)}">no image</div>')
        return (
            f'<div class="field"><label>{h(label)}</label>'
            f'<div class="img-field">'
            f'{preview}'
            f'<div class="img-row">'
            f'<input class="img-path-input" type="text" name="{h(name)}" id="f-{h(name)}" value="{h(val or "")}" placeholder="/images/..." '
            f'oninput="document.getElementById(\'prev-{h(name)}\').src=this.value">'
            f'<input type="file" name="_file_{h(name)}" accept="image/*" '
            f'onchange="previewFile(this,\'prev-{h(name)}\',\'f-{h(name)}\')">'
            f'</div>'
            f'</div></div>'
        )

    # default: text
    return f'<div class="field"><label for="f-{h(name)}">{h(label)}{req_html}</label><input type="text" name="{h(name)}" id="f-{h(name)}" value="{h(val or "")}" {"required" if req else ""}></div>'

def extract_field(f: dict, form: dict):
    name = f["name"]
    ftype = f.get("type", "text")
    raw = form.get(name, "")
    if ftype == "checkbox":
        return name, raw == "true"
    if ftype == "tags":
        return name, [t.strip() for t in raw.split(",") if t.strip()]
    if ftype == "number":
        try: return name, int(raw)
        except: return name, None
    # image: path comes from text input (file upload handled separately)
    return name, raw

def image_fields(cfg: dict) -> list:
    return [f for f in cfg["fields"] if f.get("type") == "image"]

async def handle_image_uploads(ctype: str, cfg: dict, form_data, data: dict):
    """Check for uploaded files and save them, updating data paths."""
    for f in image_fields(cfg):
        name = f["name"]
        file_key = f"_file_{name}"
        uploaded = form_data.getlist(file_key)
        if not uploaded:
            continue
        upload_file = uploaded[0]
        if not hasattr(upload_file, "filename") or not upload_file.filename:
            continue
        folder = f.get("folder", f"images/{ctype}")
        dest = PUBLIC_DIR / folder
        dest.mkdir(parents=True, exist_ok=True)
        fname = Path(upload_file.filename).name
        out = dest / fname
        out.write_bytes(await upload_file.read())
        data[name] = f"/{folder}/{fname}"

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse("/projects")

@app.get("/{ctype}", response_class=HTMLResponse)
def list_view(ctype: str, flash: str = "", flash_type: str = "ok"):
    if ctype not in TYPES:
        raise HTTPException(404)
    cfg = TYPES[ctype]
    entries = list_entries(ctype)

    flash_html = f'<div class="flash {h(flash_type)}">{h(flash)}</div>' if flash else ""
    if not entries:
        rows = '<tr><td colspan="3" class="empty">No entries yet. <a href="/{ctype}/new">Add one →</a></td></tr>'
    else:
        def make_row(e):
            eid = e["id"]
            title = h(e.get("title") or eid)
            date  = h(e.get("date", ""))
            return (
                f'<tr>'
                f'<td><strong>{title}</strong></td>'
                f'<td class="date-cell">{date}</td>'
                f'<td class="id-cell">{h(eid)}</td>'
                f'<td style="text-align:right;white-space:nowrap">'
                f'<a class="btn btn-ghost btn-sm" href="/{ctype}/{eid}/edit">Edit</a> '
                f'<form method="post" action="/{ctype}/{eid}/delete" style="display:inline"'
                f' onsubmit="return confirm(\'Delete?\')">'
                f'<button class="btn btn-red btn-sm" type="submit">Delete</button></form>'
                f'</td></tr>'
            )
        rows = "".join(make_row(e) for e in entries)

    body = f"""
{flash_html}
<div class="page-header">
  <h1>{h(cfg["label"])}</h1>
  <a class="btn btn-green" href="/{ctype}/new">+ New</a>
</div>
<table>
  <thead><tr><th>Title</th><th>Date</th><th>ID</th><th></th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""
    return shell(cfg["label"], body, active_type=ctype)

@app.get("/{ctype}/new", response_class=HTMLResponse)
def new_form(ctype: str):
    if ctype not in TYPES:
        raise HTTPException(404)
    cfg = TYPES[ctype]
    fields_html = "".join(render_field(f, None) for f in cfg["fields"])
    body = f"""
<div class="page-header">
  <h1>New {h(cfg["label"])}</h1>
  <a class="btn btn-ghost" href="/{ctype}">← Back</a>
</div>
<form method="post" action="/{ctype}/new" class="form-card" enctype="multipart/form-data">
  {fields_html}
  <div class="body-section">
    <label>Content (Markdown)</label>
    <textarea name="_body" style="min-height:140px;font-family:monospace;font-size:12px" placeholder="Write content in Markdown..."></textarea>
  </div>
  <div class="form-actions">
    <a class="btn btn-ghost" href="/{ctype}">Cancel</a>
    <button class="btn btn-green" type="submit">Save</button>
  </div>
</form>"""
    return shell(f"New {cfg['label']}", body, active_type=ctype)

@app.post("/{ctype}/new")
async def create_entry(ctype: str, request: Request):
    if ctype not in TYPES:
        raise HTTPException(404)
    form = await request.form()
    cfg = TYPES[ctype]
    form_dict = dict(form)
    data = {}
    for f in cfg["fields"]:
        k, v = extract_field(f, form_dict)
        if v is not None and v != "" and v != []:
            data[k] = v
    data["_body"] = form_dict.get("_body", "")
    await handle_image_uploads(ctype, cfg, form, data)

    d = content_dir(ctype)
    d.mkdir(parents=True, exist_ok=True)
    slug = safe_slug(data.get("title", "entry"))
    p = d / f"{slug}.md"
    i = 1
    while p.exists():
        p = d / f"{slug}-{i}.md"
        i += 1
    write_md(p, data)
    sync_timeline(ctype, p.stem, dict(data))
    return RedirectResponse(f"/{ctype}?flash=Created+{p.stem}&flash_type=ok", status_code=303)

@app.get("/{ctype}/{eid}/edit", response_class=HTMLResponse)
def edit_form(ctype: str, eid: str):
    if ctype not in TYPES:
        raise HTTPException(404)
    p = content_dir(ctype) / f"{eid}.md"
    if not p.exists():
        raise HTTPException(404)
    cfg = TYPES[ctype]
    data = parse_md(p)
    fields_html = "".join(render_field(f, data.get(f["name"])) for f in cfg["fields"])
    body = f"""
<div class="page-header">
  <h1>Edit — {h(data.get("title") or eid)}</h1>
  <a class="btn btn-ghost" href="/{ctype}">← Back</a>
</div>
<form method="post" action="/{ctype}/{h(eid)}/edit" class="form-card" enctype="multipart/form-data">
  {fields_html}
  <div class="body-section">
    <label>Content (Markdown)</label>
    <textarea name="_body" style="min-height:140px;font-family:monospace;font-size:12px">{h(data.get("_body",""))}</textarea>
  </div>
  <div class="form-actions">
    <a class="btn btn-ghost" href="/{ctype}">Cancel</a>
    <button class="btn btn-green" type="submit">Save</button>
  </div>
</form>"""
    return shell(f"Edit {cfg['label']}", body, active_type=ctype)

@app.post("/{ctype}/{eid}/edit")
async def update_entry(ctype: str, eid: str, request: Request):
    if ctype not in TYPES:
        raise HTTPException(404)
    p = content_dir(ctype) / f"{eid}.md"
    if not p.exists():
        raise HTTPException(404)
    form = await request.form()
    cfg = TYPES[ctype]
    form_dict = dict(form)
    data = {}
    for f in cfg["fields"]:
        k, v = extract_field(f, form_dict)
        data[k] = v
    data["_body"] = form_dict.get("_body", "")
    await handle_image_uploads(ctype, cfg, form, data)
    write_md(p, data)
    sync_timeline(ctype, eid, dict(data))
    return RedirectResponse(f"/{ctype}?flash=Saved+{eid}&flash_type=ok", status_code=303)

@app.post("/{ctype}/{eid}/delete")
def delete_entry(ctype: str, eid: str):
    if ctype not in TYPES:
        raise HTTPException(404)
    p = content_dir(ctype) / f"{eid}.md"
    if p.exists():
        p.unlink()
    unsync_timeline(ctype, eid)
    return RedirectResponse(f"/{ctype}?flash=Deleted+{eid}&flash_type=ok", status_code=303)

@app.post("/upload/{folder:path}")
async def upload_file(folder: str, file: UploadFile = File(...)):
    dest = PUBLIC_DIR / folder
    dest.mkdir(parents=True, exist_ok=True)
    name = Path(file.filename).name
    out  = dest / name
    out.write_bytes(await file.read())
    return {"path": f"/{folder}/{name}"}

if __name__ == "__main__":
    print("\n  Portfolio Admin → http://localhost:8888\n")
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="warning")
