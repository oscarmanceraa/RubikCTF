import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

export default function IniciarSesion() {
  const { iniciarSesion } = useAutenticacion();
  const navegar = useNavigate();
  const ubicacion = useLocation();
  const destino = ubicacion.state?.desde || "/panel";

  const [usuario, setUsuario] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setError("");
    setEnviando(true);
    try {
      await iniciarSesion(usuario, contrasena);
      navegar(destino, { replace: true });
    } catch (fallo) {
      setError("Usuario o contraseña incorrectos.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section className="mx-auto max-w-md px-4 py-16 md:py-24">
      <h1 className="text-3xl font-bold tracking-tight">Entrar</h1>
      <p className="mt-1 text-apagado">Accede para continuar con el CTF.</p>

      <form className="mt-8 space-y-4" onSubmit={manejarEnvio}>
        <div>
          <label className="etiqueta" htmlFor="usuario">
            Usuario
          </label>
          <input
            id="usuario"
            className="campo"
            value={usuario}
            onChange={(evento) => setUsuario(evento.target.value)}
            autoComplete="username"
            required
          />
        </div>
        <div>
          <label className="etiqueta" htmlFor="contrasena">
            Contraseña
          </label>
          <input
            id="contrasena"
            type="password"
            className="campo"
            value={contrasena}
            onChange={(evento) => setContrasena(evento.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        {error ? <p className="text-sm text-peligro">{error}</p> : null}

        <button type="submit" className="boton-primario w-full" disabled={enviando}>
          {enviando ? "Entrando…" : "Entrar"}
        </button>
      </form>

      <p className="mt-6 text-sm text-apagado">
        ¿No tienes cuenta?{" "}
        <Link to="/registro" className="text-acento-suave hover:underline">
          Crea una
        </Link>
      </p>
    </section>
  );
}
