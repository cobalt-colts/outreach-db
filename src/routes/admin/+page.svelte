<script lang="ts">
    import {onMount} from "svelte";
    import {clearAuthToken, getAuthToken, getPermissionLevel} from "$lib/auth.svelte";
    import { goto } from "$app/navigation";
    import Eventcreatedialog from "$lib/components/blocks/eventcreatedialog.svelte";
    import Button from "$lib/components/ui/button.svelte";
    import {toast} from "svelte-sonner";

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
    <div class="m-3 flex w-auto flex-col items-start gap-3">
        <Eventcreatedialog />
        <Button onclick={() => toast("test!")}>Test toast</Button>
    </div>
{/if}
