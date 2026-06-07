<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { sources } from '$lib/stores/sidebar';

  onMount(() => {
    const unsubscribe = sources.subscribe((items) => {
      if (items.length > 0) {
        goto(`/sources/${items[0].slug}`, { replaceState: true });
      }
    });
    return unsubscribe;
  });
</script>

<section class="empty">
  <h2>Bem-vindo</h2>
  <p>Adicione uma fonte Pinterest na barra lateral para começar.</p>
</section>

<style>
  .empty {
    padding: 2rem;
    color: #9aa3b2;
  }

  h2 {
    margin: 0 0 0.5rem;
    color: #e8eaed;
  }
</style>
