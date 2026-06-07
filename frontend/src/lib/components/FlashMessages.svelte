<script lang="ts">
  export let error = '';
  export let status = '';
</script>

{#if error}
  <p class="error">{error}</p>
{/if}
{#if status}
  <p class="status">{status}</p>
{/if}

<style>
  .status {
    padding: 0 1.25rem 1rem;
    color: #9aa3b2;
  }

  .error {
    padding: 0 1.25rem 1rem;
    color: #ff8a80;
  }
</style>
