import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  const sorted = posts.sort(
    (a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime()
  );

  return rss({
    title: 'z3roday | Jashwanth Raghav - Blog',
    description: 'Security research articles, CTF writeups, vulnerability disclosures, and tool guides.',
    site: context.site ?? 'https://yoursite.com',
    items: sorted.map((post) => ({
      title:       post.data.title,
      pubDate:     new Date(post.data.date),
      description: post.data.description,
      link:        `/blog/${post.id}/`,
      categories:  post.data.tags,
    })),
    customData: `<language>en-us</language>`,
  });
}
