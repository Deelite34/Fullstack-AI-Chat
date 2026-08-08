import axios, { type AxiosError } from "axios";

const api = axios.create({
  adapter: "fetch",
  baseURL: "/",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.response.use(
  async (response) => {
    // access invalid (401)=> refresh it
    // refresh invalid => redirect to login page
    if(response.status === 401) {
      const res = await api.post("/auth/refresh")
    }
  },
  (error: AxiosError<{ detail?: string }>) => {
    const message =
      error.response?.data?.detail || error.message || "Request failed";

    return Promise.reject(new Error(message));
  },
);

export default api;
