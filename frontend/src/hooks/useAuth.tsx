/**
 * Auth context — wraps the /api/auth/me query and exposes login,
 * register, and logout actions. Auth state lives here so any
 * component (ProtectedRoute, Topbar, Settings) can read it without
 * prop drilling.
 */
import React, { createContext, useContext } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getCurrentUser, loginUser, logoutUser, registerUser } from "../services/api";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string, confirmPassword: string) => Promise<User>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ["current-user"],
    queryFn: getCurrentUser,
    retry: false,
    // A 401 here just means "not logged in" — not a real error to surface.
    throwOnError: false,
  });

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) => loginUser({ email, password }),
    onSuccess: (loggedInUser) => queryClient.setQueryData(["current-user"], loggedInUser),
  });

  const registerMutation = useMutation({
    mutationFn: (payload: { name: string; email: string; password: string; confirm_password: string }) =>
      registerUser(payload),
    onSuccess: (newUser) => queryClient.setQueryData(["current-user"], newUser),
  });

  const logoutMutation = useMutation({
    mutationFn: logoutUser,
    onSuccess: () => queryClient.setQueryData(["current-user"], null),
  });

  const value: AuthContextValue = {
    user: user ?? null,
    isLoading,
    isAuthenticated: !!user,
    login: (email, password) => loginMutation.mutateAsync({ email, password }),
    register: (name, email, password, confirm_password) =>
      registerMutation.mutateAsync({ name, email, password, confirm_password }),
    logout: () => logoutMutation.mutateAsync(),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
