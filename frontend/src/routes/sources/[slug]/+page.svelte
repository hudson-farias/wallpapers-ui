<script lang="ts">
  import { page } from '$app/stores';
  import ImageGrid from '$lib/components/ImageGrid.svelte';
  import ImageEditor from '$lib/components/ImageEditor.svelte';
  import { getAppContext } from '$lib/context';
  import {
    addFavorite,
    applyWallpaper,
    fetchFavorites,
    fetchImages,
    refreshSource,
    type WallpaperImage
  } from '$lib/api';
  import { setFavoriteCount, setSourceImageCount } from '$lib/stores/sidebar';

  const app = getAppContext();

  let images: WallpaperImage[] = [];
  let selectedImage: WallpaperImage | null = null;
  let loadingImages = true;
  let busy = false;
  let savingFavorite = false;
  let error = '';
  let status = '';

  $: slug = $page.params.slug;

  let loadedSlug = '';
  $: if (slug && slug !== loadedSlug) {
    loadedSlug = slug;
    void loadBoard(false);
  }

  async function loadBoard(refresh = false) {
    loadingImages = true;
    error = '';
    try {
      const [imageData, favoriteData] = await Promise.all([
        fetchImages(slug, refresh),
        fetchFavorites()
      ]);
      images = imageData.images;
      setSourceImageCount(slug, imageData.images.length);
      setFavoriteCount(favoriteData.count);
    } catch (err) {
      images = [];
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loadingImages = false;
    }
  }

  async function handleRefresh() {
    loadingImages = true;
    error = '';
    status = '';
    try {
      await refreshSource(slug);
      status = `Fonte "${slug}" atualizada`;
      await loadBoard(false);
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
      loadingImages = false;
    }
  }

  async function handleToggleFavorite(image: WallpaperImage) {
    if (image.favorite) {
      status = 'Já favoritado — abra /favorites para gerenciar';
      return;
    }

    savingFavorite = true;
    error = '';
    status = '';
    try {
      await addFavorite(image.slug, image.name);
      status = `Salvo em favorites/${image.slug}/`;
      await loadBoard(false);
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      savingFavorite = false;
    }
  }

  async function applySelected() {
    if (!selectedImage) return;
    busy = true;
    error = '';
    status = '';
    try {
      await applyWallpaper(app.getScreenId(), selectedImage.slug, selectedImage.name);
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
  <title>{slug} · wallpaper-ui</title>
</svelte:head>

<div class="panel-toolbar">
  <h2>{slug}</h2>
  <button disabled={loadingImages || savingFavorite} on:click={handleRefresh}>
    {loadingImages ? 'Atualizando…' : 'Atualizar'}
  </button>
</div>

{#if error}
  <p class="error">{error}</p>
{/if}
{#if status}
  <p class="status">{status}</p>
{/if}

{#if loadingImages}
  <p class="status content-status">Baixando cache da fonte…</p>
{:else}
  <ImageGrid
    {images}
    showFavoriteButton
    onSelect={(image) => (selectedImage = image)}
    onToggleFavorite={handleToggleFavorite}
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
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.85rem 1rem 0;
  }

  .panel-toolbar h2 {
    margin: 0;
    font-size: 1rem;
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
    flex: 1;
    padding: 1rem;
  }
</style>
