<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { setScreenAlias, type Screen } from '$lib/api';

  export let screens: Screen[] = [];
  export let value = 0;
  export let dbusAvailable = true;

  const dispatch = createEventDispatcher<{ change: Screen[] }>();

  let editingAlias = false;
  let aliasInput = '';
  let saving = false;
  let error = '';

  $: selected = screens.find((screen) => screen.id === value) ?? screens[0];

  function label(screen: Screen) {
    return screen.display_name || screen.alias || screen.name;
  }

  function openAliasEditor() {
    if (!selected) return;
    aliasInput = selected.alias ?? '';
    editingAlias = true;
    error = '';
  }

  function closeAliasEditor() {
    editingAlias = false;
    error = '';
  }

  async function handleSaveAlias() {
    if (!selected || saving) return;
    saving = true;
    error = '';
    try {
      const result = await setScreenAlias(selected.id, aliasInput);
      screens = screens.map((screen) =>
        screen.id === selected.id
          ? { ...screen, alias: result.alias, display_name: result.display_name }
          : screen
      );
      dispatch('change', screens);
      editingAlias = false;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      saving = false;
    }
  }
</script>

<div class="screen-panel">
  <label class="field">
    <span>Tela</span>
    <div class="select-row">
      <select bind:value>
        {#each screens as screen (screen.id)}
          <option value={screen.id}>{label(screen)}</option>
        {/each}
      </select>
      <button
        type="button"
        class="edit-btn"
        title="Editar alias"
        disabled={!selected}
        on:click={openAliasEditor}
      >
        ✎
      </button>
    </div>
  </label>

  {#if editingAlias && selected}
    <div class="alias-editor">
      <label class="field">
        <span>Alias</span>
        <input
          bind:value={aliasInput}
          placeholder={selected.name}
          disabled={saving}
          on:keydown={(event) => event.key === 'Enter' && handleSaveAlias()}
        />
      </label>
      <div class="alias-actions">
        <button type="button" disabled={saving} on:click={handleSaveAlias}>
          {saving ? '…' : 'Salvar'}
        </button>
        <button type="button" class="ghost" disabled={saving} on:click={closeAliasEditor}>
          Cancelar
        </button>
      </div>
    </div>
  {/if}

  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if !dbusAvailable}
    <p class="warn">D-Bus do Plasma indisponível no container — aplicar wallpaper pode falhar.</p>
  {/if}
</div>

<style>
  .screen-panel {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 220px;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  span {
    font-size: 0.85rem;
    color: #9aa3b2;
  }

  .select-row {
    display: flex;
    gap: 0.35rem;
    align-items: stretch;
  }

  .select-row select {
    flex: 1;
    min-width: 0;
  }

  .edit-btn {
    width: 2rem;
    padding: 0;
    flex-shrink: 0;
    font-size: 0.95rem;
    line-height: 1;
    color: #9aa3b2;
  }

  .edit-btn:hover:not(:disabled) {
    color: #e8eaed;
    border-color: #3d5afe;
  }

  .alias-editor {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0.65rem;
    border: 1px solid #2a3140;
    border-radius: 8px;
    background: #151a24;
  }

  .alias-actions {
    display: flex;
    gap: 0.35rem;
  }

  .ghost {
    background: transparent;
    border-color: #3d4451;
    color: #9aa3b2;
  }

  .warn {
    margin: 0;
    font-size: 0.82rem;
    color: #ffb74d;
  }

  .error {
    margin: 0;
    font-size: 0.82rem;
    color: #ff8a80;
  }
</style>
