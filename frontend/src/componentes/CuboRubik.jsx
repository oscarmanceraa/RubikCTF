import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, RoundedBox } from "@react-three/drei";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  COLORES_CARA,
  EJE_CARA,
  anguloMovimiento,
  aplicarMovimiento,
  crearStickers,
  indiceEje,
  parsearMovimiento,
  radianes,
} from "../cubo/motor.js";

const DURACION_MOVIMIENTO = 0.45;
const SEPARACION = 1.0;
const OFFSET_STICKER = 0.5;

const ROTACION_NORMAL = {
  "0,0,1": [0, 0, 0],
  "0,0,-1": [0, Math.PI, 0],
  "1,0,0": [0, Math.PI / 2, 0],
  "-1,0,0": [0, -Math.PI / 2, 0],
  "0,1,0": [-Math.PI / 2, 0, 0],
  "0,-1,0": [Math.PI / 2, 0, 0],
};

function suavizar(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function agruparCubies(stickers) {
  const mapa = new Map();
  for (const sticker of stickers) {
    const clave = sticker.posicion.join(",");
    let cubie = mapa.get(clave);
    if (!cubie) {
      cubie = { posicion: sticker.posicion, stickers: [] };
      mapa.set(clave, cubie);
    }
    cubie.stickers.push(sticker);
  }
  return [...mapa.values()];
}

function claveCubie(cubie) {
  return cubie.stickers
    .map((sticker) => sticker.id)
    .sort((a, b) => a - b)
    .join("-");
}

function Sticker({ sticker }) {
  const [nx, ny, nz] = sticker.normal;
  return (
    <RoundedBox
      args={[0.9, 0.9, 0.06]}
      radius={0.05}
      smoothness={2}
      position={[nx * OFFSET_STICKER, ny * OFFSET_STICKER, nz * OFFSET_STICKER]}
      rotation={ROTACION_NORMAL[`${nx},${ny},${nz}`]}
    >
      <meshStandardMaterial
        color={COLORES_CARA[sticker.color]}
        roughness={0.35}
        metalness={0.15}
      />
    </RoundedBox>
  );
}

function Cubie({ cubie }) {
  const [x, y, z] = cubie.posicion;
  return (
    <group position={[x * SEPARACION, y * SEPARACION, z * SEPARACION]}>
      <RoundedBox args={[0.97, 0.97, 0.97]} radius={0.06} smoothness={1}>
        <meshStandardMaterial color="#140f22" roughness={0.85} metalness={0.2} />
      </RoundedBox>
      {cubie.stickers.map((sticker) => (
        <Sticker key={sticker.id} sticker={sticker} />
      ))}
    </group>
  );
}

function Escena({ stickers, version, movimiento, grupoRef, alTerminar }) {
  const progreso = useRef(0);
  const movimientoRef = useRef(movimiento);
  const invalidate = useThree((estado) => estado.invalidate);

  useEffect(() => {
    progreso.current = 0;
    movimientoRef.current = movimiento;
    if (grupoRef.current) {
      grupoRef.current.rotation.set(0, 0, 0);
    }
    if (movimiento) invalidate();
  }, [movimiento, invalidate, grupoRef]);

  useEffect(() => {
    invalidate();
  }, [version, invalidate]);

  useFrame((_, delta) => {
    const actual = movimientoRef.current;
    if (!actual || !grupoRef.current) return;

    progreso.current = Math.min(1, progreso.current + delta / DURACION_MOVIMIENTO);
    grupoRef.current.rotation.set(0, 0, 0);
    grupoRef.current.rotation[actual.eje] = actual.angulo * suavizar(progreso.current);
    invalidate();

    if (progreso.current >= 1) {
      movimientoRef.current = null;
      alTerminar(actual);
    }
  });

  const cubies = useMemo(() => agruparCubies(stickers), [stickers, version]);

  const indice = movimiento ? indiceEje(movimiento.eje) : -1;
  const esMovil = (cubie) =>
    movimiento != null && cubie.posicion[indice] === movimiento.signo;

  const moviles = cubies.filter(esMovil);
  const estaticos = cubies.filter((cubie) => !esMovil(cubie));

  return (
    <>
      <ambientLight intensity={0.8} />
      <directionalLight position={[6, 8, 6]} intensity={1.0} />
      <directionalLight position={[-6, -4, -6]} intensity={0.4} />

      <group scale={1.02}>
        {estaticos.map((cubie) => (
          <Cubie key={claveCubie(cubie)} cubie={cubie} />
        ))}
        <group ref={grupoRef}>
          {moviles.map((cubie) => (
            <Cubie key={claveCubie(cubie)} cubie={cubie} />
          ))}
        </group>
      </group>

      <OrbitControls
        enablePan={false}
        enableDamping={false}
        minDistance={5}
        maxDistance={16}
        rotateSpeed={0.6}
      />
    </>
  );
}

export default function CuboRubik({
  inicial = [],
  movimientos = [],
  listo = true,
  className = "panel aspect-square w-full overflow-hidden",
  pie = true,
}) {
  const stickersRef = useRef(null);
  if (stickersRef.current === null && listo) {
    const nuevos = crearStickers();
    for (const notacion of inicial) {
      aplicarMovimiento(nuevos, notacion);
    }
    stickersRef.current = nuevos;
  }

  const grupoRef = useRef(null);
  const colaRef = useRef([]);
  const encoladosRef = useRef(0);

  const [version, setVersion] = useState(0);
  const [movimiento, setMovimiento] = useState(null);
  const [visible, setVisible] = useState(false);
  const contenedorRef = useRef(null);

  const claveInicial = (inicial || []).join(" ");

  const iniciarSiguiente = useCallback(() => {
    const notacion = colaRef.current[0];
    if (!notacion) return;
    const { cara, sufijo } = parsearMovimiento(notacion);
    const [eje, signo] = EJE_CARA[cara];
    setMovimiento({
      notacion,
      cara,
      sufijo,
      eje,
      signo,
      angulo: radianes(anguloMovimiento(cara, sufijo)),
    });
  }, []);

  const alTerminar = useCallback(
    (terminado) => {
      aplicarMovimiento(stickersRef.current, terminado.notacion);
      colaRef.current.shift();
      setVersion((valor) => valor + 1);
      if (colaRef.current.length) {
        iniciarSiguiente();
      } else {
        setMovimiento(null);
      }
    },
    [iniciarSiguiente]
  );

  // (Re)construir el cubo con el estado inicial, sin animar.
  useEffect(() => {
    if (!listo) return;
    const nuevos = crearStickers();
    for (const notacion of inicial || []) {
      aplicarMovimiento(nuevos, notacion);
    }
    stickersRef.current = nuevos;
    colaRef.current = [];
    encoladosRef.current = 0;
    setMovimiento(null);
    setVersion((valor) => valor + 1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [claveInicial, listo]);

  // Encolar movimientos nuevos para animarlos.
  useEffect(() => {
    if (movimientos.length > encoladosRef.current) {
      const nuevas = movimientos.slice(encoladosRef.current);
      encoladosRef.current = movimientos.length;
      colaRef.current.push(...nuevas);
      if (!movimiento && colaRef.current.length) {
        iniciarSiguiente();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [movimientos]);

  // Montar el Canvas solo cuando el cubo esta a la vista.
  useEffect(() => {
    const el = contenedorRef.current;
    if (!el || typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return undefined;
    }
    const observador = new IntersectionObserver(
      (entradas) => {
        entradas.forEach((entrada) => setVisible(entrada.isIntersecting));
      },
      { rootMargin: "250px" }
    );
    observador.observe(el);
    return () => observador.disconnect();
  }, []);

  return (
    <div ref={contenedorRef} className={className}>
      {listo && visible && stickersRef.current ? (
        <Canvas
          frameloop="demand"
          dpr={[1, 2]}
          gl={{ antialias: true }}
          camera={{ position: [4.5, 4, 6], fov: 40 }}
        >
          <color attach="background" args={["#141020"]} />
          <Escena
            stickers={stickersRef.current}
            version={version}
            movimiento={movimiento}
            grupoRef={grupoRef}
            alTerminar={alTerminar}
          />
        </Canvas>
      ) : (
        <div className="flex h-full w-full items-center justify-center text-sm text-apagado">
          Cargando cubo…
        </div>
      )}

      {pie ? (
        <p className="border-t border-borde px-4 py-2 text-center text-xs text-apagado">
          Arrastra para mover la vista. Los giros los aplica el sistema al resolver retos.
        </p>
      ) : null}
    </div>
  );
}
