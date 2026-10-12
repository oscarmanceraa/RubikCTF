import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { cliente } from "../api/cliente.js";
import CuboRubik from "../componentes/CuboRubikLazy.jsx";
import InsigniaDificultad from "../componentes/InsigniaDificultad.jsx";
import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

export default function DetalleReto() {
  const { slug } = useParams();
  const { cargarPerfil } = useAutenticacion();

  const [reto, setReto] = useState(null);
  const [inicial, setInicial] = useState([]);
  const [animar, setAnimar] = useState([]);
  const [flag, setFlag] = useState("");
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    (async () => {
      setCargando(true);
      try {
        const { data } = await cliente.get(`retos/${slug}/`);
        setReto(data);
      } catch (fallo) {
        setReto(null);
      } finally {
        setCargando(false);
      }
      try {
        const { data } = await cliente.get("cubo/");
        setInicial(data.secuencia || []);
      } catch (fallo) {
        // sin cubo disponible; se ignora
      }
    })();
  }, [slug]);

  async function enviarFlag(evento) {
    evento.preventDefault();
    setError("");
    setResultado(null);
    setEnviando(true);
    try {
      const { data } = await cliente.post(`retos/${slug}/enviar/`, { flag });
      setResultado(data);
      if (data.correcto) {
        setFlag("");
        setReto((actual) => (actual ? { ...actual, resuelto: true } : actual));
        setAnimar((previos) => [...previos, ...(data.delta || [])]);
        await cargarPerfil();
      }
    } catch (fallo) {
      if (fallo.response?.status === 429) {
        setError("Demasiados intentos seguidos. Espera un momento.");
      } else {
        setError("No se pudo enviar la flag. Inténtalo de nuevo.");
      }
    } finally {
      setEnviando(false);
    }
  }

  if (cargando) {
    return <p className="mx-auto max-w-3xl px-4 py-10 text-apagado">Cargando reto…</p>;
  }

  if (!reto) {
    return (
      <section className="mx-auto max-w-3xl px-4 py-10">
        <p>Este reto no existe o no está activo.</p>
        <Link to="/retos" className="mt-4 inline-block text-acento-suave hover:underline">
          Volver a los retos
        </Link>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-3xl px-4 py-10">
      <Link to="/retos" className="text-sm text-apagado transition-colors hover:text-tinta">
        ← Retos
      </Link>

      <div className="panel mt-4 p-6 md:p-8">
        <div className="flex items-center gap-2 text-sm text-apagado">
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: reto.categoria?.color || "#7c5cff" }}
          />
          {reto.categoria?.nombre}
          {reto.resuelto ? (
            <span className="ml-auto font-medium text-acento-suave">Resuelto</span>
          ) : null}
        </div>

        <h1 className="mt-2 text-3xl font-bold tracking-tight">{reto.nombre}</h1>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <InsigniaDificultad dificultad={reto.dificultad} etiqueta={reto.etiqueta_dificultad} />
          <span className="text-sm font-semibold">
            {reto.puntos}
            <span className="ml-1 font-normal text-apagado">pts</span>
          </span>
          {reto.movimientos?.length ? (
            <span className="flex flex-wrap gap-1.5">
              {reto.movimientos.map((movimiento) => (
                <span
                  key={movimiento.notacion}
                  className="rounded-md bg-grafito px-1.5 py-0.5 font-mono text-xs text-tinta"
                >
                  {movimiento.notacion}
                </span>
              ))}
            </span>
          ) : null}
        </div>

        <p className="mt-6 whitespace-pre-line text-[15px] leading-relaxed text-apagado">
          {reto.descripcion || "Este reto aún no tiene descripción."}
        </p>

        {reto.cantidad_pistas ? (
          <p className="mt-4 text-sm text-apagado">
            Pistas disponibles: {reto.cantidad_pistas}
          </p>
        ) : null}
      </div>

      <div className="panel mt-6 p-6 md:p-8">
        <h2 className="text-xl font-semibold">Enviar flag</h2>
        <p className="mt-1 text-sm text-apagado">
          Formato esperado: <span className="font-mono text-tinta">RUBIK{"{...}"}</span>
        </p>

        <form className="mt-5 flex flex-col gap-3 sm:flex-row" onSubmit={enviarFlag}>
          <input
            className="campo font-mono"
            placeholder="RUBIK{...}"
            value={flag}
            onChange={(evento) => setFlag(evento.target.value)}
            required
          />
          <button type="submit" className="boton-primario shrink-0" disabled={enviando}>
            {enviando ? "Comprobando…" : "Enviar"}
          </button>
        </form>

        {error ? <p className="mt-3 text-sm text-peligro">{error}</p> : null}

        {resultado ? (
          <div
            className={`mt-5 rounded-xl border p-4 text-sm ${
              resultado.correcto
                ? "border-acento/50 bg-acento/10"
                : "border-peligro/50 bg-peligro/10 text-peligro"
            }`}
          >
            <p className={resultado.correcto ? "text-acento-suave" : ""}>{resultado.mensaje}</p>
            {resultado.correcto ? (
              <p className="mt-1 text-apagado">
                +{resultado.puntos_otorgados} puntos · Total: {resultado.puntuacion_total}
                {resultado.delta?.length ? ` · ${resultado.delta.length} giro(s)` : ""}
              </p>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className="mt-6">
        <h2 className="mb-3 text-xl font-semibold">Tu cubo</h2>
        <CuboRubik inicial={inicial} movimientos={animar} />
      </div>
    </section>
  );
}
