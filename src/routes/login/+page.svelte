<script lang="ts">
    import {getAuthToken, signIn} from "$lib/auth.svelte";

    let username: string = $state("")
    let password: string = $state("")

    async function logIn(): Promise<void> {
        await signIn(username, password)
    }

</script>

{#if !getAuthToken}
    <form onsubmit={() => logIn()}>
        <input class="border-2 border-black" bind:value={username} placeholder="Username"/>
        <input class="border-2 border-black" bind:value={password} placeholder="Password"/>
        <button class="border-2 boarder-black" type="submit">Login</button>
    </form>
{:else}
    <h1 class="text-2xl font-extrabold">logged in!</h1>
    <p>auth code: {getAuthToken}</p>
{/if}