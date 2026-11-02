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
      <rect
        x="20"
        y="22"
        width="80"
        height="80"
        rx="18"
        fill="#1e1834"
        stroke="#7c5cff"
        strokeWidth="3"
      />
      <rect x="27" y="29" width="15" height="15" rx="4" fill="#2ecc71" />
      <rect x="78" y="29" width="15" height="15" rx="4" fill="#ff4d4d" />
      <rect x="27" y="78" width="15" height="15" rx="4" fill="#3b82f6" />
      <rect x="78" y="78" width="15" height="15" rx="4" fill="#ffd23f" />
      <circle cx="47" cy="57" r="7" fill="#f4f2ff" />
      <circle cx="73" cy="57" r="7" fill="#f4f2ff" />
      <circle cx="48" cy="58" r="3" fill="#141020" />
      <circle cx="74" cy="58" r="3" fill="#141020" />
      <path
        d="M48 72 Q60 82 72 72"
        stroke="#f4f2ff"
        strokeWidth="3.2"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
}

export default function Mascota({ slug }) {
  const [pregunta, setPregunta] = useState(null);
  const [respuesta, setRespuesta] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let activo = true;
    (async () => {
      setCargando(true);
      try {
        const { data } = await cliente.get(`retos/${slug}/mascota/`);
        if (activo) setPregunta(data);
      } catch (fallo) {
        if (activo) setPregunta(null);
      } finally {
        if (activo) setCargando(false);
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

  if (cargando) {
    return <div className="panel p-5 text-sm text-apagado">Rubi está pensando…</div>;
  }

  if (!pregunta?.disponible) {
    return null;
  }

  return (
    <div className="panel p-5">
      <div className="flex items-start gap-4">
        <Rubi className="h-20 w-20 shrink-0" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-tinta">
            Rubi <span className="font-normal text-apagado">· mascota del CTF</span>
          </p>

          {pregunta.pista_desbloqueada ? (
            <div className="mt-2 rounded-xl border border-acento/40 bg-acento/10 p-3">
              <p className="text-xs font-semibold text-acento-suave">Pista desbloqueada</p>
              <p className="mt-1 text-sm text-tinta">{pregunta.pista}</p>
            </div>
          ) : (
            <>
              <p className="mt-1 text-sm text-apagado">{pregunta.texto}</p>
              <form className="mt-3 flex flex-col gap-2 sm:flex-row" onSubmit={responder}>
                <input
                  className="campo"
                  value={respuesta}
                  onChange={(evento) => setRespuesta(evento.target.value)}
                  placeholder="Escribe tu respuesta"
                />
                <button type="submit" className="boton-primario shrink-0" disabled={enviando}>
                  {enviando ? "Comprobando…" : "Responder"}
                </button>
              </form>
              {error ? <p className="mt-2 text-sm text-peligro">{error}</p> : null}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
