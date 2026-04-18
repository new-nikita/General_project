import { ref } from "vue";
import axios from "../api/client"; // твой axios/fetch клиент

interface InitialRegisterResponse {
  message: string;
}

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  birth_date?: string;
  gender?: string;
  phone_number?: string;
  country?: string;
  city?: string;
  street?: string;
  bio?: string;
}

interface RegisterResponse {
  message: string;
}

export function useRegister() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const success = ref<string | null>(null);

  async function initialRegister(email: string) {
    loading.value = true;
    error.value = null;
    success.value = null;

    try {
      const res = await axios.post<InitialRegisterResponse>("/initial-register", { email });
      success.value = res.data.message;
    } catch (e: any) {
      error.value = e.response?.data?.detail || "Ошибка при отправке email";
    } finally {
      loading.value = false;
    }
  }

  async function registerUser(formData: RegisterRequest, avatarFile?: File) {
    loading.value = true;
    error.value = null;
    success.value = null;

    try {
      const fd = new FormData();
      for (const key in formData) {
        if ((formData as any)[key] != null) {
          fd.append(key, (formData as any)[key]);
        }
      }
      if (avatarFile) {
        fd.append("avatar", avatarFile);
      }

      const res = await axios.post<RegisterResponse>("/register", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      success.value = res.data.message;
    } catch (e: any) {
      error.value = e.response?.data?.detail || "Ошибка при регистрации";
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    success,
    initialRegister,
    registerUser,
  };
}