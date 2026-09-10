
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("retina_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("retina_token");
      localStorage.removeItem("retina_user");
    }
    return Promise.reject(error);
  }
);

export const apiOrigin = API_BASE_URL.replace(/\/api\/?$/, "");

export const toAbsoluteUrl = (url) => {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  return `${apiOrigin}${url.startsWith("/") ? "" : "/"}${url}`;
};

export const authApi = {
  login: (payload) => api.post("/auth/login", payload),
  register: (payload) => api.post("/auth/register", payload),
  me: () => api.get("/auth/me"),
  logout: () => api.post("/auth/logout"),
};

export const patientApi = {
  create: (payload) => api.post("/patients", payload),
  get: (id) => api.get(`/patients/${id}`),
  list: () => api.get("/patients"),
};

export const screeningApi = {
  create: (payload) => api.post("/screenings", payload),
  list: () => api.get("/screenings"),
  get: (caseId) => api.get(`/screenings/${caseId}`),
  comparison: (caseId) => api.get(`/screenings/${caseId}/comparison`),

  upload: (caseId, eye, file) => {
    const formData = new FormData();
    formData.append("eye", eye);
    formData.append("image", file);
    return api.post(`/screenings/${caseId}/image`, formData);
  },

  updateQuality: (caseId, quality) =>
    api.patch(`/screenings/${caseId}/quality`, quality),

  analyze: (caseId, eye) =>
    api.post(`/screenings/${caseId}/analyze`, null, {
      params: { eye },
      timeout: 180000,
    }),
};

export const reviewApi = {
  create: (payload) => api.post("/reviews", payload),
  pending: () => api.get("/reviews/pending"),
  update: (reviewId, payload) => api.put(`/reviews/${reviewId}`, payload),
};

export const reportApi = {
  get: (caseId) => api.get(`/reports/${caseId}`),
  pdfUrl: (caseId) => `${API_BASE_URL}/reports/${caseId}/pdf`,
};

export default api;
