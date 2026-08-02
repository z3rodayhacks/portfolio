import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const siteUrl = (context.site ?? 'https://yoursite.com').toString().replace(/\/$/, '');
  const body = [
    'User-agent: *',
    'Allow: /',
    '',
    `Sitemap: ${siteUrl}/sitemap-index.xml`,
    `Sitemap: ${siteUrl}/image-sitemap.xml`,
  ].join('\n');

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
