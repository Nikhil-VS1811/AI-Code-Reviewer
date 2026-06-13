import { apiClient } from "./client";
import type { LoginPayload, SignupPayload, TokenResponse, User } from "../types/api";

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/login/json", payload);
  return data;
}

export async function signup(payload: SignupPayload): Promise<User> {
  const { data } = await apiClient.post<User>("/auth/signup", payload);
  return data;
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}
