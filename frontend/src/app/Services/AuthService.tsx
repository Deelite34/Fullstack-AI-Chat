import api from "./api";

export type AccessTokenResponse = { token: string; token_type: string };

export type UserProfile = {
  id: number;
  username: string;
  email: string;
};

export const loginAPI = (username: string, password: string) =>
  api.post<AccessTokenResponse>("/auth/login", { username, password });

export const getCurrentUserAPI = () => api.get<UserProfile>("/auth/me");

export const refreshAPI = (token?: string) =>
  api.post<AccessTokenResponse>(
    "/auth/tokens/refresh",
    token ? { token } : undefined,
  );

export const logoutAPI = (token: string) =>
  api.post<void>("/auth/logout", { token });