import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const CLAVE_ACCESS = "rubikctf_access";
const CLAVE_REFRESH = "rubikctf_refresh";

export const cliente = axios.create({ baseURL: BASE });

export function obtenerAccess() {
  return localStorage.getItem(CLAVE_ACCESS);
}

export function guardarTokens({ access, refresh }) {
  if (access) localStorage.setItem(CLAVE_ACCESS, access);
  if (refresh) localStorage.setItem(CLAVE_REFRESH, refresh);
}

export function limpiarTokens() {
  localStorage.removeItem(CLAVE_ACCESS);
  localStorage.removeItem(CLAVE_REFRESH);
}

cliente.interceptors.request.use((config) => {
  const access = obtenerAccess();
  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

let refrescoEnCurso = null;

cliente.interceptors.response.use(
  (respuesta) => respuesta,
  async (error) => {
    const original = error.config;
    const refresh = localStorage.getItem(CLAVE_REFRESH);

    if (error.response?.status === 401 && refresh && !original._reintento) {
      original._reintento = true;
      try {
        refrescoEnCurso =
          refrescoEnCurso ||
          axios.post(`${BASE}/autenticacion/token/refrescar/`, { refresh });
        const { data } = await refrescoEnCurso;
        refrescoEnCurso = null;
        guardarTokens({ access: data.access });
        original.headers.Authorization = `Bearer ${data.access}`;
        return cliente(original);
      } catch (falloRefresco) {
        refrescoEnCurso = null;
        limpiarTokens();
      }
    }
    return Promise.reject(error);
  }
);
