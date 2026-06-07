<script lang="ts">
  import '../app.css';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import AppSidebar from '$lib/components/AppSidebar.svelte';
  import ScreenSelect from '$lib/components/ScreenSelect.svelte';
  import FlashMessages from '$lib/components/FlashMessages.svelte';
  import { setAppContext } from '$lib/context';
  import { createSource, deleteSource, fetchScreens, type Screen } from '$lib/api';
  import { refreshSidebar, sources } from '$lib/stores/sidebar';

  let screens: Screen[] = [];
  let dbusAvailable = true;
  let screenId = 0;
  let loading = true;
  let mutatingSources = false;
  let error = '';
  let status = '';

  setAppContext({
    get screens() {
      return screens;
    },
    get dbusAvailable() {
      return dbusAvailable;
    },
    getScreenId: () => screenId,
    setScreenId: (value: number) => {
      screenId = value;
    }
  });

  async function handleAddSource(source: string) {
    mutatingSources = true;
    error = '';
    status = '';
    try {
      const created = await createSource(source);
      status = `Fonte "${created.slug}" adicionada`;
      await refreshSidebar();
      await goto(`/sources/${created.slug}`);
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      mutatingSources = false;
    }
  }

  async function handleRemoveSource(sourceId: number) {
    mutatingSources = true;
    error = '';
    status = '';
    try {
      const removed = await deleteSource(sourceId);
      status = `Fonte "${removed.slug}" removida`;
      await refreshSidebar();
      const remaining = $sources.filter((s) => s.id !== sourceId);
      if (remaining.length > 0) {
        await goto(`/sources/${remaining[0].slug}`);
      } else {
        await goto('/');
      }
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      mutatingSources = false;
    }
  }

  onMount(async () => {
    try {
      const [screenData] = await Promise.all([fetchScreens(), refreshSidebar()]);
      screens = screenData.screens;
      dbusAvailable = screenData.dbus_available;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loading = false;
    }
  });
</script>

<div class="app">
  <header class="topbar">
    <div>
      <h1>wallpaper-ui</h1>
      <p>Fontes · favoritos · telas</p>
    </div>
    <ScreenSelect
      {screens}
      bind:value={screenId}
      {dbusAvailable}
      on:change={(event) => (screens = event.detail)}
    />
  </header>

  {#if loading}
    <p class="status">Carregando…</p>
  {:else}
    <div class="content">
      <AppSidebar
        mutating={mutatingSources}
        onAdd={handleAddSource}
        onRemove={handleRemoveSource}
      />
      <main class="main-panel">
        <slot />
      </main>
    </div>
  {/if}

  <FlashMessages {error} {status} />
</div>

<style>
  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid #2a3140;
    background: #121722;
  }

  h1 {
    margin: 0;
    font-size: 1.25rem;
  }

  .topbar p {
    margin: 0.2rem 0 0;
    color: #9aa3b2;
    font-size: 0.9rem;
  }

  .content {
    display: flex;
    flex: 1;
    min-height: 0;
  }

  .main-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .status {
    padding: 1rem 1.25rem;
    color: #9aa3b2;
  }
</style>
