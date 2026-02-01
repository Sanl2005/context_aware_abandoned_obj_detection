import React, { createContext, useState, useEffect } from "react";
import api from "../api/api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setUser({ role: "admin" }); // decoded on backend already
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const res = await api.post("/login", { email, password });
    localStorage.setItem("token", res.data.token);
    setUser(res.data.user);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
