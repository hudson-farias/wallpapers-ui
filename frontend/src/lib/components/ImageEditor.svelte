<script lang="ts">
  import type { WallpaperImage } from '$lib/api';

  export let image: WallpaperImage | null = null;
  export let screenId = 0;
  export let busy = false;
  export let onApply: () => void = () => {};
  export let onClose: () => void = () => {};

  let cropEnabled = false;
  let cropX = 0;
  let cropY = 0;
  let cropWidth = 1920;
  let cropHeight = 1080;
  let outputWidth = 1920;
  let outputHeight = 1080;
</script>

{#if image}
  <div class="overlay" role="dialog" aria-modal="true">
    <div class="panel">
      <header>
        <h3>{image.name}</h3>
        <button on:click={onClose}>Fechar</button>
      </header>

      <img src={image.url} alt={image.name} class="preview" />

      <section class="controls">
        <label>
          <input type="checkbox" bind:checked={cropEnabled} />
          Crop 16:9 antes de aplicar (MVP — envia crop completo por enquanto)
        </label>

        {#if cropEnabled}
          <div class="crop-fields">
            <label>X <input type="number" bind:value={cropX} min="0" /></label>
            <label>Y <input type="number" bind:value={cropY} min="0" /></label>
            <label>Largura <input type="number" bind:value={cropWidth} min="1" /></label>
            <label>Altura <input type="number" bind:value={cropHeight} min="1" /></label>
            <label>Saída W <input type="number" bind:value={outputWidth} min="1" /></label>
            <label>Saída H <input type="number" bind:value={outputHeight} min="1" /></label>
          </div>
        {/if}

        <button class="primary" disabled={busy} on:click={onApply}>
          {busy ? 'Aplicando…' : `Aplicar na tela ${screenId}`}
        </button>
      </section>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.72);
    display: grid;
    place-items: center;
    padding: 1rem;
    z-index: 20;
  }

  .panel {
    width: min(960px, 100%);
    max-height: 92vh;
    overflow: auto;
    background: #151a24;
    border: 1px solid #2a3140;
    border-radius: 12px;
    padding: 1rem;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  h3 {
    margin: 0;
    font-size: 1rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .preview {
    width: 100%;
    margin-top: 0.75rem;
    border-radius: 8px;
    background: #0a0d12;
  }

  .controls {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .crop-fields {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.5rem;
  }

  .crop-fields label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.82rem;
    color: #9aa3b2;
  }
</style>
