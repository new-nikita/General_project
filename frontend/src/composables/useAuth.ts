import { useRouter } from 'vue-router'
import { ref } from 'vue'
import axios from '@/api/client' // или свой путь

export function useAuth() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref<string | null>(null)

    const login = async (username: string, password: string) => {
        try {
            loading.value = true
            error.value = null

            const res = await axios.post('/login', {
                username,
                password,
            })

            // 👉 редирект после логина
            router.push(`/profile/${res.data.user_id}`)

        } catch (e: any) {
            error.value = e.response?.data?.detail || 'Login failed'
        } finally {
            loading.value = false
        }
    }

    return {
        login,
        loading,
        error,
    }
}