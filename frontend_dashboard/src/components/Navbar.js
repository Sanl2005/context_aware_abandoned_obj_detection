import React from "react";
import { useAuth } from "../auth/AuthContext";

export default function Navbar() {
  const { logout } = useAuth();

  return (
    <div style={styles.nav}>
      <h2>🚨 Smart Look</h2>
      <button onClick={logout} style={styles.btn}>Logout</button>
    </div>
  );
}

const styles = {
  nav: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 20px",
    background: "#111",
    color: "#fff"
  },
  btn: {
    background: "#e74c3c",
    border: "none",
    color: "#fff",
    padding: "8px 12px",
    cursor: "pointer"
  }
};
