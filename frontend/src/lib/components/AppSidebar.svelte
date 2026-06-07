<script lang="ts">
  import { page } from '$app/stores';
  import { favoriteCount, sources } from '$lib/stores/sidebar';

  export let mutating = false;
  export let onAdd: (source: string) => void | Promise<void> = () => {};
  export let onRemove: (id: number) => void | Promise<void> = () => {};

  let newSource = '';

  $: pathname = $page.url.pathname;
  $: favoritesActive = pathname === '/favorites' || pathname.startsWith('/favorites/');

  function sourceHref(slug: string) {
    return `/sources/${slug}`;
  }

  function isSourceActive(slug: string) {
    return pathname === `/sources/${slug}`;
  }

  async function handleAdd() {
    const value = newSource.trim();
    if (!value || mutating) return;
    await onAdd(value);
    newSource = '';
  }
</script>

<aside class="sidebar">
  <h2>Fontes</h2>

  <form class="add-form" on:submit|preventDefault={handleAdd}>
    <input
      type="text"
      bind:value={newSource}
      placeholder="https://www.pinterest.com/usuario/board/"
      disabled={mutating}
    />
    <button type="submit" class="primary" disabled={mutating || !newSource.trim()}>
      {mutating ? '…' : 'Adicionar'}
    </button>
  </form>

  <nav class="nav-section">
    <a class="nav-link" class:active={favoritesActive} href="/favorites">
      <span class="slug">Favoritos</span>
      <span class="meta">{$favoriteCount} imgs</span>
    </a>
  </nav>

  {#if $sources.length === 0}
    <p class="muted">Nenhuma fonte cadastrada</p>
  {:else}
    <ul>
      {#each $sources as source (source.id)}
        <li>
          <a class="nav-link source-link" class:active={isSourceActive(source.slug)} href={sourceHref(source.slug)}>
            <span class="slug">{source.slug}</span>
            <span class="meta">{source.image_count} imgs</span>
          </a>
          <button
            class="remove-btn"
            title="Remover fonte"
            disabled={mutating}
            on:click={() => onRemove(source.id)}
          >
            ×
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</aside>

<style>
  .sidebar {
    width: 280px;
    border-right: 1px solid #2a3140;
    padding: 1rem;
    background: #121722;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  h2 {
    margin: 0;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #9aa3b2;
  }

  .add-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .add-form input {
    width: 100%;
    font-size: 0.85rem;
  }

  .nav-section {
    margin-bottom: 0.25rem;
  }

  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow: auto;
  }

  li {
    display: flex;
    gap: 0.35rem;
    align-items: stretch;
  }

  .nav-link {
    flex: 1;
    text-decoration: none;
    color: inherit;
    border: 1px solid #3d4451;
    background: #1a1f2b;
    border-radius: 8px;
    padding: 0.5rem 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .nav-link:hover {
    background: #252b3a;
  }

  .nav-link.active {
    border-color: #3d5afe;
    background: #1c2440;
  }

  .remove-btn {
    width: 2rem;
    padding: 0;
    flex-shrink: 0;
    font-size: 1.1rem;
    line-height: 1;
    color: #ff8a80;
    border-color: #3d4451;
  }

  .slug {
    font-weight: 600;
  }

  .meta {
    font-size: 0.8rem;
    color: #9aa3b2;
  }

  .muted {
    color: #9aa3b2;
    font-size: 0.9rem;
    margin: 0;
  }
</style>
