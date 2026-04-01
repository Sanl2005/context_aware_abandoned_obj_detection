import React, { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

// Demo credentials - replace with real backend authentication
const DEMO_CREDENTIALS = {
  username: "admin",
  password: "admin123"
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem("sentinelEye_user");
    const sessionExpiry = localStorage.getItem("sentinelEye_session_expiry");

    if (storedUser && sessionExpiry) {
      const now = new Date().getTime();
      if (now < parseInt(sessionExpiry)) {
        // Session is still valid
        setUser(JSON.parse(storedUser));
      } else {
        // Session expired, clear storage
        localStorage.removeItem("sentinelEye_user");
        localStorage.removeItem("sentinelEye_session_expiry");
      }
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    // Validate credentials
    if (username === DEMO_CREDENTIALS.username && password === DEMO_CREDENTIALS.password) {
      const userData = {
        username: username,
        role: "admin",
        loginTime: new Date().toISOString()
      };

      // Set session expiry (24 hours)
      const expiryTime = new Date().getTime() + (24 * 60 * 60 * 1000);

      localStorage.setItem("sentinelEye_user", JSON.stringify(userData));
      localStorage.setItem("sentinelEye_session_expiry", expiryTime.toString());
      setUser(userData);

      return true;
    } else {
      throw new Error("Invalid username or password");
    }
  };

  const loginWithOAuth = async (provider, token, userInfo) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    try {
      // In a real application, you would send the token to your backend
      // and verify it on the server side
      const userData = {
        username: userInfo.email || userInfo.name,
        email: userInfo.email,
        name: userInfo.name,
        picture: userInfo.picture,
        provider: provider, // 'google' or 'apple'
        role: "user",
        loginTime: new Date().toISOString()
      };

      // Set session expiry (24 hours)
      const expiryTime = new Date().getTime() + (24 * 60 * 60 * 1000);

      localStorage.setItem("sentinelEye_user", JSON.stringify(userData));
      localStorage.setItem("sentinelEye_session_expiry", expiryTime.toString());
      setUser(userData);

      return true;
    } catch (error) {
      throw new Error("OAuth authentication failed");
    }
  };

  const logout = () => {
    localStorage.removeItem("sentinelEye_user");
    localStorage.removeItem("sentinelEye_session_expiry");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, loginWithOAuth, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
