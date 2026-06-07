import { writable } from 'svelte/store';
import { fetchFavorites, fetchSources, type Source } from '$lib/api';

export const sources = writable<Source[]>([]);
export const favoriteCount = writable(0);

export async function refreshSidebar() {
  const [sourceData, favoriteData] = await Promise.all([fetchSources(), fetchFavorites()]);
  sources.set(sourceData.sources);
  favoriteCount.set(favoriteData.count);
}

export function setSourceImageCount(slug: string, count: number) {
  sources.update((list) =>
    list.map((source) => (source.slug === slug ? { ...source, image_count: count } : source))
  );
}

export function setFavoriteCount(count: number) {
  favoriteCount.set(count);
}
