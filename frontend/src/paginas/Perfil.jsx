import { useEffect, useState } from "react";

import { cliente } from "../api/cliente.js";
import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

function Fila({ etiqueta, valor, acento }) {
  return (
    <div className="flex items-center justify-between px-5 py-4">
      <span className="text-sm text-apagado">{etiqueta}</span>
      <span className={`text-sm font-medium ${acento || "text-tinta"}`}>{valor}</span>
    </div>
  );
}

export default function Perfil() {
  const { usuario, cargarPerfil } = useAutenticacion();
  const [nombreVisible, setNombreVisible] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    if (usuario) {
      setNombreVisible(usuario.nombre_visible || "");
    }
  }, [usuario]);

  async function guardar(evento) {
    evento.preventDefault();
    setMensaje("");
    setError("");
    setGuardando(true);
    try {
      await cliente.patch("autenticacion/perfil/", { nombre_visible: nombreVisible });
      await cargarPerfil();
      setMensaje("Perfil actualizado.");
    } catch (fallo) {
      setError("No se pudo actualizar el perfil.");
    } finally {
      setGuardando(false);
    }
  }

  return (
    <section className="mx-auto max-w-xl px-4 py-12">
      <h1 className="text-3xl font-bold tracking-tight">Perfil</h1>

      <div className="panel mt-8 divide-y divide-borde">
        <Fila etiqueta="Usuario" valor={usuario?.usuario} />
        <Fila etiqueta="Correo" valor={usuario?.correo} />
        <Fila etiqueta="Puntuación" valor={usuario?.puntuacion ?? 0} acento="text-acento-suave" />
      </div>

      <form className="panel mt-6 space-y-4 p-6" onSubmit={guardar}>
        <div>
          <label className="etiqueta" htmlFor="nombre_visible">
            Nombre visible
          </label>
          <input
            id="nombre_visible"
            className="campo"
            value={nombreVisible}
            onChange={(evento) => setNombreVisible(evento.target.value)}
          />
        </div>

        {mensaje ? <p className="text-sm text-acento-suave">{mensaje}</p> : null}
        {error ? <p className="text-sm text-peligro">{error}</p> : null}

        <button type="submit" className="boton-primario" disabled={guardando}>
          {guardando ? "Guardando…" : "Guardar cambios"}
        </button>
      </form>
    </section>
  );
}
