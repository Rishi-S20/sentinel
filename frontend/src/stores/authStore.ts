import { create } from "zustand";
import api from "@/api/client";

interface User {
  id: string;
  email: string;
  name: string;
  plan_tier: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;

  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User, token: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await api.post<{ user: User; access_token: string }>(
        "/auth/login",
        { email, password }
      );
      api.setToken(response.access_token);
      set({
        user: response.user,
        token: response.access_token,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    api.setToken(null);
    set({ user: null, token: null });
  },

  setUser: (user: User, token: string) => {
    api.setToken(token);
    set({ user, token });
  },
}));
