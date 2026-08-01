# Cybersecurity Portfolio — Static Site

A fully static, high-performance cybersecurity portfolio built with **Astro 7**, **Tailwind CSS v4**,
and deployed on **Cloudflare Pages**.  
No backend. No database. No CMS. Pure markdown → static HTML.

---

## Quick Start

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # builds to ./dist/
npm run preview    # preview the build locally
```

---

## Deployment (Cloudflare Pages)

### First-time setup

1. Push this repository to GitHub.
2. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Workers & Pages** → **Create**.
3. Select **Connect to Git** → choose your repository.
4. Use these build settings:

| Setting | Value |
|---------|-------|
| Framework preset | Astro |
| Build command | `npm run build` |
| Output directory | `dist` |
| Node.js version | `22` |

5. Click **Save and Deploy**.

### Automatic deploys

Every `git push` to your default branch triggers a Cloudflare Pages rebuild automatically.
No configuration needed — just push your changes.

### Custom domain

In Cloudflare Pages → your project → **Custom domains** → add your domain.
Cloudflare handles SSL automatically.

### Environment variables (optional)

If you ever need env vars (e.g., analytics keys), set them in:
Cloudflare Dashboard → Pages → your project → **Settings** → **Environment variables**.

---

## Content Management Workflow

You manage content entirely through GitHub — no code required for routine updates.

### Adding a new project

1. Go to your GitHub repo → `src/content/projects/`
2. Click **Add file** → **Create new file**
3. Name it `your-project-name.md`
4. Paste this template and fill it in:

```markdown
---
title: "My Project Name"
description: "One sentence describing what it does."
date: "2025-01-15"
tags: ["Penetration Testing", "Python", "Network Security"]
thumbnail: "/images/projects/my-project.png"
featured: false
github: "https://github.com/you/repo"
demo: "https://demo.example.com"
status: "completed"          # completed | in-progress | archived
techStack: ["Python", "Scapy", "Docker"]
category: "Security Tooling"
---

Write your project description here using Markdown.

## Overview

...

## Technical Details

...
```

5. Commit → Cloudflare rebuilds → project appears at `/projects/your-project-name`

### Adding a blog post

1. `src/content/blog/` → **Create new file** → `my-post-title.md`
2. Template:

```markdown
---
title: "Blog Post Title"
description: "A short description shown in previews and meta tags."
date: "2025-01-20"
tags: ["Web Security", "CTF", "Research"]
thumbnail: "/images/blog/my-post.png"
featured: false
draft: false                  # set true to hide from the site
---

Blog content in Markdown here.

## Code blocks

```python
print("syntax highlighted automatically")
```

## Tables, callouts, etc. all work.
```

3. Commit to publish. Set `draft: true` to save as a work-in-progress.

### Adding a talk

1. `src/content/talks/` → new `.md` file:

```markdown
---
title: "Talk Title"
description: "What the talk covered."
date: "2025-03-10"
event: "Conference Name"
location: "City, Country"
slides: "https://speakerdeck.com/you/talk-slug"
video: "https://youtube.com/watch?v=abc"
tags: ["Network Security", "Red Team"]
---
```

### Adding a certificate

1. `src/content/certificates/` → new `.md` file:

```markdown
---
title: "OSCP"
issuer: "Offensive Security"
date: "2025-02-01"
credentialId: "OS-123456"
credentialUrl: "https://credential.net/verify/example"
thumbnail: "/certificates/oscp-badge.png"
tags: ["Penetration Testing", "Offensive Security"]
---
```

2. Upload the badge image to `public/certificates/` using GitHub's file upload.

### Adding a timeline entry

```markdown
---
title: "Joined XYZ as Senior Engineer"
date: "2025-01-01"
description: "Brief description of what this milestone was."
type: "work"           # work | education | achievement | project | other
organization: "XYZ Corp"
location: "Remote"
tags: ["Career"]
---
```

---

## Uploading Images

### Via GitHub web UI

1. Navigate to the target folder (e.g., `public/images/projects/`)
2. Click **Add file** → **Upload files**
3. Drag-and-drop your image(s)
4. Commit directly to main

### Image paths

| Folder | Used for |
|--------|----------|
| `public/images/projects/` | Project thumbnails |
| `public/images/blog/` | Blog post thumbnails |
| `public/profile/` | Profile photo (`photo.jpg`) |
| `public/certificates/` | Certificate badge images |
| `public/logos/` | Company/event logos |
| `public/images/gallery/` | Gallery photos |

In frontmatter, reference them as:
```yaml
thumbnail: "/images/projects/my-image.jpg"
```

### Gallery

Add images to `public/images/gallery/`, then update `public/gallery-index.json`:

```json
[
  {
    "src": "/images/gallery/defcon-2025.jpg",
    "alt": "DEF CON 2025",
    "caption": "Presenting at DEF CON 33"
  },
  {
    "src": "/images/gallery/hackathon.jpg",
    "alt": "Hackathon team photo"
  }
]
```

---

## Personalisation

### Update your name and identity

Edit `src/components/home/Hero.astro`:
- Change "Your Name" in the `<h1>` tag
- Update the description paragraph
- Change the stats (projects, CVEs, posts, talks)

### Update the navigation header brand

Edit `src/components/layout/Header.astro` — change the `/sec~` text to your handle or initials.

### Update social links

Edit `src/components/layout/Footer.astro` → `social` array:

```js
const social = [
  { href: 'https://github.com/YOURHANDLE', ... },
  { href: 'https://linkedin.com/in/YOURPROFILE', ... },
];
```

### Update the site URL (for sitemap + RSS)

Edit `astro.config.mjs`:

```js
site: 'https://yourdomain.com',
```

Also set this in Cloudflare Pages environment variables as `SITE_URL` if you use a custom domain.

### Update About page content

Edit `src/pages/about.astro` — update:
- The `skills` object with your actual skills
- The profile section (name, role, description)
- CTAs link to your resume PDF at `public/resume.pdf`

---

## Project Structure

```text
cybersec-portfolio/
├── src/
│   ├── content/                  # All content — edit these files
│   │   ├── projects/             # .md files for projects
│   │   ├── blog/                 # .md or .mdx files for blog posts
│   │   ├── talks/                # .md files for talks
│   │   ├── certificates/         # .md files for certificates
│   │   ├── timeline/             # .md files for timeline entries
│   │   ├── experience/           # .md files for work experience
│   │   └── config.ts             # Content schemas (don't edit unless adding fields)
│   ├── components/
│   │   ├── home/                 # Hero, FeaturedProjects, LatestPosts
│   │   ├── layout/               # Header, Footer
│   │   └── ui/                   # Shared UI components
│   ├── layouts/
│   │   ├── BaseLayout.astro      # Root layout (SEO, header, footer)
│   │   ├── BlogLayout.astro      # Blog post layout
│   │   └── ProjectLayout.astro   # Project page layout
│   ├── pages/                    # URL routes
│   │   ├── index.astro           # Homepage
│   │   ├── about.astro
│   │   ├── projects/
│   │   ├── blog/
│   │   ├── talks.astro
│   │   ├── certificates.astro
│   │   ├── timeline.astro
│   │   ├── gallery.astro
│   │   ├── contact.astro
│   │   ├── search.astro
│   │   ├── 404.astro
│   │   ├── rss.xml.ts
│   │   └── robots.txt.ts
│   ├── styles/global.css         # Design system, CSS variables, Tailwind config
│   └── lib/utils.ts              # Utility functions
├── public/
│   ├── images/                   # Static images
│   ├── certificates/             # Certificate badge images
│   ├── profile/                  # Profile photo
│   ├── logos/                    # Company / event logos
│   ├── favicon.svg
│   ├── gallery-index.json        # Gallery image list
│   └── resume.pdf                # Your resume
├── astro.config.mjs
├── tsconfig.json
└── package.json
```

---

## Frontmatter Fields Reference

### Projects (`src/content/projects/`)

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Project name |
| `description` | Yes | One-line summary |
| `date` | Yes | `YYYY-MM-DD` |
| `tags` | No | Array of strings |
| `thumbnail` | No | Image path |
| `featured` | No | Show on homepage |
| `github` | No | GitHub URL |
| `demo` | No | Live demo URL |
| `status` | No | `completed` / `in-progress` / `archived` |
| `techStack` | No | Array of technologies |
| `category` | No | e.g., "Security Tooling" |

### Blog (`src/content/blog/`)

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Post title |
| `description` | Yes | Excerpt / meta description |
| `date` | Yes | `YYYY-MM-DD` |
| `tags` | No | Array |
| `thumbnail` | No | Hero image |
| `featured` | No | Highlight on homepage |
| `draft` | No | `true` = hidden from build |

### Certificates (`src/content/certificates/`)

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Cert name |
| `issuer` | Yes | Issuing organisation |
| `date` | Yes | Issued date |
| `credentialId` | No | Certificate number |
| `credentialUrl` | No | Verification URL |
| `thumbnail` | No | Badge image |
| `expiry` | No | Expiry date |

---

## How Cloudflare Pages Rebuilds Automatically

```
You edit a .md file on GitHub
         ↓
GitHub triggers a webhook to Cloudflare Pages
         ↓
Cloudflare clones the repo and runs: npm run build
         ↓
Astro reads all content files and generates static HTML
         ↓
Output is deployed to Cloudflare's edge network (300+ PoPs)
         ↓
Your site updates — usually within 60 seconds
```

No manual steps. No servers to manage.

---

## Performance

This site targets 100/100 on all Lighthouse metrics:
- **Static HTML** — no server rendering, instant response from CDN edge
- **Zero client JS** by default — animations use CSS only
- **Tailwind CSS v4** — only the CSS you use is included
- **Lazy image loading** — `loading="lazy"` on below-fold images
- **Shiki syntax highlighting** — done at build time, no runtime JS

---

## Adding New Features

### Add a new page

Create `src/pages/my-page.astro`:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout title="My Page" description="...">
  <div class="py-16 px-4 sm:px-6 max-w-4xl mx-auto">
    <h1 class="text-4xl font-bold text-zinc-100">My Page</h1>
  </div>
</BaseLayout>
```

Then add a link in `src/components/layout/Header.astro` → `navLinks` array.

### Add a new content collection field

Edit `src/content.config.ts` — add the field to the schema:

```ts
myNewField: z.string().optional(),
```

Then reference it in the page template as `entry.data.myNewField`.

---

## License

MIT — free to use and adapt for your own portfolio.
