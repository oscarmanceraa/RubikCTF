// Motor del cubo en el cliente: solo posiciones y normales de los stickers.
// Debe producir el mismo resultado que backend/apps/retos/cube_engine.py.

export const CARAS = ["U", "R", "F", "D", "L", "B"];
export const SUFIJOS = ["", "'", "2"];

export const EJE_CARA = {
  U: ["y", 1],
  D: ["y", -1],
  R: ["x", 1],
  L: ["x", -1],
  F: ["z", 1],
  B: ["z", -1],
};

const INDICE_EJE = { x: 0, y: 1, z: 2 };

const CARA_POR_NORMAL = {
  "1,0,0": "R",
  "-1,0,0": "L",
  "0,1,0": "U",
  "0,-1,0": "D",
  "0,0,1": "F",
  "0,0,-1": "B",
};

// Colores tematicos: cara -> color.
export const COLORES_CARA = {
  U: "#f2f2f2", // blanco  -> OSINT / Esteganografia
  D: "#ffd23f", // amarillo -> Forense
  F: "#2ecc71", // verde    -> Web
  B: "#2f80ed", // azul     -> Redes
  R: "#ff3b3b", // rojo     -> Criptografia
  L: "#ff8c1a", // naranja  -> Reversing
};

export function parsearMovimiento(movimiento) {
  const cara = movimiento[0].toUpperCase();
  const sufijo = movimiento.slice(1);
  if (!EJE_CARA[cara] || !SUFIJOS.includes(sufijo)) {
    throw new Error(`Movimiento invalido: ${movimiento}`);
  }
  return { cara, sufijo };
}

export function anguloMovimiento(cara, sufijo) {
  const signo = EJE_CARA[cara][1];
  const base = signo > 0 ? -90 : 90;
  if (sufijo === "'") return -base;
  if (sufijo === "2") return 180;
  return base;
}

export function radianes(grados) {
  return (grados * Math.PI) / 180;
}

export function matrizRotacion(eje, grados) {
  const r = (grados * Math.PI) / 180;
  const c = Math.round(Math.cos(r));
  const s = Math.round(Math.sin(r));
  if (eje === "x") return [[1, 0, 0], [0, c, -s], [0, s, c]];
  if (eje === "y") return [[c, 0, s], [0, 1, 0], [-s, 0, c]];
  return [[c, -s, 0], [s, c, 0], [0, 0, 1]];
}

export function rotarVector(matriz, vector) {
  return [
    matriz[0][0] * vector[0] + matriz[0][1] * vector[1] + matriz[0][2] * vector[2],
    matriz[1][0] * vector[0] + matriz[1][1] * vector[1] + matriz[1][2] * vector[2],
    matriz[2][0] * vector[0] + matriz[2][1] * vector[1] + matriz[2][2] * vector[2],
  ];
}

export function crearStickers() {
  const stickers = [];
  let id = 0;
  for (let x = -1; x <= 1; x += 1) {
    for (let y = -1; y <= 1; y += 1) {
      for (let z = -1; z <= 1; z += 1) {
        if (x === 0 && y === 0 && z === 0) continue;
        const normales = [
          [x, 0, 0],
          [0, y, 0],
          [0, 0, z],
        ].filter((normal) => normal[0] !== 0 || normal[1] !== 0 || normal[2] !== 0);
        for (const normal of normales) {
          stickers.push({
            id: id++,
            color: CARA_POR_NORMAL[normal.join(",")],
            posicion: [x, y, z],
            normal: [...normal],
          });
        }
      }
    }
  }
  return stickers;
}

export function aplicarMovimiento(stickers, movimiento) {
  const { cara, sufijo } = parsearMovimiento(movimiento);
  const [eje, signo] = EJE_CARA[cara];
  const rotacion = matrizRotacion(eje, anguloMovimiento(cara, sufijo));
  const indice = INDICE_EJE[eje];
  for (const sticker of stickers) {
    if (sticker.posicion[indice] === signo) {
      sticker.posicion = rotarVector(rotacion, sticker.posicion);
      sticker.normal = rotarVector(rotacion, sticker.normal);
    }
  }
}

export function indiceEje(eje) {
  return INDICE_EJE[eje];
}
