import { createContext, useContext, useEffect, useState } from "react";

import { cliente, guardarTokens, limpiarTokens, obtenerAccess } from "../api/cliente.js";

const Contexto = createContext(null);

export function ProveedorAutenticacion({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  async function cargarPerfil() {
    try {
      const { data } = await cliente.get("autenticacion/perfil/");
      setUsuario(data);
      return data;
    } catch (error) {
      setUsuario(null);
      return null;
    }
  }

  useEffect(() => {
    (async () => {
      if (obtenerAccess()) {
        await cargarPerfil();
      }
      setCargando(false);
    })();
  }, []);

  // Cookie con el usuario actual, para que los retos separen su estado por usuario.
  useEffect(() => {
    if (usuario?.usuario) {
      document.cookie = `rubik_usuario=${encodeURIComponent(usuario.usuario)}; path=/; max-age=86400; SameSite=Lax`;
    } else {
      document.cookie = "rubik_usuario=; path=/; max-age=0; SameSite=Lax";
    }
  }, [usuario]);

  async function iniciarSesion(usuarioNombre, contrasena) {
    const { data } = await cliente.post("autenticacion/token/", {
      username: usuarioNombre,
      password: contrasena,
    });
    guardarTokens(data);
    return cargarPerfil();
  }

  async function registrarse(datos) {
    await cliente.post("autenticacion/registro/", datos);
    return iniciarSesion(datos.usuario, datos.contrasena);
  }

  function cerrarSesion() {
    limpiarTokens();
    setUsuario(null);
  }

  const valor = {
    usuario,
    cargando,
    iniciarSesion,
    registrarse,
    cerrarSesion,
    cargarPerfil,
  };

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>;
}

export function useAutenticacion() {
  const contexto = useContext(Contexto);
  if (!contexto) {
    throw new Error("useAutenticacion debe usarse dentro de ProveedorAutenticacion");
  }
  return contexto;
}
