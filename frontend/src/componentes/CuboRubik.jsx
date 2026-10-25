import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";

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

// Recursos compartidos (se crean una sola vez).
const GEOMETRIA = new THREE.BoxGeometry(0.92, 0.92, 0.08);
const MATERIAL = new THREE.MeshLambertMaterial();
const ESCALA = new THREE.Vector3(1, 1, 1);
const EJE_VECTOR = {
  x: new THREE.Vector3(1, 0, 0),
  y: new THREE.Vector3(0, 1, 0),
  z: new THREE.Vector3(0, 0, 1),
};

const NORMAL_QUAT = {};
for (const [clave, normal] of Object.entries({
  "0,0,1": [0, 0, 1],
  "0,0,-1": [0, 0, -1],
  "1,0,0": [1, 0, 0],
  "-1,0,0": [-1, 0, 0],
  "0,1,0": [0, 1, 0],
  "0,-1,0": [0, -1, 0],
})) {
  NORMAL_QUAT[clave] = new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(0, 0, 1),
    new THREE.Vector3(...normal)
  );
}

function Escena({ stickers, version, movimiento, alTerminar }) {
  const mallaRef = useRef(null);
  const progreso = useRef(0);
  const movimientoRef = useRef(null);
  const invalidate = useThree((estado) => estado.invalidate);

  const matriz = useMemo(() => new THREE.Matrix4(), []);
  const posicion = useMemo(() => new THREE.Vector3(), []);
  const quaternion = useMemo(() => new THREE.Quaternion(), []);
  const rotacion = useMemo(() => new THREE.Quaternion(), []);

  const actualizar = useCallback(
    (mov, avance) => {
      const malla = mallaRef.current;
      if (!malla) return;

      const indice = mov ? indiceEje(mov.eje) : -1;
      if (mov) {
        rotacion.setFromAxisAngle(EJE_VECTOR[mov.eje], mov.angulo * avance);
      }

      for (let i = 0; i < stickers.length; i += 1) {
        const sticker = stickers[i];
        const n = sticker.normal;
        posicion.set(
          sticker.posicion[0] * SEPARACION + n[0] * OFFSET_STICKER,
          sticker.posicion[1] * SEPARACION + n[1] * OFFSET_STICKER,
          sticker.posicion[2] * SEPARACION + n[2] * OFFSET_STICKER
        );
        quaternion.copy(NORMAL_QUAT[n.join(",")]);

        if (mov && sticker.posicion[indice] === mov.signo) {
          posicion.applyQuaternion(rotacion);
          quaternion.premultiply(rotacion);
        }

        matriz.compose(posicion, quaternion, ESCALA);
        malla.setMatrixAt(i, matriz);
      }
      malla.instanceMatrix.needsUpdate = true;
    },
    [stickers, matriz, posicion, quaternion, rotacion]
  );

  // Colores (una sola vez) y matrices iniciales.
  useLayoutEffect(() => {
    const malla = mallaRef.current;
    if (!malla) return;
    malla.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    for (let i = 0; i < stickers.length; i += 1) {
      malla.setColorAt(i, new THREE.Color(COLORES_CARA[stickers[i].color]));
    }
    if (malla.instanceColor) malla.instanceColor.needsUpdate = true;
    actualizar(null, 0);
    invalidate();
  }, [stickers, actualizar, invalidate]);

  // Recalcular cuando cambia el estado (nuevo movimiento aplicado / reinicio).
  useEffect(() => {
    actualizar(null, 0);
    invalidate();
  }, [version, actualizar, invalidate]);

  // Arrancar la animación cuando llega un movimiento nuevo.
  useEffect(() => {
    progreso.current = 0;
    movimientoRef.current = movimiento;
    if (movimiento) invalidate();
  }, [movimiento, invalidate]);

  useFrame((_, delta) => {
    const mov = movimientoRef.current;
    if (!mov) return;

    progreso.current = Math.min(1, progreso.current + delta / DURACION_MOVIMIENTO);
    actualizar(mov, progreso.current);
    invalidate();

    if (progreso.current >= 1) {
      movimientoRef.current = null;
      alTerminar(mov);
    }
  });

  return (
    <>
      <ambientLight intensity={0.9} />
      <directionalLight position={[5, 7, 6]} intensity={0.75} />
      <directionalLight position={[-6, -4, -6]} intensity={0.35} />

      <instancedMesh
        ref={mallaRef}
        args={[GEOMETRIA, MATERIAL, stickers.length]}
        frustumCulled={false}
        dispose={null}
      />

      <OrbitControls
        enablePan={false}
        enableDamping={false}
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
  className = "panel aspect-square w-full overflow-hidden",
  pie = true,
}) {
  const stickersRef = useRef(null);
  if (stickersRef.current === null) {
    stickersRef.current = crearStickers();
  }

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
      {visible ? (
        <Canvas
          frameloop="demand"
          dpr={1}
          gl={{ antialias: true, powerPreference: "low-power" }}
          camera={{ position: [4.5, 4, 6], fov: 40 }}
        >
          <color attach="background" args={["#141020"]} />
          <Escena
            stickers={stickersRef.current}
            version={version}
            movimiento={movimiento}
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
