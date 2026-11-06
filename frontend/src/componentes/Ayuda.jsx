import { useEffect, useState } from "react";

import { cliente } from "../api/cliente.js";

function Burbuja({ children }) {
  return (
    <div className="rounded-xl rounded-tl-sm border border-borde bg-panel-2 p-3 text-sm text-tinta">
      {children}
    </div>
  );
}

export default function Ayuda({ slug }) {
  const [pregunta, setPregunta] = useState(null);
  const [abierto, setAbierto] = useState(false);
  const [paso, setPaso] = useState(0);
  const [burla, setBurla] = useState("");
  const [respuesta, setRespuesta] = useState("");
  const [errorRed, setErrorRed] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [recienAcertado, setRecienAcertado] = useState(false);

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

  function abrir() {
    setAbierto(true);
    setPaso(0);
    setBurla("");
    setRespuesta("");
    setErrorRed("");
    setRecienAcertado(false);
  }

  function avanzar() {
    setBurla("");
    setPaso((actual) => Math.min(actual + 1, 3));
  }

  async function responder(evento) {
    evento.preventDefault();
    setErrorRed("");
    setBurla("");
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
        setRecienAcertado(true);
      } else {
        setBurla("Jajaja, no. Inténtelo otra vez.");
      }
    } catch (fallo) {
      setErrorRed("No se pudo comprobar la respuesta.");
    } finally {
      setEnviando(false);
    }
  }

  if (!pregunta?.disponible) {
    return null;
  }

  const yaTiene = pregunta.pista_desbloqueada;

  let frase;
  if (yaTiene) {
    frase = recienAcertado ? "Tome, vea la pista." : "Ya le di la pista. No me moleste más.";
  } else if (paso === 0) {
    frase = "¿Qué necesita?";
  } else if (paso === 1) {
    frase = "¡Qué quiere!";
  } else if (paso === 2) {
    frase = "No sea cansón.";
  } else {
    frase = "Listo, pero respóndame esto:";
  }

  const textoBoton = paso === 2 ? "Por favor" : "Necesito ayuda";

  return (
    <>
      {abierto ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#05070d]/70 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-label="Ayuda"
          onClick={() => setAbierto(false)}
        >
          <div
            className="panel relative w-full max-w-3xl overflow-hidden"
            onClick={(evento) => evento.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setAbierto(false)}
              aria-label="Cerrar ayuda"
              className="absolute right-3 top-3 z-10 grid h-9 w-9 place-items-center rounded-full border border-borde bg-superficie text-apagado transition hover:text-tinta"
            >
              ✕
            </button>

            <div className="grid sm:grid-cols-[280px_1fr]">
              <div className="flex items-center justify-center bg-[#f4ecdc] p-5">
                <img
                  src="/ayuda2.png"
                  alt="Ayuda"
                  className="max-h-[380px] w-auto object-contain drop-shadow-md"
                />
              </div>

              <div className="flex flex-col gap-4 p-6">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-acento" />
                  <p className="text-sm font-semibold text-tinta">
                    Ayuda <span className="font-normal text-apagado">· pistas del reto</span>
                  </p>
                </div>

                <Burbuja>{frase}</Burbuja>

                {yaTiene ? (
                  <div className="rounded-xl border border-acento/40 bg-acento/10 p-3">
                    <p className="text-xs font-semibold text-acento-suave">Pista</p>
                    <p className="mt-1 text-sm text-tinta">{pregunta.pista}</p>
                  </div>
                ) : paso < 3 ? (
                  <div className="mt-auto">
                    <button type="button" className="boton-primario w-full" onClick={avanzar}>
                      {textoBoton}
                    </button>
                  </div>
                ) : (
                  <>
                    <Burbuja>{pregunta.texto}</Burbuja>
                    {burla ? <Burbuja>{burla}</Burbuja> : null}
                    <form className="flex flex-col gap-2" onSubmit={responder}>
                      <input
                        className="campo"
                        value={respuesta}
                        onChange={(evento) => setRespuesta(evento.target.value)}
                        placeholder="Escriba su respuesta"
                      />
                      <button type="submit" className="boton-primario" disabled={enviando}>
                        {enviando ? "Comprobando…" : "Responder"}
                      </button>
                    </form>
                    {errorRed ? <p className="text-sm text-peligro">{errorRed}</p> : null}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <div className="fixed bottom-5 right-5 z-40 flex items-center gap-2">
        <span className="hidden rounded-full border border-borde bg-superficie px-3 py-1 text-xs text-apagado sm:block">
          ¿Necesitas ayuda?
        </span>
        <button
          type="button"
          onClick={abrir}
          aria-label="Abrir ayuda"
          className="relative h-16 w-16 overflow-hidden rounded-full shadow-[0_10px_30px_rgba(124,92,255,.35)] ring-2 ring-acento/40 transition hover:scale-105"
        >
          <span className="mascota-flotar block h-full w-full">
            <img
              src="/ayuda.png"
              alt="Ayuda"
              className="h-full w-full scale-110 object-cover object-center"
            />
          </span>
        </button>
      </div>
    </>
  );
}
