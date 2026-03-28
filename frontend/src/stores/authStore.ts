import { useUser } from "@stackframe/stack";

import { stackClientApp } from "@/stack/client";

export function useAuthStore() {
  const user = useUser();

  const logout = async () => {
    await stackClientApp.signOut();
  };

  return {
    user,
    isAuthenticated: !!user,
    isLoading: user === undefined,
    logout,
  };
}
