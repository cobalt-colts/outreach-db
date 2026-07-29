let auth_token = $state()
let error_str = $state()

export function getAuthToken() {
    return auth_token
}

export async function signIn(email: string, password: string): Promise<void> {
    try {
        const response = await fetch(
            "/api/auth/login",
            {
                method: "POST",
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        )

        const data = await response.json()

        auth_token = data.auth_token;
    } catch (e) {
        const error = e as Error;
        console.error(error)
        error_str = error.message
    }
}

export async function apiRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = new Headers(options.headers);
    if (auth_token != '') {
        headers.set("Authorization", `Bearer ${auth_token}`);
    }

    return await fetch(url, {
        ...options,
        headers,
    });
}