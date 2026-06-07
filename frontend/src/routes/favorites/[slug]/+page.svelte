<script lang="ts">
  import { page } from '$app/stores';
  import ImageGrid from '$lib/components/ImageGrid.svelte';
  import ImageEditor from '$lib/components/ImageEditor.svelte';
  import { getAppContext } from '$lib/context';
  import {
    applyWallpaper,
    fetchFavoriteSlugImages,
    removeFavorite,
    type WallpaperImage
  } from '$lib/api';
  import { refreshSidebar } from '$lib/stores/sidebar';

  const app = getAppContext();

  let images: WallpaperImage[] = [];
  let selectedImage: WallpaperImage | null = null;
  let loading = true;
  let busy = false;
  let error = '';
  let status = '';

  $: slug = $page.params.slug;

  let loadedSlug = '';
  $: if (slug && slug !== loadedSlug) {
    loadedSlug = slug;
    void loadFavorites();
  }

  async function loadFavorites() {
    loading = true;
    error = '';
    try {
      const data = await fetchFavoriteSlugImages(slug);
      images = data.images;
    } catch (err) {
      images = [];
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loading = false;
    }
  }

  async function handleRemove(image: WallpaperImage) {
    error = '';
    status = '';
    try {
      await removeFavorite(image.slug, image.filename ?? image.name);
      status = 'Removido dos favoritos';
      await loadFavorites();
      await refreshSidebar();
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    }
  }

  async function applySelected() {
    if (!selectedImage) return;
    busy = true;
    error = '';
    status = '';
    try {
      await applyWallpaper(
        app.getScreenId(),
        selectedImage.slug,
        selectedImage.filename ?? selectedImage.name,
        { fromFavorites: true }
      );
      status = `Wallpaper aplicado na tela ${app.getScreenId()}`;
      selectedImage = null;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      busy = false;
    }
  }
</script>

<svelte:head>
  <title>{slug} · favoritos</title>
</svelte:head>

<div class="panel-toolbar">
  <div>
    <h2>{slug}</h2>
    <a class="back" href="/favorites">← todas as fontes</a>
  </div>
</div>

{#if error}
  <p class="error">{error}</p>
{/if}
{#if status}
  <p class="status">{status}</p>
{/if}

{#if loading}
  <p class="status content-status">Carregando favoritos…</p>
{:else}
  <ImageGrid
    {images}
    showFavoriteButton
    onSelect={(image) => (selectedImage = image)}
    onToggleFavorite={handleRemove}
  />
{/if}

<ImageEditor
  image={selectedImage}
  screenId={app.getScreenId()}
  {busy}
  onApply={applySelected}
  onClose={() => (selectedImage = null)}
/>

<style>
  .panel-toolbar {
    padding: 0.85rem 1rem 0;
  }

  h2 {
    margin: 0;
    font-size: 1rem;
    color: #e8eaed;
  }

  .back {
    display: inline-block;
    margin-top: 0.25rem;
    color: #9aa3b2;
    font-size: 0.85rem;
    text-decoration: none;
  }

  .back:hover {
    color: #e8eaed;
  }

  .status {
    padding: 0 1rem;
    color: #9aa3b2;
  }

  .error {
    padding: 0 1rem;
    color: #ff8a80;
  }

  .content-status {
    padding: 1rem;
  }
</style>
