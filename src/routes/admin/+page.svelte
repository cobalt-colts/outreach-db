<script lang="ts">
    import {onMount} from "svelte";
    import {clearAuthToken, getAuthToken, getPermissionLevel} from "$lib/auth.svelte";
    import { goto } from "$app/navigation";

    let authorized = $state(false);

    onMount(async () => {
        if (!getAuthToken()) {
            await goto("/login", {replaceState: true});
            return;
        }

        try {
            if (await getPermissionLevel() !== 0) {
                await goto("/", {replaceState: true});
                return;
            }

            authorized = true;
        } catch {
            clearAuthToken();
            await goto("/login", {replaceState: true});
        }
    });
</script>

{#if authorized}
    <main class="flex justify-center text-center">
        <h1>Welcome to admin!</h1>
    </main>
{/if}
