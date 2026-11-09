import { useEffect, useMemo, useState } from "react";

import { cliente } from "../api/cliente.js";
import TarjetaReto from "../componentes/TarjetaReto.jsx";

const FLECHA_HORIZONTAL =
  "flex h-10 items-center justify-center rounded-md border border-borde bg-superficie text-apagado transition hover:bg-superficie-2 hover:text-tinta";
const FLECHA_LATERAL =
  "flex w-10 flex-1 items-center justify-center rounded-md border border-borde bg-superficie text-apagado transition hover:bg-superficie-2 hover:text-tinta";

function indicesColumna(total, columna) {
  const indices = [];
  for (let i = columna; i < total; i += 3) indices.push(i);
  return indices;
}

function indicesFila(total, fila) {
  const indices = [];
  for (let i = fila * 3; i < total && i < fila * 3 + 3; i += 1) indices.push(i);
  return indices;
}

export default function Retos() {
  const [retos, setRetos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [filtro, setFiltro] = useState("todas");
  const [cargando, setCargando] = useState(true);
  const [orden, setOrden] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const [respuestaRetos, respuestaCategorias] = await Promise.all([
          cliente.get("retos/"),
          cliente.get("categorias/"),
        ]);
        setRetos(respuestaRetos.data);
        setCategorias(respuestaCategorias.data);
      } finally {
        setCargando(false);
      }
    })();
  }, []);

  const visibles = useMemo(() => {
    return retos.filter((reto) => {
      return filtro === "todas" || reto.categoria?.slug === filtro;
    });
  }, [retos, filtro]);

  const categoriasConRetos = useMemo(() => {
    const slugs = new Set(retos.map((reto) => reto.categoria?.slug).filter(Boolean));
    return categorias.filter((categoria) => slugs.has(categoria.slug));
  }, [retos, categorias]);

  const claveVisibles = visibles.map((reto) => reto.id).join(",");
  useEffect(() => {
    setOrden([]);
  }, [claveVisibles]);

  const lista = useMemo(() => {
    if (orden.length === 0) return visibles;
    const porId = new Map(visibles.map((reto) => [reto.id, reto]));
    return orden.map((id) => porId.get(id)).filter(Boolean);
  }, [orden, visibles]);

  function desplazar(indices, direccion) {
    const siguiente = [...lista];
    const valores = indices.map((i) => lista[i]);
    if (direccion === 1) valores.unshift(valores.pop());
    else valores.push(valores.shift());
    indices.forEach((indice, k) => {
      siguiente[indice] = valores[k];
    });
    setOrden(siguiente.map((reto) => reto.id));
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight">Retos</h1>
      <p className="mt-1 text-apagado">
        Resuelve cada reto para desbloquear su movimiento del cubo.
      </p>

      <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
        <button
          className={filtro === "todas" ? "boton-primario" : "boton"}
          onClick={() => setFiltro("todas")}
        >
          Todas
        </button>
        {categoriasConRetos.map((categoria) => (
          <button
            key={categoria.slug}
            className={filtro === categoria.slug ? "boton-primario" : "boton"}
            onClick={() => setFiltro(categoria.slug)}
          >
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: categoria.color }}
            />
            {categoria.nombre}
          </button>
        ))}
      </div>

      {cargando ? (
        <p className="mt-6 text-apagado">Cargando retos…</p>
      ) : visibles.length ? (
        <div className="mx-auto mt-12 grid w-full max-w-3xl grid-cols-[auto_1fr_auto] grid-rows-[auto_1fr_auto] gap-2">
          <div />
          <div className="grid grid-cols-3 gap-2">
            {[0, 1, 2].map((columna) => (
              <button
                key={`arriba-${columna}`}
                className={FLECHA_HORIZONTAL}
                onClick={() => desplazar(indicesColumna(lista.length, columna), 1)}
                aria-label={`Desplazar columna ${columna + 1} hacia abajo`}
              >
                ▼
              </button>
            ))}
          </div>
          <div />

          <div className="flex flex-col gap-2">
            {[0, 1, 2].map((fila) => (
              <button
                key={`izquierda-${fila}`}
                className={FLECHA_LATERAL}
                onClick={() => desplazar(indicesFila(lista.length, fila), 1)}
                aria-label={`Desplazar fila ${fila + 1} hacia la derecha`}
              >
                ▶
              </button>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-2">
            {lista.map((reto) => (
              <TarjetaReto key={reto.id} reto={reto} ficha />
            ))}
          </div>

          <div className="flex flex-col gap-2">
            {[0, 1, 2].map((fila) => (
              <button
                key={`derecha-${fila}`}
                className={FLECHA_LATERAL}
                onClick={() => desplazar(indicesFila(lista.length, fila), -1)}
                aria-label={`Desplazar fila ${fila + 1} hacia la izquierda`}
              >
                ◀
              </button>
            ))}
          </div>

          <div />
          <div className="grid grid-cols-3 gap-2">
            {[0, 1, 2].map((columna) => (
              <button
                key={`abajo-${columna}`}
                className={FLECHA_HORIZONTAL}
                onClick={() => desplazar(indicesColumna(lista.length, columna), -1)}
                aria-label={`Desplazar columna ${columna + 1} hacia arriba`}
              >
                ▲
              </button>
            ))}
          </div>
          <div />
        </div>
      ) : (
        <p className="mt-6 text-apagado">No hay retos que coincidan con el filtro.</p>
      )}
    </section>
  );
}
