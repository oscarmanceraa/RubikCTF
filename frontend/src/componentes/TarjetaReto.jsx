import { Link } from "react-router-dom";

import { COLORES_CARA } from "../cubo/motor.js";
import InsigniaDificultad from "./InsigniaDificultad.jsx";

function colorDeReto(reto) {
  const notacion = reto.movimientos?.[0]?.notacion || "";
  const cara = notacion[0]?.toUpperCase();
  if (cara && COLORES_CARA[cara]) return COLORES_CARA[cara];
  return reto.categoria?.color || "#ffd500";
}

function colorDeTexto(hex) {
  const limpio = (hex || "#ffd500").replace("#", "");
  const r = parseInt(limpio.slice(0, 2), 16) || 0;
  const g = parseInt(limpio.slice(2, 4), 16) || 0;
  const b = parseInt(limpio.slice(4, 6), 16) || 0;
  const luminancia = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminancia > 0.5 ? "#0d0d0f" : "#ffffff";
}

function TarjetaClasica({ reto }) {
  const color = reto.categoria?.color || "#ffd500";

  return (
    <Link
      to={`/retos/${reto.slug}`}
      className="panel group flex flex-col gap-3 p-5 transition hover:-translate-y-0.5"
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

function FichaCubo({ reto }) {
  const color = colorDeReto(reto);
  const texto = colorDeTexto(color);
  const sutil = texto === "#ffffff" ? "rgba(255,255,255,0.18)" : "rgba(0,0,0,0.18)";
  const chip = texto === "#ffffff" ? "rgba(255,255,255,0.16)" : "rgba(0,0,0,0.16)";

  return (
    <Link
      to={`/retos/${reto.slug}`}
      className="group flex aspect-square flex-col gap-2 p-3 transition hover:-translate-y-0.5 sm:p-4"
      style={{
        backgroundColor: color,
        color: texto,
        borderRadius: "var(--radius-lg)",
        boxShadow: "inset 0 0 0 1px rgba(0,0,0,0.12), 0 10px 30px rgba(0,0,0,0.3)",
      }}
    >
      <div className="flex items-center justify-between text-[11px] font-medium opacity-90 sm:text-xs">
        <span className="truncate">{reto.categoria?.nombre}</span>
        {reto.resuelto ? <span className="shrink-0">✓</span> : null}
      </div>

      <h3 className="text-sm font-semibold leading-snug sm:text-base">{reto.nombre}</h3>

      <div className="mt-auto flex flex-wrap items-center justify-between gap-2 pt-1">
        <span
          className="rounded-full px-2 py-0.5 text-[11px] font-medium sm:text-xs"
          style={{ backgroundColor: sutil }}
        >
          {reto.etiqueta_dificultad || reto.dificultad}
        </span>
        <span className="text-xs font-semibold sm:text-sm">
          {reto.puntos}
          <span className="ml-1 font-normal opacity-80">pts</span>
        </span>
      </div>

      {reto.movimientos?.length ? (
        <div className="flex flex-wrap gap-1.5">
          {reto.movimientos.map((movimiento) => (
            <span
              key={movimiento.notacion}
              className="rounded-md px-1.5 py-0.5 font-mono text-[11px] sm:text-xs"
              style={{ backgroundColor: chip }}
            >
              {movimiento.notacion}
            </span>
          ))}
        </div>
      ) : null}
    </Link>
  );
}

export default function TarjetaReto({ reto, ficha = false }) {
  return ficha ? <FichaCubo reto={reto} /> : <TarjetaClasica reto={reto} />;
}
