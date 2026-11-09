import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { cliente } from "../api/cliente.js";
import CuboRubik from "../componentes/CuboRubikLazy.jsx";
import TarjetaReto from "../componentes/TarjetaReto.jsx";
import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

const CONFETI = Array.from({ length: 22 }, (_, i) => ({
  left: (i * 4.7 + 2) % 100,
  color: ["#009b48", "#b71234", "#0046ad", "#ffd500", "#ff5800", "#ffffff", "#ffd500"][
    i % 7
  ],
  delay: (i * 0.13) % 2.6,
  dur: 2.2 + (i % 5) * 0.25,
}));

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

  const retosJefe = retos.filter((reto) => !reto.es_final);
  const totalJefe = retosJefe.length;
  const resueltosJefe = retosJefe.filter((reto) => reto.resuelto).length;
  const vida = totalJefe ? Math.round(100 * (1 - resueltosJefe / totalJefe)) : 100;
  const porcentajeJefe = totalJefe ? resueltosJefe / totalJefe : 0;
  const derrotado = totalJefe > 0 && resueltosJefe >= totalJefe;

  const FASES = {
    1: { img: "/jefe-fase1.png", nombre: "Fase 1 · El payaso gruñón" },
    2: { img: "/jefe-fase2.png", nombre: "Fase 2 · Se está calentando" },
    3: { img: "/jefe-fase3.png", nombre: "Fase 3 · Modo bestia" },
    4: { img: "/jefe-fase4.png", nombre: "Fase 4 · Forma final" },
    muerte: { img: "/jefe-muerte.png", nombre: "Derrotado" },
  };
  let fase = 1;
  if (derrotado) fase = "muerte";
  else if (porcentajeJefe >= 0.75) fase = 4;
  else if (porcentajeJefe >= 0.5) fase = 3;
  else if (porcentajeJefe >= 0.3) fase = 2;
  const faseActual = FASES[fase];

  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight">
        Hola, {usuario?.nombre_visible || usuario?.usuario}
      </h1>
      <p className="mt-1 text-apagado">Tu progreso en RUBIK CTF.</p>

      {!cargando ? (
        <div className="panel relative mt-6 overflow-hidden p-6 md:p-8">
          <div className="grid items-center gap-6 md:grid-cols-[300px_1fr]">
            <div className="relative mx-auto w-full max-w-[280px] -rotate-1 rounded-2xl border border-[#d8c9ab] bg-[#f4ecdc] p-3 shadow-[0_24px_60px_rgba(0,0,0,.45)]">
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded bg-peligro px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.2em] text-white">
                Boss
              </span>
              <img
                src={faseActual.img}
                alt={faseActual.nombre}
                className={`boss-img mx-auto w-full ${derrotado ? "boss-death" : ""}`}
                style={{ mixBlendMode: "multiply" }}
              />
              {derrotado ? (
                <img src="/explosion.webp" alt="" className="boss-explosion" aria-hidden="true" />
              ) : null}
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-peligro">Jefe final</p>
              <h2 className="mt-1 text-2xl font-bold">{faseActual.nombre}</h2>

              <div className="mt-4">
                <div className="flex items-center justify-between text-sm text-apagado">
                  <span>Vida</span>
                  <span>{vida} / 100</span>
                </div>
                <div className="mt-1 h-4 overflow-hidden rounded-full border border-borde bg-grafito">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-peligro to-aviso transition-all"
                    style={{ width: `${vida}%` }}
                  />
                </div>
              </div>

              <p className="mt-4 text-sm text-apagado">
                {derrotado
                  ? "¡Jefe derrotado! El reto final se ha desbloqueado."
                  : `Cada reto resuelto le quita vida al payaso. Llevas ${resueltosJefe} de ${totalJefe}.`}
              </p>

              {derrotado ? (
                <div className="mt-3 rounded-xl border border-peligro/40 bg-peligro/10 p-3 text-sm text-tinta">
                  Reto final desbloqueado. Búscalo en{" "}
                  <Link to="/retos" className="text-acento-suave hover:underline">
                    Retos
                  </Link>
                  .
                </div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      <div className="mt-8 grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-8">
          {cubo?.cubo_resuelto ? (
            <div className="relative overflow-hidden rounded-2xl border border-acento/40 bg-superficie p-6 text-center">
              <div className="pointer-events-none absolute inset-0" aria-hidden="true">
                {CONFETI.map((confeti, indice) => (
                  <span
                    key={indice}
                    className="confeti"
                    style={{
                      left: `${confeti.left}%`,
                      backgroundColor: confeti.color,
                      animationDelay: `${confeti.delay}s`,
                      animationDuration: `${confeti.dur}s`,
                    }}
                  />
                ))}
              </div>
              <p className="text-sm font-medium text-acento-suave">Completado</p>
              <h2 className="mt-1 text-3xl font-bold tracking-tight">¡Cubo resuelto!</h2>
              <p className="mx-auto mt-2 max-w-md text-sm text-apagado">
                Has resuelto los {total} retos y completado el cubo. Eres oficialmente un
                Rubik Master de RUBIK CTF.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-2 text-sm">
                <span className="rounded-full border border-borde px-3 py-1">
                  {usuario?.puntuacion ?? 0} pts
                </span>
                <span className="rounded-full border border-borde px-3 py-1">
                  {resueltos}/{total} retos
                </span>
              </div>
            </div>
          ) : null}

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
          <CuboRubik inicial={cubo?.secuencia || []} listo={Boolean(cubo)} />
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
