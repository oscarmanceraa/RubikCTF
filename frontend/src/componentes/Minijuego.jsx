import { useEffect, useMemo, useRef, useState } from "react";

const COLORES_CUBO = {
  U: "#f2f2f2",
  R: "#ff3b3b",
  F: "#2ecc71",
  D: "#ffd23f",
  L: "#ff8c1a",
  B: "#2f80ed",
};
const LETRAS = ["R", "F", "B", "L", "D", "U"];

const ETIQUETAS = {
  ordenar: "Ordena el comando",
  paciencia: "La paciencia del payaso",
  simon: "Simon del cubo",
  ppt: "Piedra, papel o tijera",
};

function Ordenar({ tokens, comprobar }) {
  const [usados, setUsados] = useState([]);
  const [enviando, setEnviando] = useState(false);

  const restantes = tokens
    .map((token, indice) => ({ token, indice }))
    .filter(({ indice }) => !usados.includes(indice));
  const texto = usados.map((indice) => tokens[indice]).join(" ");

  async function revisar() {
    setEnviando(true);
    await comprobar({ orden: texto });
    setEnviando(false);
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-apagado">Pulsa las piezas en orden para armar el comando.</p>
      <div className="min-h-10 break-all rounded-lg border border-borde bg-grafito p-2 font-mono text-xs text-tinta">
        {texto || <span className="text-apagado">…</span>}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {restantes.map(({ token, indice }) => (
          <button
            key={indice}
            type="button"
            onClick={() => setUsados([...usados, indice])}
            className="rounded-md border border-borde px-2 py-1 font-mono text-xs text-tinta transition hover:border-acento"
          >
            {token}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <button type="button" className="boton" onClick={() => setUsados([])}>
          Borrar
        </button>
        <button
          type="button"
          className="boton-primario"
          disabled={enviando || tokens.length === 0 || usados.length !== tokens.length}
          onClick={revisar}
        >
          {enviando ? "Comprobando…" : "Comprobar"}
        </button>
      </div>
    </div>
  );
}

function Paciencia({ comprobar }) {
  const [pos, setPos] = useState(0);
  const [activo, setActivo] = useState(true);
  const [fallo, setFallo] = useState("");
  const direccion = useRef(1);

  useEffect(() => {
    if (!activo) return undefined;
    const id = setInterval(() => {
      setPos((actual) => {
        let siguiente = actual + direccion.current * 3;
        if (siguiente >= 100) {
          siguiente = 100;
          direccion.current = -1;
        }
        if (siguiente <= 0) {
          siguiente = 0;
          direccion.current = 1;
        }
        return siguiente;
      });
    }, 16);
    return () => clearInterval(id);
  }, [activo]);

  async function detener() {
    if (pos >= 40 && pos <= 60) {
      setActivo(false);
      await comprobar({ completado: true });
    } else {
      setFallo("¡Ja! Inténtelo otra vez.");
      setPos(0);
      direccion.current = 1;
    }
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-apagado">Detén la barra en la zona verde.</p>
      <div className="relative h-4 rounded-full bg-grafito">
        <div className="absolute inset-y-0 left-[40%] w-[20%] bg-acento/40" />
        <div
          className="absolute top-0 h-4 w-1 rounded bg-tinta"
          style={{ left: `calc(${pos}% - 2px)` }}
        />
      </div>
      <button type="button" className="boton-primario" onClick={detener} disabled={!activo}>
        Detener
      </button>
      {fallo ? <p className="text-sm text-aviso">{fallo}</p> : null}
    </div>
  );
}

function Simon({ comprobar }) {
  const [secuencia, setSecuencia] = useState([]);
  const [fase, setFase] = useState("memorizar");
  const [indice, setIndice] = useState(0);
  const [fallo, setFallo] = useState("");

  function nueva() {
    const siguiente = Array.from(
      { length: 3 },
      () => LETRAS[Math.floor(Math.random() * LETRAS.length)]
    );
    setSecuencia(siguiente);
    setFase("memorizar");
    setIndice(0);
    setFallo("");
  }

  useEffect(() => {
    nueva();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (fase !== "memorizar") return undefined;
    const id = setTimeout(() => setFase("jugar"), 3000);
    return () => clearTimeout(id);
  }, [fase, secuencia]);

  async function pulsar(letra) {
    if (fase !== "jugar") return;
    if (letra !== secuencia[indice]) {
      setFallo("¡Ja! Inténtelo otra vez.");
      nueva();
      return;
    }
    const siguiente = indice + 1;
    if (siguiente >= secuencia.length) {
      setFase("listo");
      await comprobar({ completado: true });
    } else {
      setIndice(siguiente);
    }
  }

  return (
    <div className="space-y-3">
      {fase === "memorizar" ? (
        <>
          <p className="text-sm text-apagado">Memoriza la secuencia…</p>
          <div className="flex gap-2">
            {secuencia.map((letra, i) => (
              <span
                key={i}
                className="h-10 w-10 rounded-lg"
                style={{ backgroundColor: COLORES_CUBO[letra] }}
              />
            ))}
          </div>
        </>
      ) : (
        <>
          <p className="text-sm text-apagado">Repite la secuencia ({indice}/{secuencia.length}).</p>
          <div className="grid grid-cols-3 gap-2">
            {LETRAS.map((letra) => (
              <button
                key={letra}
                type="button"
                onClick={() => pulsar(letra)}
                className="h-10 rounded-lg border border-borde transition hover:scale-105"
                style={{ backgroundColor: COLORES_CUBO[letra] }}
                aria-label={letra}
              />
            ))}
          </div>
        </>
      )}
      {fallo ? <p className="text-sm text-aviso">{fallo}</p> : null}
    </div>
  );
}

function PPT({ comprobar }) {
  const [yo, setYo] = useState(0);
  const [payaso, setPayaso] = useState(0);
  const [mensaje, setMensaje] = useState("");

  async function jugar(eleccion) {
    const opciones = ["piedra", "papel", "tijera"];
    const suya = opciones[Math.floor(Math.random() * opciones.length)];
    const ganaYo =
      (eleccion === "piedra" && suya === "tijera") ||
      (eleccion === "papel" && suya === "piedra") ||
      (eleccion === "tijera" && suya === "papel");

    if (eleccion === suya) {
      setMensaje(`Empate (${eleccion} vs ${suya}).`);
      return;
    }

    if (ganaYo) {
      const nuevo = yo + 1;
      setYo(nuevo);
      setMensaje(`Ganas (${eleccion} vs ${suya}).`);
      if (nuevo >= 2) {
        await comprobar({ completado: true });
      }
    } else {
      const nuevo = payaso + 1;
      setPayaso(nuevo);
      setMensaje(`Pierdes (${eleccion} vs ${suya}).`);
      if (nuevo >= 2) {
        setMensaje("Jajaja, perdiste. Otra vez.");
        setYo(0);
        setPayaso(0);
      }
    }
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-apagado">Gánale al payaso al mejor de 3.</p>
      <div className="flex gap-2">
        {["piedra", "papel", "tijera"].map((opcion) => (
          <button
            key={opcion}
            type="button"
            className="boton capitalize"
            onClick={() => jugar(opcion)}
          >
            {opcion}
          </button>
        ))}
      </div>
      <p className="text-sm text-tinta">
        Tú {yo} · Payaso {payaso}
      </p>
      {mensaje ? <p className="text-sm text-apagado">{mensaje}</p> : null}
    </div>
  );
}

export default function Minijuego({ tipo, tokens, onCompletar }) {
  const [error, setError] = useState("");

  async function comprobar(payload) {
    setError("");
    const resultado = await onCompletar(payload);
    if (!resultado.ok) {
      setError(resultado.mensaje || "Casi... inténtelo otra vez.");
    }
    return resultado.ok;
  }

  const juego = useMemo(() => {
    if (tipo === "ordenar") return <Ordenar tokens={tokens || []} comprobar={comprobar} />;
    if (tipo === "paciencia") return <Paciencia comprobar={comprobar} />;
    if (tipo === "simon") return <Simon comprobar={comprobar} />;
    return <PPT comprobar={comprobar} />;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tipo, tokens]);

  return (
    <div className="space-y-3 rounded-xl border border-borde bg-grafito p-3">
      <p className="text-xs font-semibold text-acento-suave">
        Minijuego · {ETIQUETAS[tipo] || tipo}
      </p>
      {juego}
      {error ? <p className="text-sm text-peligro">{error}</p> : null}
    </div>
  );
}
