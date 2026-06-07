<script lang="ts">
  import type { WallpaperImage } from '$lib/api';

  export let images: WallpaperImage[] = [];
  export let showFavoriteButton = true;
  export let onSelect: (image: WallpaperImage) => void = () => {};
  export let onToggleFavorite: (image: WallpaperImage) => void | Promise<void> = () => {};
</script>

<section class="grid-wrap">
  {#if images.length === 0}
    <p class="muted">Nenhuma imagem para exibir.</p>
  {:else}
    <div class="grid">
      {#each images as image (image.slug + image.name)}
        <div class="card">
          <button class="preview-btn" on:click={() => onSelect(image)}>
            <img src={image.url} alt={image.name} loading="lazy" />
          </button>
          <div class="card-footer">
            <span class="name" title="{image.slug}/{image.name}">{image.name}</span>
            {#if showFavoriteButton}
              <button
                class="fav-btn"
                class:active={image.favorite}
                title={image.favorite ? 'Remover favorito' : 'Favoritar em subpasta'}
                on:click={() => onToggleFavorite(image)}
              >
                {image.favorite ? '★' : '☆'}
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
  .grid-wrap {
    flex: 1;
    padding: 1rem;
    overflow: auto;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1rem;
  }

  .card {
    overflow: hidden;
    display: flex;
    flex-direction: column;
    border: 1px solid #2a3140;
    border-radius: 8px;
    background: #151a24;
  }

  .preview-btn {
    padding: 0;
    border: none;
    border-radius: 0;
    background: transparent;
  }

  img {
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    display: block;
    background: #0a0d12;
  }

  .card-footer {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.45rem 0.55rem;
  }

  .name {
    flex: 1;
    font-size: 0.78rem;
    color: #b8c0cc;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .fav-btn {
    width: 2rem;
    height: 2rem;
    padding: 0;
    flex-shrink: 0;
    font-size: 1rem;
    line-height: 1;
    color: #9aa3b2;
    border-color: #3d4451;
    background: transparent;
  }

  .fav-btn.active {
    color: #ffd54f;
    border-color: #ffd54f;
  }

  .fav-btn:hover {
    background: #252b3a;
  }

  .muted {
    color: #9aa3b2;
  }
</style>
