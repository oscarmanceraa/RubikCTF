import { Suspense, lazy } from "react";

const CuboRubik = lazy(() => import("./CuboRubik.jsx"));

const CLASE_POR_DEFECTO = "panel aspect-square w-full overflow-hidden";

function Esqueleto({ className }) {
  return (
    <div
      className={`${className || CLASE_POR_DEFECTO} flex items-center justify-center text-sm text-apagado`}
    >
      Cargando cubo…
    </div>
  );
}

export default function CuboRubikLazy(props) {
  return (
    <Suspense fallback={<Esqueleto className={props.className} />}>
      <CuboRubik {...props} />
    </Suspense>
  );
}
