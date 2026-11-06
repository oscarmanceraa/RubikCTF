import { useEffect, useState } from "react";

import { cliente } from "../api/cliente.js";

function AyudaAvatar({ className }) {
  const [error, setError] = useState(false);
  return (
    <span
      className={`grid shrink-0 place-items-center overflow-hidden rounded-full bg-[#f4ecdc] ring-1 ring-acento/30 ${className}`}
    >
      {error ? (
        <span className="font-bold text-[#7c5cff]">?</span>
      ) : (
        <img
          src="/ayuda.png"
          alt="Ayuda"
          onError={() => setError(true)}
          className="h-full w-full object-cover object-[center_18%]"
        />
      )}
    </span>
  );
}

export default function Ayuda({ slug }) {
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
              <AyudaAvatar className="h-9 w-9" />
              <div>
                <p className="text-sm font-semibold text-tinta">Ayuda</p>
                <p className="text-[11px] text-apagado">Pistas del reto</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setAbierto(false)}
              className="rounded-full px-2 py-1 text-apagado transition hover:text-tinta"
              aria-label="Cerrar ayuda"
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
            ¿Necesitas ayuda?
          </span>
        ) : null}
        <button
          type="button"
          onClick={() => setAbierto((valor) => !valor)}
          aria-expanded={abierto}
          aria-label="Abrir ayuda"
          className="relative grid h-16 w-16 place-items-center rounded-full shadow-[0_10px_30px_rgba(124,92,255,.35)] transition hover:scale-105"
        >
          <span className="absolute inset-0 -z-10 rounded-full bg-acento/10" />
          <span className="mascota-flotar">
            <AyudaAvatar className="h-16 w-16" />
          </span>
        </button>
      </div>
    </div>
  );
}
