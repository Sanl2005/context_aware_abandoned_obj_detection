import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:3000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ Attach token ONLY ONCE
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ✅ Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
