import { useEffect, useState } from "react";

import { cliente } from "../api/cliente.js";

function Rubi({ className }) {
  return (
    <svg
      viewBox="0 0 120 120"
      className={className}
      role="img"
      aria-label="Rubi, la mascota del CTF"
    >
      <line x1="60" y1="22" x2="60" y2="12" stroke="#7c5cff" strokeWidth="3" strokeLinecap="round" />
      <circle cx="60" cy="9" r="4.5" fill="#a855f7" />
      <rect x="20" y="22" width="80" height="80" rx="18" fill="#1e1834" stroke="#7c5cff" strokeWidth="3" />
      <rect x="27" y="29" width="15" height="15" rx="4" fill="#2ecc71" />
      <rect x="78" y="29" width="15" height="15" rx="4" fill="#ff4d4d" />
      <rect x="27" y="78" width="15" height="15" rx="4" fill="#3b82f6" />
      <rect x="78" y="78" width="15" height="15" rx="4" fill="#ffd23f" />
      <circle cx="47" cy="57" r="7" fill="#f4f2ff" />
      <circle cx="73" cy="57" r="7" fill="#f4f2ff" />
      <circle cx="48" cy="58" r="3" fill="#141020" />
      <circle cx="74" cy="58" r="3" fill="#141020" />
      <path d="M48 72 Q60 82 72 72" stroke="#f4f2ff" strokeWidth="3.2" fill="none" strokeLinecap="round" />
    </svg>
  );
}

export default function Mascota({ slug }) {
  const [pregunta, setPregunta] = useState(null);
  const [abierto, setAbierto] = useState(false);
  const [respuesta, setRespuesta] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    let activo = true;
    (async () => {
      for (let intento = 0; intento < 3; intento += 1) {
        try {
          const { data } = await cliente.get(`retos/${slug}/mascota/`);
          if (activo) setPregunta(data);
          return;
        } catch (fallo) {
          if (intento === 2) {
            if (activo) setPregunta(null);
            return;
          }
          await new Promise((resolver) => setTimeout(resolver, 700 * (intento + 1)));
        }
      }
    })();
    return () => {
      activo = false;
    };
  }, [slug]);

  async function responder(evento) {
    evento.preventDefault();
    setError("");
    setEnviando(true);
    try {
      const { data } = await cliente.post(`retos/${slug}/mascota/`, { respuesta });
      if (data.correcto) {
        setPregunta((actual) => ({
          ...actual,
          pista_desbloqueada: true,
          pista: data.pista,
        }));
        setRespuesta("");
      } else {
        setError(data.mensaje || "No es correcto. Inténtalo de nuevo.");
      }
    } catch (fallo) {
      setError("No se pudo comprobar la respuesta.");
    } finally {
      setEnviando(false);
    }
  }

  if (!pregunta?.disponible) {
    return null;
  }

  return (
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end gap-3">
      {abierto ? (
        <div className="panel w-[min(92vw,360px)] overflow-hidden shadow-2xl">
          <div className="flex items-center justify-between border-b border-borde bg-superficie px-4 py-3">
            <div className="flex items-center gap-2">
              <Rubi className="h-7 w-7" />
              <div>
                <p className="text-sm font-semibold text-tinta">Rubi</p>
                <p className="text-[11px] text-apagado">mascota del CTF</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setAbierto(false)}
              className="rounded-full px-2 py-1 text-apagado transition hover:text-tinta"
              aria-label="Cerrar"
            >
              ✕
            </button>
          </div>

          <div className="p-4">
            {pregunta.pista_desbloqueada ? (
              <div className="rounded-xl border border-acento/40 bg-acento/10 p-3">
                <p className="text-xs font-semibold text-acento-suave">Pista desbloqueada</p>
                <p className="mt-1 text-sm text-tinta">{pregunta.pista}</p>
              </div>
            ) : (
              <>
                <div className="rounded-xl rounded-tl-sm border border-borde bg-panel-2 p-3 text-sm text-tinta">
                  {pregunta.texto}
                </div>
                <form className="mt-3" onSubmit={responder}>
                  <input
                    className="campo"
                    value={respuesta}
                    onChange={(evento) => setRespuesta(evento.target.value)}
                    placeholder="Escribe tu respuesta"
                  />
                  <button type="submit" className="boton-primario mt-2 w-full" disabled={enviando}>
                    {enviando ? "Comprobando…" : "Responder"}
                  </button>
                </form>
                {error ? <p className="mt-2 text-sm text-peligro">{error}</p> : null}
              </>
            )}
          </div>
        </div>
      ) : null}

      <div className="flex items-center gap-2">
        {!abierto ? (
          <span className="hidden rounded-full border border-borde bg-superficie px-3 py-1 text-xs text-apagado sm:block">
            ¿Necesitas una pista?
          </span>
        ) : null}
        <button
          type="button"
          onClick={() => setAbierto((valor) => !valor)}
          aria-expanded={abierto}
          aria-label="Hablar con Rubi"
          className="relative grid h-14 w-14 place-items-center rounded-full border border-acento/50 bg-superficie shadow-[0_10px_30px_rgba(124,92,255,.35)] transition hover:scale-105"
        >
          <span className="absolute inset-0 -z-10 rounded-full bg-acento/10" />
          <span className="mascota-flotar">
            <Rubi className="h-11 w-11" />
          </span>
        </button>
      </div>
    </div>
  );
}
