import { Link } from "react-router-dom";

import InsigniaDificultad from "./InsigniaDificultad.jsx";

export default function TarjetaReto({ reto }) {
  const color = reto.categoria?.color || "#7c5cff";

  return (
    <Link
      to={`/retos/${reto.slug}`}
      className="panel group flex flex-col gap-3 p-5 transition-colors hover:border-acento-suave"
    >
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-sm text-apagado">
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: color }}
          />
          {reto.categoria?.nombre}
        </span>
        {reto.resuelto ? (
          <span className="text-xs font-medium text-acento-suave">Resuelto</span>
        ) : null}
      </div>

      <h3 className="text-lg font-semibold leading-snug text-tinta transition-colors group-hover:text-acento-suave">
        {reto.nombre}
      </h3>

      <div className="mt-auto flex items-center justify-between pt-1">
        <InsigniaDificultad dificultad={reto.dificultad} etiqueta={reto.etiqueta_dificultad} />
        <span className="text-sm font-semibold text-tinta">
          {reto.puntos}
          <span className="ml-1 font-normal text-apagado">pts</span>
        </span>
      </div>

      {reto.movimientos?.length ? (
        <div className="flex flex-wrap gap-1.5">
          {reto.movimientos.map((movimiento) => (
            <span
              key={movimiento.notacion}
              className="rounded-md bg-grafito px-1.5 py-0.5 font-mono text-xs text-apagado"
            >
              {movimiento.notacion}
            </span>
          ))}
        </div>
      ) : null}
    </Link>
  );
}
