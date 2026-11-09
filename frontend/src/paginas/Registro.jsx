import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

function extraerErrores(datos) {
  if (!datos || typeof datos !== "object") return "No se pudo completar el registro.";
  const mensajes = [];
  for (const [campo, valor] of Object.entries(datos)) {
    const texto = Array.isArray(valor) ? valor.join(" ") : String(valor);
    mensajes.push(`${campo}: ${texto}`);
  }
  return mensajes.join(" · ") || "No se pudo completar el registro.";
}

export default function Registro() {
  const { registrarse } = useAutenticacion();
  const navegar = useNavigate();

  const [formulario, setFormulario] = useState({
    usuario: "",
    correo: "",
    nombre_visible: "",
    contrasena: "",
  });
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  function actualizar(campo, valor) {
    setFormulario((actual) => ({ ...actual, [campo]: valor }));
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setError("");
    setEnviando(true);
    try {
      await registrarse(formulario);
      navegar("/panel", { replace: true });
    } catch (fallo) {
      setError(extraerErrores(fallo.response?.data));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section className="relative py-12 md:py-20">
      <div className="mx-auto w-full max-w-page px-4 md:px-6">
        <div className="mx-auto w-full max-w-[440px]">
          <div className="rounded-lg border border-line bg-surface p-6 md:p-8">
            <div className="flex flex-col items-center text-center">
              <span className="grid h-12 w-12 grid-cols-3 gap-0.5 rounded-md bg-surface-body p-1">
                <span className="rounded-[2px] bg-cube-red" />
                <span className="rounded-[2px] bg-cube-white" />
                <span className="rounded-[2px] bg-cube-blue" />
                <span className="rounded-[2px] bg-cube-orange" />
                <span className="rounded-[2px] bg-cube-yellow" />
                <span className="rounded-[2px] bg-cube-green" />
                <span className="rounded-[2px] bg-cube-blue" />
                <span className="rounded-[2px] bg-cube-red" />
                <span className="rounded-[2px] bg-cube-white" />
              </span>
              <h1 className="mt-4 text-3xl font-bold tracking-tight text-cube-white">
                Crear cuenta
              </h1>
              <p className="mt-1 text-sm text-muted">Empieza a resolver retos.</p>
            </div>

            <form className="mt-6 space-y-4" onSubmit={manejarEnvio}>
              <div>
                <label className="etiqueta" htmlFor="usuario">
                  Usuario
                </label>
                <input
                  id="usuario"
                  className="campo"
                  value={formulario.usuario}
                  onChange={(evento) => actualizar("usuario", evento.target.value)}
                  autoComplete="username"
                  required
                />
              </div>
              <div>
                <label className="etiqueta" htmlFor="correo">
                  Correo
                </label>
                <input
                  id="correo"
                  type="email"
                  className="campo"
                  value={formulario.correo}
                  onChange={(evento) => actualizar("correo", evento.target.value)}
                  autoComplete="email"
                  required
                />
              </div>
              <div>
                <label className="etiqueta" htmlFor="nombre_visible">
                  Nombre visible (opcional)
                </label>
                <input
                  id="nombre_visible"
                  className="campo"
                  value={formulario.nombre_visible}
                  onChange={(evento) => actualizar("nombre_visible", evento.target.value)}
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
                  value={formulario.contrasena}
                  onChange={(evento) => actualizar("contrasena", evento.target.value)}
                  autoComplete="new-password"
                  required
                />
              </div>

              {error ? <p className="text-sm text-cube-red">{error}</p> : null}

              <button type="submit" className="boton-primario w-full" disabled={enviando}>
                {enviando ? "Creando…" : "Crear cuenta"}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-muted">
              ¿Ya tienes cuenta?{" "}
              <Link to="/iniciar-sesion" className="font-semibold text-cube-yellow hover:underline">
                Entra
              </Link>
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
