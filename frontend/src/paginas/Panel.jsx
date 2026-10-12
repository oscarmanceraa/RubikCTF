import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { cliente } from "../api/cliente.js";
import CuboRubik from "../componentes/CuboRubikLazy.jsx";
import TarjetaReto from "../componentes/TarjetaReto.jsx";
import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

export default function Panel() {
  const { usuario } = useAutenticacion();
  const [retos, setRetos] = useState([]);
  const [cubo, setCubo] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [respuestaRetos, respuestaCubo] = await Promise.all([
          cliente.get("retos/"),
          cliente.get("cubo/"),
        ]);
        setRetos(respuestaRetos.data);
        setCubo(respuestaCubo.data);
      } finally {
        setCargando(false);
      }
    })();
  }, []);

  const resueltos = retos.filter((reto) => reto.resuelto).length;
  const total = retos.length;
  const porcentaje = total ? Math.round((resueltos / total) * 100) : 0;
  const pendientes = retos.filter((reto) => !reto.resuelto).slice(0, 4);

  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight">
        Hola, {usuario?.nombre_visible || usuario?.usuario}
      </h1>
      <p className="mt-1 text-apagado">Tu progreso en RUBIK CTF.</p>

      <div className="mt-8 grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-8">
          <div className="panel p-6">
            <div className="flex flex-wrap items-end justify-between gap-6">
              <div>
                <p className="text-sm text-apagado">Puntuación</p>
                <p className="text-5xl font-bold tracking-tight">{usuario?.puntuacion ?? 0}</p>
              </div>
              <div className="flex gap-8">
                <div>
                  <p className="text-sm text-apagado">Retos resueltos</p>
                  <p className="text-2xl font-semibold">
                    {resueltos}
                    <span className="text-apagado">/{total}</span>
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between text-sm text-apagado">
                <span>Progreso</span>
                <span>{porcentaje}%</span>
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-superficie-2">
                <div
                  className="h-full rounded-full bg-acento transition-all"
                  style={{ width: `${porcentaje}%` }}
                />
              </div>
              {cubo?.cubo_resuelto ? (
                <p className="mt-3 text-sm font-medium text-acento-suave">
                  Cubo resuelto. Enhorabuena.
                </p>
              ) : null}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Retos pendientes</h2>
              <Link to="/retos" className="text-sm text-acento-suave hover:underline">
                Ver todos
              </Link>
            </div>

            {cargando ? (
              <p className="mt-4 text-apagado">Cargando…</p>
            ) : pendientes.length ? (
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {pendientes.map((reto) => (
                  <TarjetaReto key={reto.id} reto={reto} />
                ))}
              </div>
            ) : (
              <p className="mt-4 text-apagado">
                No hay retos pendientes. Has completado todo el contenido disponible.
              </p>
            )}
          </div>
        </div>

        <aside className="lg:sticky lg:top-24 lg:self-start">
          <h2 className="mb-3 text-xl font-semibold">Tu cubo</h2>
          <CuboRubik inicial={cubo?.secuencia || []} />
          <p className="mt-3 text-sm text-apagado">
            {cubo?.cubo_resuelto
              ? "Cubo resuelto. Has completado todos los retos."
              : "El cubo se completa a medida que resuelves retos."}
          </p>
        </aside>
      </div>
    </section>
  );
}
