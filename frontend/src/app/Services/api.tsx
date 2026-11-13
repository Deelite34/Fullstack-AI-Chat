import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios";

const api = axios.create({
  adapter: "fetch",
  baseURL: "/",
  timeout: 10000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

type TokenResponse = { token: string; token_type: string };

let accessToken: string | null = null;
let refreshRequest: Promise<string> | null = null;
let onSessionExpired: (() => void) | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

function requestAccessTokenRefresh() {
  if (!accessToken) {
    return Promise.reject(new Error("No access token is available to refresh"));
  }

  refreshRequest ??= api
    .post<TokenResponse>("/auth/tokens/refresh", { token: accessToken })
    .then(({ data }) => {
      setAccessToken(data.token);
      return data.token;
    })
    .finally(() => {
      refreshRequest = null;
    });

  return refreshRequest;
}

export async function refreshAccessToken() {
  try {
    return await requestAccessTokenRefresh();
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      setAccessToken(null);
      onSessionExpired?.();
    }
    throw error;
  }
}

export function setSessionExpiredHandler(handler: () => void) {
  onSessionExpired = handler;
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  } else {
    delete config.headers.Authorization;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<{ detail?: string }>) => {
    const request = error.config;
    if (
      error.response?.status === 401 &&
      request &&
      accessToken &&
      !request._retry &&
      !request.url?.includes("/auth/tokens/refresh")
    ) {
      request._retry = true;
      try {
        await refreshAccessToken();
        if (request.url?.includes("/auth/logout")) {
          request.data = { token: accessToken };
        }
        return api(request);
      } catch (refreshError) {
        return Promise.reject(refreshError);
      }
    }

    if (error.response?.data?.detail) {
      error.message = error.response.data.detail;
    }
    return Promise.reject(error);
  },
);

export default api;
