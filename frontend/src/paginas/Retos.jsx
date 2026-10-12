import { useEffect, useMemo, useState } from "react";

import { cliente } from "../api/cliente.js";
import TarjetaReto from "../componentes/TarjetaReto.jsx";

export default function Retos() {
  const [retos, setRetos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [filtro, setFiltro] = useState("todas");
  const [soloPendientes, setSoloPendientes] = useState(false);
  const [cargando, setCargando] = useState(true);

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
      const coincideCategoria = filtro === "todas" || reto.categoria?.slug === filtro;
      const coincideEstado = !soloPendientes || !reto.resuelto;
      return coincideCategoria && coincideEstado;
    });
  }, [retos, filtro, soloPendientes]);

  return (
    <section className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight">Retos</h1>
      <p className="mt-1 text-apagado">
        Resuelve cada reto para desbloquear su movimiento del cubo.
      </p>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        <button
          className={filtro === "todas" ? "boton-primario" : "boton"}
          onClick={() => setFiltro("todas")}
        >
          Todas
        </button>
        {categorias.map((categoria) => (
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
        <label className="ml-auto flex cursor-pointer items-center gap-2 text-sm text-apagado">
          <input
            type="checkbox"
            className="accent-acento"
            checked={soloPendientes}
            onChange={(evento) => setSoloPendientes(evento.target.checked)}
          />
          Solo pendientes
        </label>
      </div>

      {cargando ? (
        <p className="mt-6 text-apagado">Cargando retos…</p>
      ) : visibles.length ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visibles.map((reto) => (
            <TarjetaReto key={reto.id} reto={reto} />
          ))}
        </div>
      ) : (
        <p className="mt-6 text-apagado">No hay retos que coincidan con el filtro.</p>
      )}
    </section>
  );
}
