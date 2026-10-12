import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, RoundedBox } from "@react-three/drei";
import { useCallback, useEffect, useRef, useState } from "react";

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

const DURACION_MOVIMIENTO = 0.35;
const SEPARACION = 1.0;
const OFFSET_STICKER = 0.5 + 0.02;

const ROTACION_NORMAL = {
  "0,0,1": [0, 0, 0],
  "0,0,-1": [0, Math.PI, 0],
  "1,0,0": [0, Math.PI / 2, 0],
  "-1,0,0": [0, -Math.PI / 2, 0],
  "0,1,0": [-Math.PI / 2, 0, 0],
  "0,-1,0": [Math.PI / 2, 0, 0],
};

function Sticker({ sticker }) {
  const [px, py, pz] = sticker.posicion;
  const [nx, ny, nz] = sticker.normal;
  const posicion = [
    px * SEPARACION + nx * OFFSET_STICKER,
    py * SEPARACION + ny * OFFSET_STICKER,
    pz * SEPARACION + nz * OFFSET_STICKER,
  ];
  const rotacion = ROTACION_NORMAL[`${nx},${ny},${nz}`];

  return (
    <RoundedBox
      args={[0.92, 0.92, 0.08]}
      radius={0.06}
      smoothness={3}
      position={posicion}
      rotation={rotacion}
    >
      <meshStandardMaterial
        color={COLORES_CARA[sticker.color]}
        roughness={0.35}
        metalness={0.15}
      />
    </RoundedBox>
  );
}

function Escena({ stickers, movimiento, grupoRef, alTerminar, autoRotar }) {
  const progreso = useRef(0);
  const movimientoRef = useRef(movimiento);

  useEffect(() => {
    progreso.current = 0;
    movimientoRef.current = movimiento;
  }, [movimiento]);

  useFrame((_, delta) => {
    const actual = movimientoRef.current;
    if (!actual || !grupoRef.current) return;

    progreso.current = Math.min(1, progreso.current + delta / DURACION_MOVIMIENTO);
    grupoRef.current.rotation.set(0, 0, 0);
    grupoRef.current.rotation[actual.eje] = actual.angulo * progreso.current;

    if (progreso.current >= 1) {
      movimientoRef.current = null;
      alTerminar(actual);
    }
  });

  const indice = movimiento ? indiceEje(movimiento.eje) : -1;
  const esMovil = (sticker) =>
    movimiento != null && sticker.posicion[indice] === movimiento.signo;

  const moviles = stickers.filter(esMovil);
  const estaticos = stickers.filter((sticker) => !esMovil(sticker));

  return (
    <>
      <ambientLight intensity={0.7} />
      <directionalLight position={[6, 8, 6]} intensity={1.1} />
      <directionalLight position={[-6, -4, -6]} intensity={0.4} />

      <group scale={1.02}>
        <RoundedBox args={[3.06, 3.06, 3.06]} radius={0.12} smoothness={4}>
          <meshStandardMaterial color="#0a0e14" roughness={0.85} metalness={0.2} />
        </RoundedBox>

        {estaticos.map((sticker) => (
          <Sticker key={sticker.id} sticker={sticker} />
        ))}

        <group ref={grupoRef}>
          {moviles.map((sticker) => (
            <Sticker key={sticker.id} sticker={sticker} />
          ))}
        </group>
      </group>

      <OrbitControls
        enablePan={false}
        enableZoom={!autoRotar}
        autoRotate={autoRotar}
        autoRotateSpeed={0.9}
        minDistance={5}
        maxDistance={14}
        rotateSpeed={0.6}
      />
    </>
  );
}

export default function CuboRubik({
  inicial = [],
  movimientos = [],
  autoRotar = false,
  className = "panel aspect-square w-full overflow-hidden",
  pie = true,
}) {
  const stickersRef = useRef(null);
  if (stickersRef.current === null) {
    stickersRef.current = crearStickers();
  }

  const grupoRef = useRef(null);
  const colaRef = useRef([]);
  const encoladosRef = useRef(0);

  const [version, setVersion] = useState(0);
  const [movimiento, setMovimiento] = useState(null);

  // El desorden de partida como texto, para detectar cambios de forma estable.
  const claveInicial = (inicial || []).join(" ");

  // (Re)construye el cubo desde cero y aplica el estado inicial sin animar.
  // Se dispara cuando llega/ cambia el estado inicial (p. ej. tras el fetch).
  useEffect(() => {
    stickersRef.current = crearStickers();
    colaRef.current = [];
    encoladosRef.current = 0;
    setMovimiento(null);
    for (const notacion of inicial || []) {
      aplicarMovimiento(stickersRef.current, notacion);
    }
    setVersion((valor) => valor + 1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [claveInicial]);

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

  // Movimientos nuevos: encolarlos para animarlos.
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

  return (
    <div className={className}>
      <Canvas camera={{ position: [4.5, 4, 6], fov: 40 }} dpr={[1, 2]}>
        <color attach="background" args={["#141020"]} />
        <Escena
          stickers={stickersRef.current}
          movimiento={movimiento}
          grupoRef={grupoRef}
          alTerminar={alTerminar}
          autoRotar={autoRotar}
        />
      </Canvas>
      {pie ? (
        <p className="border-t border-borde px-4 py-2 text-center text-xs text-apagado">
          Arrastra para mover la vista. Los giros los aplica el sistema al resolver retos.
        </p>
      ) : null}
    </div>
  );
}
