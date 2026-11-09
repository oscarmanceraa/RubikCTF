import { Link } from "react-router-dom";

import CuboRubik from "../componentes/CuboRubikLazy.jsx";
import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

const CATEGORIAS = [
  { nombre: "Web", cara: "F", color: "#009b48", texto: "#ffffff" },
  { nombre: "Criptografía", cara: "R", color: "#b71234", texto: "#ffffff" },
  { nombre: "Redes", cara: "B", color: "#0046ad", texto: "#ffffff" },
  { nombre: "Forense", cara: "D", color: "#ffd500", texto: "#0d0d0f" },
  { nombre: "Reversing", cara: "L", color: "#ff5800", texto: "#0d0d0f" },
  { nombre: "OSINT y esteganografía", cara: "U", color: "#ffffff", texto: "#0d0d0f" },
];

const DESORDEN_DEMO = ["R", "U", "F'", "R2", "L", "D'", "B"];

export default function Inicio() {
  const { usuario } = useAutenticacion();

  return (
    <section className="relative pt-8 pb-16 md:pt-12 md:pb-24">
      <div className="mx-auto w-full max-w-page px-4 md:px-6">
        <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <h1 className="text-4xl font-bold leading-[1.05] tracking-tight text-cube-white md:text-6xl">
              Resuelve retos y el cubo se mueve solo.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
              RubikCTF es un Capture The Flag para aprender ciberseguridad. Cada flag
              correcta suma puntos y gira una cara del cubo. No se toca a mano: se gana.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              {usuario ? (
                <>
                  <Link to="/retos" className="boton-primario">
                    Ver retos
                  </Link>
                  <Link to="/panel" className="boton">
                    Mi panel
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/registro" className="boton-primario">
                    Crear cuenta
                  </Link>
                  <Link to="/iniciar-sesion" className="boton">
                    Entrar
                  </Link>
                </>
              )}
            </div>
          </div>

          <CuboRubik inicial={DESORDEN_DEMO} pie={false} className="aspect-square w-full" />
        </div>

        <div className="mt-16 border-t border-line pt-8">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted">
            Seis categorías, un color del cubo para cada una.
          </h2>
          <ul className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {CATEGORIAS.map((categoria) => (
              <li
                key={categoria.nombre}
                className="flex items-center gap-3 rounded-md border border-line bg-surface px-4 py-3 transition-colors hover:bg-surface-elevated"
              >
                <span
                  className="grid h-9 w-9 shrink-0 place-items-center rounded-[3px] font-mono text-sm font-bold shadow-[inset_0_0_0_1px_rgba(0,0,0,0.15)]"
                  style={{ backgroundColor: categoria.color, color: categoria.texto }}
                >
                  {categoria.cara}
                </span>
                <span className="text-sm text-cube-white">{categoria.nombre}</span>
              </li>
            ))}
          </ul>
        </div>

        <p className="mt-10 text-center text-xs text-muted">
          Desarrollado por{" "}
          <span className="text-cube-white">Oscar Mancera</span>,{" "}
          <span className="text-cube-white">Miguel Munar</span> y{" "}
          <span className="text-cube-white">Diego Vacca</span>
        </p>
      </div>
    </section>
  );
}
