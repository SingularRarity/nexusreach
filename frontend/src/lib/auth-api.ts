import type { AuthResponse, RegisterRequest, User } from "@/types/auth";
import { api } from "./api";

export async function login(email: string, password: string): Promise<AuthResponse> {
  // fastapi-users expects OAuth2 form data for login
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  return api.post<AuthResponse>("/api/v1/auth/login", body);
}

export async function register(data: RegisterRequest): Promise<User> {
  return api.post<User>("/api/v1/auth/register", data);
}

export async function logout(): Promise<void> {
  return api.post<void>("/api/v1/auth/logout");
}

export async function getMe(): Promise<User> {
  return api.get<User>("/api/v1/auth/me");
}
