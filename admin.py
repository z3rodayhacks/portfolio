#!/usr/bin/env python3
"""
Portfolio Admin Dashboard
Run: python admin.py
Open: http://localhost:8888
"""
import json, re, sys
from pathlib import Path
import yaml
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

ROOT        = Path(__file__).parent
CONTENT_DIR = ROOT / "src" / "content"
PUBLIC_DIR  = ROOT / "public"

# ── Schema config (mirrors content.config.ts) ─────────────────────────────────
TYPES = {
    "projects": {
        "label": "Projects",
        "dir": str(CONTENT_DIR / "projects"),
        "fields": [
            {"name":"title",       "type":"text",     "required":True,  "label":"Title"},
            {"name":"description", "type":"textarea",  "required":True,  "label":"Description"},
            {"name":"date",        "type":"date",      "required":True,  "label":"Date"},
            {"name":"status",      "type":"select",    "required":False, "label":"Status",     "options":["completed","in-progress","archived"], "default":"completed"},
            {"name":"category",    "type":"text",      "required":False, "label":"Category"},
            {"name":"github",      "type":"text",      "required":False, "label":"GitHub URL"},
            {"name":"demo",        "type":"text",      "required":False, "label":"Demo URL"},
            {"name":"thumbnail",   "type":"image",     "required":False, "label":"Thumbnail",  "folder":"images/projects"},
            {"name":"techStack",   "type":"tags",      "required":False, "label":"Tech Stack"},
            {"name":"tags",        "type":"tags",      "required":False, "label":"Tags"},
            {"name":"featured",    "type":"checkbox",  "required":False, "label":"Featured on homepage"},
        ],
    },
    "blog": {
        "label": "Blog",
        "dir": str(CONTENT_DIR / "blog"),
        "fields": [
            {"name":"title",       "type":"text",     "required":True,  "label":"Title"},
            {"name":"description", "type":"textarea",  "required":True,  "label":"Description"},
            {"name":"date",        "type":"date",      "required":True,  "label":"Date"},
            {"name":"thumbnail",   "type":"image",     "required":False, "label":"Thumbnail",  "folder":"images/blog"},
            {"name":"tags",        "type":"tags",      "required":False, "label":"Tags"},
            {"name":"featured",    "type":"checkbox",  "required":False, "label":"Featured"},
            {"name":"draft",       "type":"checkbox",  "required":False, "label":"Draft (hidden from site)"},
        ],
    },
    "talks": {
        "label": "Talks",
        "dir": str(CONTENT_DIR / "talks"),
        "fields": [
            {"name":"title",       "type":"text",     "required":True,  "label":"Title"},
            {"name":"description", "type":"textarea",  "required":True,  "label":"Description"},
            {"name":"date",        "type":"date",      "required":True,  "label":"Date"},
            {"name":"event",       "type":"text",      "required":True,  "label":"Event Name"},
            {"name":"location",    "type":"text",      "required":False, "label":"Location"},
            {"name":"linkedin",    "type":"text",      "required":False, "label":"LinkedIn Post URL"},
            {"name":"slides",      "type":"text",      "required":False, "label":"Slides URL"},
            {"name":"video",       "type":"text",      "required":False, "label":"YouTube URL"},
            {"name":"thumbnail",   "type":"image",     "required":False, "label":"Thumbnail",  "folder":"images/talks"},
            {"name":"images",      "type":"images",    "required":False, "label":"Gallery Images", "folder":"images/talks"},
            {"name":"tags",        "type":"tags",      "required":False, "label":"Tags"},
            {"name":"featured",    "type":"checkbox",  "required":False, "label":"Featured"},
        ],
    },
    "certificates": {
        "label": "Certificates",
        "dir": str(CONTENT_DIR / "certificates"),
        "fields": [
            {"name":"title",         "type":"text",    "required":True,  "label":"Certificate Name"},
            {"name":"issuer",        "type":"text",    "required":True,  "label":"Issuer"},
            {"name":"date",          "type":"date",    "required":True,  "label":"Issue Date"},
            {"name":"expiry",        "type":"date",    "required":False, "label":"Expiry Date"},
            {"name":"credentialId",  "type":"text",    "required":False, "label":"Credential ID"},
            {"name":"credentialUrl", "type":"text",    "required":False, "label":"Verification URL"},
            {"name":"thumbnail",     "type":"image",   "required":False, "label":"Badge Image", "folder":"certificates"},
            {"name":"tags",          "type":"tags",    "required":False, "label":"Tags"},
            {"name":"featured",      "type":"checkbox","required":False, "label":"Featured"},
        ],
    },
    "timeline": {
        "label": "Timeline",
        "dir": str(CONTENT_DIR / "timeline"),
        "fields": [
            {"name":"title",        "type":"text",    "required":True,  "label":"Title"},
            {"name":"date",         "type":"date",    "required":True,  "label":"Date"},
            {"name":"description",  "type":"textarea","required":True,  "label":"Description"},
            {"name":"type",         "type":"select",  "required":False, "label":"Type", "options":["work","education","achievement","project","other"], "default":"other"},
            {"name":"organization", "type":"text",    "required":False, "label":"Organization"},
            {"name":"location",     "type":"text",    "required":False, "label":"Location"},
            {"name":"tags",         "type":"tags",    "required":False, "label":"Tags"},
        ],
    },
    "competitions": {
        "label": "Competitions",
        "dir": str(CONTENT_DIR / "competitions"),
        "fields": [
            {"name":"title",       "type":"text",     "required":True,  "label":"Competition Title"},
            {"name":"description", "type":"textarea",  "required":True,  "label":"Description"},
            {"name":"date",        "type":"date",      "required":True,  "label":"Date"},
            {"name":"event",       "type":"text",      "required":True,  "label":"Event / Competition Name"},
            {"name":"organizer",   "type":"text",      "required":False, "label":"Organizer"},
            {"name":"location",    "type":"text",      "required":False, "label":"Location"},
            {"name":"result",      "type":"text",      "required":False, "label":"Result (e.g. Winner, Finalist)"},
            {"name":"team",        "type":"text",      "required":False, "label":"Team Name"},
            {"name":"teamSize",    "type":"number",    "required":False, "label":"Team Size"},
            {"name":"project",     "type":"text",      "required":False, "label":"What was built / done"},
            {"name":"github",      "type":"text",      "required":False, "label":"GitHub URL"},
            {"name":"linkedin",    "type":"text",      "required":False, "label":"LinkedIn Post URL"},
            {"name":"certificate", "type":"text",      "required":False, "label":"Certificate path or URL"},
            {"name":"thumbnail",   "type":"image",     "required":False, "label":"Thumbnail",  "folder":"images/competitions"},
            {"name":"images",      "type":"images",    "required":False, "label":"Gallery Images", "folder":"images/competitions"},
            {"name":"tags",        "type":"tags",      "required":False, "label":"Tags"},
            {"name":"featured",    "type":"checkbox",  "required":False, "label":"Featured"},
        ],
    },
    "experience": {
        "label": "Experience",
        "dir": str(CONTENT_DIR / "experience"),
        "fields": [
            {"name":"title",       "type":"text",    "required":True,  "label":"Job Title"},
            {"name":"company",     "type":"text",    "required":True,  "label":"Company"},
            {"name":"location",    "type":"text",    "required":False, "label":"Location"},
            {"name":"startDate",   "type":"date",    "required":True,  "label":"Start Date"},
            {"name":"endDate",     "type":"date",    "required":False, "label":"End Date"},
            {"name":"current",     "type":"checkbox","required":False, "label":"Currently working here"},
            {"name":"description", "type":"textarea","required":True,  "label":"Description"},
            {"name":"tags",        "type":"tags",    "required":False, "label":"Tags"},
            {"name":"order",       "type":"number",  "required":False, "label":"Display order (higher = first)", "default":0},
        ],
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────────
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
        if isinstance(v, bool):
            clean[k] = v
        elif isinstance(v, list):
            clean[k] = [str(i) for i in v]
        else:
            clean[k] = v
    fm = yaml.dump(clean, allow_unicode=True, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm}---\n\n{body}\n", encoding="utf-8")

def safe_slug(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9-]", "-", title.lower())).strip("-")[:50]

# ── API ────────────────────────────────────────────────────────────────────────
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/types")
def get_types():
    return {k: {"label": v["label"], "fields": v["fields"]} for k, v in TYPES.items()}

@app.get("/api/{ctype}")
def list_entries(ctype: str):
    if ctype not in TYPES:
        raise HTTPException(404)
    d = Path(TYPES[ctype]["dir"])
    if not d.exists():
        return []
    return sorted([parse_md(f) for f in d.glob("*.md")], key=lambda x: x.get("date", ""), reverse=True)

@app.get("/api/{ctype}/{eid}")
def get_entry(ctype: str, eid: str):
    if ctype not in TYPES:
        raise HTTPException(404)
    p = Path(TYPES[ctype]["dir"]) / f"{eid}.md"
    if not p.exists():
        raise HTTPException(404)
    return parse_md(p)

@app.post("/api/{ctype}")
async def create_entry(ctype: str, request: Request):
    if ctype not in TYPES:
        raise HTTPException(404)
    data = await request.json()
    d = Path(TYPES[ctype]["dir"])
    d.mkdir(parents=True, exist_ok=True)
    slug = data.pop("_id", None) or safe_slug(data.get("title", "entry"))
    p = d / f"{slug}.md"
    i = 1
    while p.exists():
        p = d / f"{slug}-{i}.md"
        i += 1
    write_md(p, dict(data))
    return {"id": p.stem, "ok": True}

@app.put("/api/{ctype}/{eid}")
async def update_entry(ctype: str, eid: str, request: Request):
    if ctype not in TYPES:
        raise HTTPException(404)
    p = Path(TYPES[ctype]["dir"]) / f"{eid}.md"
    if not p.exists():
        raise HTTPException(404)
    data = await request.json()
    write_md(p, dict(data))
    return {"ok": True}

@app.delete("/api/{ctype}/{eid}")
def delete_entry(ctype: str, eid: str):
    if ctype not in TYPES:
        raise HTTPException(404)
    p = Path(TYPES[ctype]["dir"]) / f"{eid}.md"
    if p.exists():
        p.unlink()
    return {"ok": True}

@app.post("/api/upload/{folder:path}")
async def upload_file(folder: str, file: UploadFile = File(...)):
    dest = PUBLIC_DIR / folder
    dest.mkdir(parents=True, exist_ok=True)
    name = Path(file.filename).name
    out  = dest / name
    out.write_bytes(await file.read())
    return {"path": f"/{folder}/{name}"}

@app.get("/api/images/{folder:path}")
def list_images(folder: str):
    d = PUBLIC_DIR / folder
    if not d.exists():
        return []
    exts = {".jpg",".jpeg",".png",".gif",".webp",".svg"}
    return [f"/{folder}/{f.name}" for f in sorted(d.iterdir()) if f.suffix.lower() in exts]

# ── UI ─────────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def admin_ui():
    return HTML

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Portfolio Admin</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:#080808;color:#e4e4e7;display:flex;height:100vh;overflow:hidden;font-size:14px}
.sidebar{width:190px;background:#0f0f0f;border-right:1px solid #1e1e1e;display:flex;flex-direction:column;flex-shrink:0}
.sidebar-title{padding:14px 16px;font-family:monospace;font-size:13px;color:#22c55e;border-bottom:1px solid #1e1e1e;font-weight:700}
.sidebar nav a{display:flex;align-items:center;gap:8px;padding:9px 16px;color:#71717a;text-decoration:none;font-size:13px;border-left:2px solid transparent;transition:all .15s}
.sidebar nav a:hover{color:#e4e4e7;background:#141414}
.sidebar nav a.active{color:#22c55e;border-left-color:#22c55e;background:#0a1a0a}
.main{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}
.topbar{padding:12px 20px;border-bottom:1px solid #1e1e1e;display:flex;align-items:center;justify-content:space-between;gap:12px;background:#0c0c0c}
.topbar h2{font-size:15px;font-weight:600;color:#f4f4f5}
.topbar-actions{display:flex;gap:8px}
.content{flex:1;overflow-y:auto;padding:20px}
.btn{padding:6px 14px;border-radius:6px;font-size:13px;cursor:pointer;border:none;transition:all .15s;font-weight:500}
.btn-green{background:#22c55e;color:#000}
.btn-green:hover{background:#16a34a}
.btn-ghost{background:transparent;border:1px solid #2a2a2a;color:#71717a}
.btn-ghost:hover{border-color:#444;color:#e4e4e7}
.btn-red{background:#ef444420;border:1px solid #ef444440;color:#ef4444}
.btn-red:hover{background:#ef444440}
.btn-sm{padding:3px 10px;font-size:12px}
.entry-list{display:flex;flex-direction:column;gap:6px}
.entry-row{display:flex;align-items:center;gap:12px;padding:11px 14px;background:#111;border:1px solid #1e1e1e;border-radius:8px;transition:border-color .15s}
.entry-row:hover{border-color:#2a2a2a}
.entry-info{flex:1;min-width:0}
.entry-title{font-size:13px;font-weight:500;color:#f4f4f5;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.entry-meta{font-size:11px;color:#3f3f46;font-family:monospace;margin-top:2px}
.entry-actions{display:flex;gap:6px;flex-shrink:0}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:100;display:flex;align-items:flex-start;justify-content:center;padding:32px 16px;overflow-y:auto}
.modal{background:#111;border:1px solid #222;border-radius:12px;width:100%;max-width:620px;padding:24px;position:relative;margin:auto}
.modal-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.modal-header h3{font-size:15px;font-weight:600;color:#f4f4f5}
.close-btn{background:none;border:none;color:#52525b;cursor:pointer;font-size:20px;line-height:1;padding:4px}
.close-btn:hover{color:#fff}
.field{margin-bottom:14px}
.field>label{display:block;font-size:11px;color:#52525b;margin-bottom:5px;text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.req{color:#ef4444}
input[type=text],input[type=date],input[type=number],textarea,select{width:100%;padding:8px 10px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:6px;color:#f4f4f5;font-size:13px;outline:none;transition:border-color .15s;font-family:inherit}
input:focus,textarea:focus,select:focus{border-color:#22c55e}
textarea{resize:vertical;min-height:72px}
.chk-row{display:flex;align-items:center;gap:8px}
.chk-row input{width:auto;accent-color:#22c55e}
.chk-row label{font-size:13px;color:#a1a1aa;text-transform:none;letter-spacing:0}
.tags-wrap{display:flex;flex-wrap:wrap;gap:5px;padding:6px 10px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:6px;min-height:38px;cursor:text;transition:border-color .15s}
.tags-wrap:focus-within{border-color:#22c55e}
.tag-chip{display:inline-flex;align-items:center;gap:4px;padding:2px 7px;background:#22c55e18;border:1px solid #22c55e35;border-radius:4px;font-size:11px;color:#22c55e}
.tag-chip button{background:none;border:none;color:#22c55e;cursor:pointer;font-size:14px;line-height:1;padding:0 1px}
.tag-chip button:hover{color:#fff}
.tags-input{border:none;background:transparent;color:#f4f4f5;font-size:13px;outline:none;flex:1;min-width:80px;padding:2px 0}
.img-upload-area{display:flex;flex-direction:column;gap:6px}
.img-preview-box{width:90px;height:66px;border-radius:6px;border:1px solid #2a2a2a;object-fit:cover;background:#1a1a1a}
.upload-label{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#1a1a1a;border:1px dashed #2a2a2a;border-radius:6px;color:#71717a;cursor:pointer;font-size:12px;transition:all .15s;width:fit-content}
.upload-label:hover{border-color:#22c55e;color:#22c55e}
.imgs-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
.img-thumb-wrap{position:relative}
.img-thumb-wrap img{width:80px;height:60px;object-fit:cover;border-radius:6px;border:1px solid #2a2a2a;display:block}
.img-thumb-wrap .rm{position:absolute;top:-5px;right:-5px;width:17px;height:17px;background:#ef4444;border:none;border-radius:50%;color:#fff;cursor:pointer;font-size:11px;display:flex;align-items:center;justify-content:center;line-height:1}
.body-area{width:100%;padding:10px;background:#0a0a0a;border:1px solid #2a2a2a;border-radius:6px;color:#e4e4e7;font-family:monospace;font-size:12px;min-height:110px;resize:vertical;outline:none;transition:border-color .15s}
.body-area:focus{border-color:#22c55e}
.modal-footer{display:flex;gap:8px;justify-content:flex-end;margin-top:20px;padding-top:16px;border-top:1px solid #1e1e1e}
.empty-state{text-align:center;padding:60px 20px;color:#3f3f46}
.empty-state p{margin-bottom:8px}
.toast{position:fixed;bottom:20px;right:20px;padding:9px 16px;background:#141414;border:1px solid #2a2a2a;border-radius:8px;font-size:13px;z-index:999;animation:toastIn .2s ease}
.toast.ok{border-color:#22c55e;color:#22c55e}
.toast.err{border-color:#ef4444;color:#ef4444}
@keyframes toastIn{from{transform:translateY(8px);opacity:0}to{transform:translateY(0);opacity:1}}
.section-sep{font-size:11px;color:#3f3f46;text-transform:uppercase;letter-spacing:.08em;margin:20px 0 10px;padding-bottom:6px;border-bottom:1px solid #1a1a1a}
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-title">/z3roday ~ admin</div>
  <nav id="nav">
    <a href="#" data-type="projects" class="active">📁 Projects</a>
    <a href="#" data-type="blog">📝 Blog</a>
    <a href="#" data-type="talks">🎤 Talks</a>
    <a href="#" data-type="certificates">🏅 Certificates</a>
    <a href="#" data-type="competitions">🏆 Competitions</a>
    <a href="#" data-type="timeline">📅 Timeline</a>
    <a href="#" data-type="experience">💼 Experience</a>
  </nav>
</div>

<div class="main">
  <div class="topbar">
    <h2 id="section-title">Projects</h2>
    <div class="topbar-actions">
      <button class="btn btn-ghost" onclick="toast('Run: npm run build  in terminal','ok')">ⓘ How to build</button>
      <button class="btn btn-green" onclick="openNew()">+ New</button>
    </div>
  </div>
  <div class="content" id="content"><div class="empty-state"><p>Loading...</p></div></div>
</div>

<div class="overlay" id="overlay" style="display:none" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-header">
      <h3 id="modal-title">New Entry</h3>
      <button class="close-btn" onclick="closeModal()">×</button>
    </div>
    <div id="form-fields"></div>
    <div class="section-sep">Content (Markdown)</div>
    <textarea class="body-area" id="f-_body" placeholder="Write your content here in Markdown..."></textarea>
    <div class="modal-footer">
      <button class="btn btn-ghost" onclick="closeModal()">Cancel</button>
      <button class="btn btn-green" onclick="saveEntry()">Save</button>
    </div>
  </div>
</div>

<script>
let currentType = 'projects';
let editingId   = null;
let SCHEMA      = {};
let tagData     = {};

// ── Init ──────────────────────────────────────────────────────────────────────
(async () => {
  const r = await fetch('/api/types');
  SCHEMA  = await r.json();
  loadEntries();
})();

document.getElementById('nav').addEventListener('click', e => {
  const a = e.target.closest('[data-type]');
  if (!a) return; e.preventDefault();
  document.querySelectorAll('#nav a').forEach(x => x.classList.remove('active'));
  a.classList.add('active');
  currentType = a.dataset.type;
  document.getElementById('section-title').textContent = SCHEMA[currentType]?.label || currentType;
  loadEntries();
});

// ── Load list ─────────────────────────────────────────────────────────────────
async function loadEntries() {
  const entries = await (await fetch(`/api/${currentType}`)).json();
  const el = document.getElementById('content');
  if (!entries.length) {
    el.innerHTML = '<div class="empty-state"><p>No entries yet.</p><p style="font-size:12px;color:#27272a">Click + New to add one.</p></div>';
    return;
  }
  el.innerHTML = '<div class="entry-list">' + entries.map(e => `
    <div class="entry-row">
      <div class="entry-info">
        <div class="entry-title">${e.title || e.id}</div>
        <div class="entry-meta">${e.date || ''} · ${e.id}</div>
      </div>
      <div class="entry-actions">
        <button class="btn btn-ghost btn-sm" onclick="editEntry('${e.id}')">Edit</button>
        <button class="btn btn-red   btn-sm" onclick="deleteEntry('${e.id}')">Delete</button>
      </div>
    </div>`).join('') + '</div>';
}

// ── Modal ─────────────────────────────────────────────────────────────────────
function openNew()            { editingId = null; renderForm({}); }
async function editEntry(id)  {
  const data = await (await fetch(`/api/${currentType}/${id}`)).json();
  editingId  = id;
  renderForm(data);
}
function closeModal() { document.getElementById('overlay').style.display = 'none'; }

function renderForm(data) {
  const cfg = SCHEMA[currentType];
  document.getElementById('modal-title').textContent = editingId ? `Edit — ${data.title || editingId}` : `New ${cfg.label}`;
  document.getElementById('overlay').style.display = 'flex';
  document.getElementById('f-_body').value = data._body || '';
  tagData = {};
  const container = document.getElementById('form-fields');
  container.innerHTML = '';

  cfg.fields.forEach(f => {
    const val = data[f.name];
    const div = document.createElement('div');

    if (f.type === 'checkbox') {
      div.innerHTML = `<div class="chk-row"><input type="checkbox" id="f-${f.name}" ${val ? 'checked' : ''}><label for="f-${f.name}">${f.label}</label></div>`;
    } else if (f.type === 'textarea') {
      div.className = 'field';
      div.innerHTML = `<label>${f.label}${f.required?'<span class="req"> *</span>':''}</label>
        <textarea id="f-${f.name}" ${f.required?'required':''}>${val||''}</textarea>`;
    } else if (f.type === 'select') {
      div.className = 'field';
      const opts = f.options.map(o=>`<option value="${o}" ${(val||f.default)===o?'selected':''}>${o}</option>`).join('');
      div.innerHTML = `<label>${f.label}</label><select id="f-${f.name}">${opts}</select>`;
    } else if (f.type === 'tags') {
      div.className = 'field';
      tagData[f.name] = Array.isArray(val) ? [...val] : [];
      div.innerHTML = `<label>${f.label}</label>
        <div class="tags-wrap" id="tw-${f.name}" onclick="document.getElementById('ti-${f.name}').focus()"></div>`;
      setTimeout(() => renderTags(f.name), 0);
    } else if (f.type === 'image') {
      div.className = 'field';
      div.innerHTML = `<label>${f.label}</label>
        <div class="img-upload-area">
          <div id="imgprev-${f.name}">${val?`<img class="img-preview-box" src="${val}">`:'<div class="img-preview-box" style="display:flex;align-items:center;justify-content:center;color:#3f3f46;font-size:11px">no image</div>'}</div>
          <input type="hidden" id="f-${f.name}" value="${val||''}">
          <label class="upload-label"><input type="file" accept="image/*" style="display:none" onchange="uploadSingle(this,'${f.name}','${f.folder||'images'}')">↑ Upload image</label>
          <input type="text" placeholder="or type path: /images/..." value="${val||''}" oninput="document.getElementById('f-${f.name}').value=this.value;updateImgPrev('${f.name}',this.value)" style="margin-top:4px">
        </div>`;
    } else if (f.type === 'images') {
      div.className = 'field';
      const existing = Array.isArray(val) ? val : [];
      div.innerHTML = `<label>${f.label}</label>
        <div class="imgs-grid" id="imgsgrid-${f.name}"></div>
        <input type="hidden" id="f-${f.name}" value='${JSON.stringify(existing)}'>
        <label class="upload-label" style="margin-top:8px"><input type="file" accept="image/*" multiple style="display:none" onchange="uploadMulti(this,'${f.name}','${f.folder||'images/talks'}')">↑ Add images</label>`;
      setTimeout(() => renderImgsGrid(f.name, existing), 0);
    } else {
      div.className = 'field';
      div.innerHTML = `<label>${f.label}${f.required?'<span class="req"> *</span>':''}</label>
        <input type="${f.type==='number'?'number':'text'}" id="f-${f.name}" value="${val!==undefined&&val!==null?val:(f.default??'')}" ${f.required?'required':''} placeholder="${f.label}">`;
    }
    container.appendChild(div);
  });
}

// ── Tags ──────────────────────────────────────────────────────────────────────
function renderTags(name) {
  const wrap = document.getElementById(`tw-${name}`);
  if (!wrap) return;
  wrap.innerHTML = (tagData[name]||[]).map(t =>
    `<span class="tag-chip">${t}<button type="button" onclick="removeTag('${name}','${t}')">×</button></span>`
  ).join('') + `<input class="tags-input" id="ti-${name}" placeholder="type & press Enter" onkeydown="tagKey(event,'${name}')">`;
}
function tagKey(e, name) {
  if (e.key!=='Enter'&&e.key!==',') return;
  e.preventDefault();
  const v = e.target.value.trim();
  if (!v) return;
  tagData[name] = tagData[name]||[];
  if (!tagData[name].includes(v)) tagData[name].push(v);
  renderTags(name);
}
function removeTag(name, tag) {
  tagData[name] = (tagData[name]||[]).filter(t=>t!==tag);
  renderTags(name);
}

// ── Image helpers ─────────────────────────────────────────────────────────────
function updateImgPrev(name, path) {
  const box = document.getElementById(`imgprev-${name}`);
  if (!box) return;
  box.innerHTML = path ? `<img class="img-preview-box" src="${path}" onerror="this.style.opacity=.3">` : '';
}
async function uploadSingle(input, name, folder) {
  const fd = new FormData(); fd.append('file', input.files[0]);
  const data = await (await fetch(`/api/upload/${folder}`, {method:'POST',body:fd})).json();
  document.getElementById(`f-${name}`).value = data.path;
  updateImgPrev(name, data.path);
  // update text input too
  const txt = input.closest('.img-upload-area')?.querySelector('input[type=text]');
  if (txt) txt.value = data.path;
  toast('Uploaded!','ok');
}
async function uploadMulti(input, name, folder) {
  const hidden = document.getElementById(`f-${name}`);
  let list = JSON.parse(hidden.value||'[]');
  for (const file of input.files) {
    const fd = new FormData(); fd.append('file', file);
    const d = await (await fetch(`/api/upload/${folder}`,{method:'POST',body:fd})).json();
    list.push(d.path);
  }
  hidden.value = JSON.stringify(list);
  renderImgsGrid(name, list);
  toast(`${input.files.length} uploaded!`,'ok');
}
function renderImgsGrid(name, list) {
  const grid = document.getElementById(`imgsgrid-${name}`);
  if (!grid) return;
  grid.innerHTML = list.map((img,i)=>`
    <div class="img-thumb-wrap">
      <img src="${img}" onerror="this.style.opacity=.3" title="${img}">
      <button class="rm" type="button" onclick="removeImg('${name}',${i})">×</button>
    </div>`).join('');
}
function removeImg(name, idx) {
  const h = document.getElementById(`f-${name}`);
  const list = JSON.parse(h.value||'[]');
  list.splice(idx,1); h.value = JSON.stringify(list);
  renderImgsGrid(name, list);
}

// ── Save ──────────────────────────────────────────────────────────────────────
async function saveEntry() {
  const cfg = SCHEMA[currentType];
  const data = {};
  for (const f of cfg.fields) {
    if (f.type==='checkbox') {
      data[f.name] = document.getElementById(`f-${f.name}`)?.checked||false;
    } else if (f.type==='tags') {
      data[f.name] = tagData[f.name]||[];
    } else if (f.type==='images') {
      data[f.name] = JSON.parse(document.getElementById(`f-${f.name}`)?.value||'[]');
    } else {
      const el = document.getElementById(`f-${f.name}`);
      const v  = el?.value?.trim()||'';
      if (v!=='') data[f.name] = f.type==='number' ? Number(v)||0 : v;
    }
  }
  data._body = document.getElementById('f-_body')?.value||'';

  const method = editingId?'PUT':'POST';
  const url    = editingId?`/api/${currentType}/${editingId}`:`/api/${currentType}`;
  const res    = await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  if (!res.ok) { toast('Error saving','err'); return; }
  toast('Saved ✓','ok');
  closeModal();
  loadEntries();
}

async function deleteEntry(id) {
  if (!confirm(`Delete "${id}"? This cannot be undone.`)) return;
  await fetch(`/api/${currentType}/${id}`,{method:'DELETE'});
  toast('Deleted','ok');
  loadEntries();
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, type='ok') {
  const el = document.createElement('div');
  el.className = `toast ${type}`; el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(()=>el.remove(), 3000);
}
</script>
</body>
</html>"""

if __name__ == "__main__":
    print("\n  Portfolio Admin Dashboard")
    print("  Open → http://localhost:8888\n")
    uvicorn.run(app, host="127.0.0.1", port=8888, log_level="warning")
