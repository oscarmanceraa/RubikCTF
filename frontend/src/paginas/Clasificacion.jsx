import { useEffect, useState } from "react";

import { cliente } from "../api/cliente.js";
import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

export default function Clasificacion() {
  const { usuario } = useAutenticacion();
  const [filas, setFilas] = useState([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const { data } = await cliente.get("clasificacion/");
        setFilas(data);
      } finally {
        setCargando(false);
      }
    })();
  }, []);

  return (
    <section className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold tracking-tight">Clasificación</h1>
      <p className="mt-1 text-apagado">Los 100 participantes con más puntuación.</p>

      {cargando ? (
        <p className="mt-8 text-apagado">Cargando…</p>
      ) : (
        <div className="panel mt-8 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-borde text-left text-apagado">
              <tr>
                <th className="px-5 py-3 font-medium">#</th>
                <th className="px-5 py-3 font-medium">Participante</th>
                <th className="px-5 py-3 text-right font-medium">Retos</th>
                <th className="px-5 py-3 text-right font-medium">Puntos</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-borde">
              {filas.map((fila, indice) => {
                const esYo = usuario && fila.id === usuario.id;
                return (
                  <tr key={fila.id} className={esYo ? "bg-superficie-2" : ""}>
                    <td className="px-5 py-3 text-apagado">{indice + 1}</td>
                    <td className="px-5 py-3">
                      {fila.nombre_visible || fila.usuario}
                      {esYo ? <span className="ml-2 text-acento-suave">(tú)</span> : null}
                    </td>
                    <td className="px-5 py-3 text-right text-apagado">{fila.retos_resueltos}</td>
                    <td className="px-5 py-3 text-right font-semibold">{fila.puntuacion}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {!filas.length ? (
            <p className="p-5 text-apagado">Todavía no hay participantes.</p>
          ) : null}
        </div>
      )}
    </section>
  );
}
