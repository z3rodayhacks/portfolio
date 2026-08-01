/** Format a date string to human-readable form */
export function formatDate(date: string | Date, options?: Intl.DateTimeFormatOptions): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  });
}

/** Format date as compact string: Jan 2024 */
export function formatDateShort(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
}

/** Estimate reading time from raw markdown body */
export function readingTime(body: string): number {
  const words = body.split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.ceil(words / 200));
}

/** Sort collection entries by date descending */
export function sortByDate<T extends { data: { date: string } }>(entries: T[]): T[] {
  return [...entries].sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime());
}

/** Get unique tags from a list of entries */
export function allTags<T extends { data: { tags: string[] } }>(entries: T[]): string[] {
  return [...new Set(entries.flatMap((e) => e.data.tags))].sort();
}

/** Slugify a string */
export function slugify(str: string): string {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '');
}

/** Truncate text to a max length, adding ellipsis */
export function truncate(text: string, maxLength = 160): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 1) + '…';
}

/** Group entries by a key */
export function groupBy<T>(arr: T[], fn: (item: T) => string): Record<string, T[]> {
  return arr.reduce<Record<string, T[]>>((acc, item) => {
    const key = fn(item);
    (acc[key] ??= []).push(item);
    return acc;
  }, {});
}
