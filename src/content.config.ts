import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';

const projects = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.string(),
    tags: z.array(z.string()).default([]),
    thumbnail: z.string().optional(),
    featured: z.boolean().default(false),
    github: z.string().url().optional(),
    demo: z.string().url().optional(),
    status: z.enum(['completed', 'in-progress', 'archived']).default('completed'),
    techStack: z.array(z.string()).default([]),
    category: z.string().optional(),
  }),
});

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.string(),
    tags: z.array(z.string()).default([]),
    thumbnail: z.string().optional(),
    featured: z.boolean().default(false),
    draft: z.boolean().default(false),
    series: z.string().optional(),
  }),
});

const talks = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/talks' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.string(),
    event: z.string(),
    location: z.string().optional(),
    slides: z.string().url().optional(),
    video: z.string().url().optional(),
    linkedin: z.string().url().optional(),
    images: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
    thumbnail: z.string().optional(),
    featured: z.boolean().default(false),
  }),
});

const certificates = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/certificates' }),
  schema: z.object({
    title: z.string(),
    issuer: z.string(),
    date: z.string(),
    expiry: z.string().optional(),
    credentialId: z.string().optional(),
    credentialUrl: z.string().url().optional(),
    thumbnail: z.string().optional(),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
  }),
});

const timeline = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/timeline' }),
  schema: z.object({
    title: z.string(),
    date: z.string(),
    description: z.string(),
    type: z.enum(['work', 'education', 'achievement', 'project', 'other']).default('other'),
    organization: z.string().optional(),
    location: z.string().optional(),
    tags: z.array(z.string()).default([]),
  }),
});

const experience = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/experience' }),
  schema: z.object({
    title: z.string(),
    company: z.string(),
    location: z.string().optional(),
    startDate: z.string(),
    endDate: z.string().optional(),
    current: z.boolean().default(false),
    description: z.string(),
    tags: z.array(z.string()).default([]),
    logo: z.string().optional(),
    order: z.number().default(0),
  }),
});

const competitions = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/competitions' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.string(),
    event: z.string(),
    organizer: z.string().optional(),
    location: z.string().optional(),
    result: z.string().optional(),
    team: z.string().optional(),
    teamSize: z.number().optional(),
    project: z.string().optional(),
    github: z.string().url().optional(),
    linkedin: z.string().url().optional(),
    certificate: z.string().optional(),
    thumbnail: z.string().optional(),
    images: z.array(z.string()).default([]),
    tags: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
  }),
});

export const collections = { projects, blog, talks, certificates, timeline, experience, competitions };
