export type Source = {
  id: number;
  slug: string;
  source: string;
  image_count: number;
};

export type FavoriteSlug = {
  name: string;
  image_count: number;
};

export type WallpaperImage = {
  name: string;
  slug: string;
  size_bytes: number;
  url: string;
  favorite?: boolean;
  filename?: string;
};

export type Screen = {
  id: number;
  name: string;
  alias?: string;
  display_name?: string;
  available?: boolean;
  note?: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      detail = (await res.text()) || detail;
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return res.json();
}

export function fetchSources() {
  return request<{ sources: Source[] }>('/api/sources');
}

export function createSource(source: string) {
  return request<Source>('/api/sources', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source })
  });
}

export function deleteSource(sourceId: number) {
  return request<{ ok: boolean; id: number; slug: string }>(`/api/sources/${sourceId}`, {
    method: 'DELETE'
  });
}

export function fetchImages(slug: string, refresh = false) {
  const query = refresh ? '?refresh=true' : '';
  return request<{ slug: string; images: WallpaperImage[] }>(`/api/sources/${slug}/images${query}`);
}

export function refreshSource(slug: string) {
  return request<{ slug: string; images: WallpaperImage[] }>(`/api/sources/${slug}/refresh`, {
    method: 'POST'
  });
}

export function fetchFavorites() {
  return request<{ slugs: FavoriteSlug[]; count: number }>('/api/favorites');
}

export function fetchFavoriteSlugImages(slug: string) {
  return request<{ slug: string; images: WallpaperImage[] }>(
    `/api/favorites/${encodeURIComponent(slug)}/images`
  );
}

export function addFavorite(slug: string, filename: string) {
  return request<{ ok: boolean; filename: string }>('/api/favorites', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ slug, filename })
  });
}

export function removeFavorite(slug: string, filename: string) {
  return request<{ ok: boolean }>(
    `/api/favorites/${encodeURIComponent(slug)}/${encodeURIComponent(filename)}`,
    { method: 'DELETE' }
  );
}

export function fetchScreens() {
  return request<{ screens: Screen[]; dbus_available: boolean }>('/api/screens');
}

export function setScreenAlias(screenId: number, alias: string) {
  return request<{ ok: boolean; screen_id: number; alias: string; display_name: string }>(
    `/api/screens/${screenId}/alias`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alias })
    }
  );
}

export function applyWallpaper(
  screenId: number,
  slug: string,
  filename: string,
  options: { fromFavorites?: boolean } = {}
) {
  return request<{ ok: boolean }>('/api/apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      screen_id: screenId,
      slug,
      filename,
      from_favorites: options.fromFavorites ?? false
    })
  });
}

export function applyCroppedWallpaper(form: FormData) {
  return request<{ ok: boolean }>('/api/apply/crop', {
    method: 'POST',
    body: form
  });
}
