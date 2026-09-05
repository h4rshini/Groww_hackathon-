import { createContext, useContext, useEffect, useState } from "react";

import { api, getToken, setToken } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    // Validate the stored token by fetching the user; drop it if it's stale.
    api.me()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  async function authenticate(fn, email, password) {
    const { access_token } = await fn(email, password);
    setToken(access_token);
    setUser(await api.me());
  }

  const value = {
    user,
    loading,
    login: (email, password) => authenticate(api.login, email, password),
    register: (email, password) => authenticate(api.register, email, password),
    logout: () => {
      setToken(null);
      setUser(null);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
