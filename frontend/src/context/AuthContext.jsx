
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("retina_user")) || null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("retina_token");

    if (!token) {
      setLoading(false);
      return;
    }

    authApi.me()
      .then(({ data }) => {
        setUser(data);
        localStorage.setItem("retina_user", JSON.stringify(data));
      })
      .catch(() => {
        localStorage.removeItem("retina_token");
        localStorage.removeItem("retina_user");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = (data) => {
    localStorage.setItem("retina_token", data.access_token);
    const nextUser = {
      user_id: data.user_id,
      name: data.name,
      email: data.email,
      role: data.role,
    };
    localStorage.setItem("retina_user", JSON.stringify(nextUser));
    setUser(nextUser);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      localStorage.removeItem("retina_token");
      localStorage.removeItem("retina_user");
      setUser(null);
    }
  };

  const value = useMemo(
    () => ({
      user,
      login,
      logout,
      isAuthenticated: !!user && !!localStorage.getItem("retina_token"),
      loading,
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
