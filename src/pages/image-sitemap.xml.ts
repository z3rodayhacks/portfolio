import type { APIContext } from 'astro';
import { getCollection } from 'astro:content';
import galleryData from '../../public/gallery-index.json';

function esc(s: string) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/[^\x09\x0A\x0D\x20-퟿-�]/g, ''); // strip emoji & invalid XML chars
}

function imgTag(loc: string, title: string, caption: string) {
  return `    <image:image>
      <image:loc>${esc(loc)}</image:loc>
      <image:title>${esc(title)}</image:title>
      <image:caption>${esc(caption)}</image:caption>
    </image:image>`;
}

function urlBlock(pageUrl: string, images: string[]) {
  if (!images.length) return '';
  return `  <url>\n    <loc>${esc(pageUrl)}</loc>\n${images.join('\n')}\n  </url>`;
}

export async function GET(context: APIContext) {
  const siteUrl = (context.site ?? 'https://gli4chskldfup3245mafdafksjdfjdfsdfsdfsrdcszd.online')
    .toString()
    .replace(/\/$/, '');

  const [talks, competitions, projects, blog] = await Promise.all([
    getCollection('talks'),
    getCollection('competitions'),
    getCollection('projects'),
    getCollection('blog', ({ data }) => !data.draft),
  ]);

  const blocks: string[] = [];

  // ── Profile photo — home & about ─────────────────────────────────────────
  const profileTag = imgTag(
    `${siteUrl}/profile/photo.jpg`,
    'Jashwanth Raghav R K',
    'Jashwanth Raghav R K — Cybersecurity Researcher and Security Consultant, Coimbatore, India',
  );
  blocks.push(urlBlock(`${siteUrl}/`,      [profileTag]));
  blocks.push(urlBlock(`${siteUrl}/about`, [profileTag]));

  // ── Talks ─────────────────────────────────────────────────────────────────
  const talkImgs: string[] = [];
  for (const talk of talks) {
    const seen = new Set<string>();
    const add = (src: string) => {
      if (!src || seen.has(src)) return;
      seen.add(src);
      const loc = `${siteUrl}${src.startsWith('/') ? src : '/' + src}`;
      talkImgs.push(imgTag(
        loc,
        `${talk.data.title} — ${talk.data.event}`,
        `Jashwanth Raghav R K presenting at ${talk.data.event} — ${talk.data.title}${talk.data.location ? ', ' + talk.data.location : ''}`,
      ));
    };
    if (talk.data.thumbnail) add(talk.data.thumbnail);
    (talk.data.images ?? []).forEach(add);
  }
  blocks.push(urlBlock(`${siteUrl}/talks`, talkImgs));

  // ── Competitions ──────────────────────────────────────────────────────────
  const compImgs: string[] = [];
  for (const comp of competitions) {
    const seen = new Set<string>();
    const result = comp.data.result ? ` (${comp.data.result})` : '';
    const add = (src: string) => {
      if (!src || seen.has(src)) return;
      seen.add(src);
      const loc = `${siteUrl}${src.startsWith('/') ? src : '/' + src}`;
      compImgs.push(imgTag(
        loc,
        `${comp.data.title}${result}`,
        `Jashwanth Raghav R K at ${comp.data.event}${result} — ${comp.data.title}`,
      ));
    };
    if (comp.data.thumbnail) add(comp.data.thumbnail);
    (comp.data.images ?? []).forEach(add);
  }
  blocks.push(urlBlock(`${siteUrl}/competitions`, compImgs));

  // ── Projects ──────────────────────────────────────────────────────────────
  const projImgs: string[] = [];
  for (const p of projects) {
    if (!p.data.thumbnail) continue;
    const loc = `${siteUrl}${p.data.thumbnail.startsWith('/') ? p.data.thumbnail : '/' + p.data.thumbnail}`;
    projImgs.push(imgTag(loc, p.data.title, `${p.data.title} — cybersecurity project by Jashwanth Raghav R K`));
  }
  blocks.push(urlBlock(`${siteUrl}/projects`, projImgs));

  // ── Blog posts ────────────────────────────────────────────────────────────
  for (const post of blog) {
    if (!post.data.thumbnail) continue;
    const loc = `${siteUrl}${post.data.thumbnail.startsWith('/') ? post.data.thumbnail : '/' + post.data.thumbnail}`;
    blocks.push(urlBlock(
      `${siteUrl}/blog/${post.id}`,
      [imgTag(loc, post.data.title, `${post.data.title} — security article by Jashwanth Raghav R K`)],
    ));
  }

  // ── Gallery (existing behaviour — all gallery images linked to /gallery/) ─
  const gallery = galleryData as { src: string; alt: string; caption?: string }[];
  const galleryImgs = gallery.map(img =>
    imgTag(
      `${siteUrl}${img.src}`,
      img.alt,
      (img.caption ?? img.alt).replace(/[^\x20-\x7E -￿]/g, '').trim(),
    )
  );
  blocks.push(urlBlock(`${siteUrl}/gallery/`, galleryImgs));

  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ...blocks.filter(Boolean),
    '</urlset>',
  ].join('\n');

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
}
