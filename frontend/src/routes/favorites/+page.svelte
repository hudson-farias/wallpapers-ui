<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchFavorites, type FavoriteSlug } from '$lib/api';

  let slugs: FavoriteSlug[] = [];
  let total = 0;
  let loading = true;
  let error = '';

  async function loadFavorites() {
    loading = true;
    error = '';
    try {
      const data = await fetchFavorites();
      slugs = data.slugs;
      total = data.count;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loading = false;
    }
  }

  onMount(loadFavorites);
</script>

<svelte:head>
  <title>Favoritos · wallpaper-ui</title>
</svelte:head>

<div class="panel-toolbar">
  <div>
    <h2>Favoritos</h2>
    <p class="meta">{total} imagens em {slugs.length} fontes</p>
  </div>
</div>

{#if error}
  <p class="error">{error}</p>
{/if}

{#if loading}
  <p class="status">Carregando favoritos…</p>
{:else if slugs.length === 0}
  <p class="status">Nenhum favorito ainda. Use ☆ em uma fonte.</p>
{:else}
  <div class="slug-grid">
    {#each slugs as item (item.name)}
      <a class="slug-link" href={`/favorites/${item.name}`}>
        <span class="name">{item.name}</span>
        <span class="count">{item.image_count} imgs</span>
      </a>
    {/each}
  </div>
{/if}

<style>
  .panel-toolbar h2 {
    margin: 0;
    font-size: 1rem;
    color: #e8eaed;
  }

  .meta {
    margin: 0.2rem 0 0;
    color: #9aa3b2;
    font-size: 0.85rem;
  }

  .panel-toolbar {
    padding: 0.85rem 1rem 0;
  }

  .slug-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
    padding: 0.75rem 1rem 1rem;
  }

  .slug-link {
    text-decoration: none;
    color: inherit;
    border: 1px solid #2a3140;
    border-radius: 8px;
    background: #151a24;
    padding: 0.85rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .slug-link:hover {
    border-color: #3d5afe;
    background: #1c2440;
  }

  .name {
    font-weight: 600;
  }

  .count {
    font-size: 0.8rem;
    color: #9aa3b2;
  }

  .status {
    padding: 0 1rem 1rem;
    color: #9aa3b2;
  }

  .error {
    padding: 0 1rem;
    color: #ff8a80;
  }
</style>
