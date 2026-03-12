import { create } from "zustand";
import type { User } from "@/types/auth";
import * as authApi from "@/lib/auth-api";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  login: (email: string, password: string) => Promise<void>;
  register: (data: Parameters<typeof authApi.register>[0]) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  reset: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("access_token"),
  isLoading: false,
  isAuthenticated: false,

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login(email, password);
      localStorage.setItem("access_token", response.access_token);
      set({ token: response.access_token });
      await get().loadUser();
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (data) => {
    set({ isLoading: true });
    try {
      await authApi.register(data);
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } finally {
      localStorage.removeItem("access_token");
      set({ user: null, token: null, isAuthenticated: false });
    }
  },

  loadUser: async () => {
    const token = get().token ?? localStorage.getItem("access_token");
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }
    set({ isLoading: true });
    try {
      const user = await authApi.getMe();
      set({ user, isAuthenticated: true });
    } catch {
      localStorage.removeItem("access_token");
      set({ user: null, token: null, isAuthenticated: false });
    } finally {
      set({ isLoading: false });
    }
  },

  reset: () => {
    localStorage.removeItem("access_token");
    set({ user: null, token: null, isAuthenticated: false, isLoading: false });
  },
}));
