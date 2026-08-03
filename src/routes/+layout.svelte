<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
    import { onMount } from "svelte";
    import { clearAuthToken, getAuthToken } from "$lib/auth.svelte";
    import Navbar from '$lib/components/blocks/navbar.svelte';
    import { Toaster } from 'svelte-sonner';

    let { children } = $props();

    async function checkToken(): Promise<void> {
        try {
            const token = getAuthToken();
            const response = await fetch("/api/auth/me", {
                method: "GET",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
            })

            if (!response.ok) {
                clearAuthToken();
            }
        } catch (e) {
            console.log(e);
        }
    }

    onMount(() => {
        if(getAuthToken()) {
            checkToken();
        }
    })
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<Toaster richColors/>
<Navbar />
{@render children()}
