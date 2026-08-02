import type { APIContext } from 'astro';
import galleryData from '../../public/gallery-index.json';

export async function GET(context: APIContext) {
  const siteUrl = (context.site ?? 'https://gli4chskldfup3245mafdafksjdfjdfsdfsdfsrdcszd.online')
    .toString()
    .replace(/\/$/, '');

  const images = galleryData as { src: string; alt: string; caption?: string }[];

  const imageEntries = images
    .map(
      (img) => `    <image:image>
      <image:loc>${siteUrl}${img.src}</image:loc>
      <image:title>${img.alt.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</image:title>
      <image:caption>${(img.caption ?? img.alt).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/🏆/g, '').replace(/🥈/g, '').trim()}</image:caption>
    </image:image>`
    )
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
>
  <url>
    <loc>${siteUrl}/gallery/</loc>
${imageEntries}
  </url>
</urlset>`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
}
