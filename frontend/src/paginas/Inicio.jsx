import { Link } from "react-router-dom";

import CuboRubik from "../componentes/CuboRubikLazy.jsx";
import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

const CATEGORIAS = [
  { nombre: "Web", color: "#2ecc71" },
  { nombre: "Criptografía", color: "#ff4d4d" },
  { nombre: "Redes", color: "#3b82f6" },
  { nombre: "Forense", color: "#ffd23f" },
  { nombre: "Reversing", color: "#ff8c1a" },
  { nombre: "OSINT y esteganografía", color: "#f2f2f2" },
];

const DESORDEN_DEMO = ["R", "U", "F'", "R2", "L", "D'", "B"];

export default function Inicio() {
  const { usuario } = useAutenticacion();

  return (
    <section className="mx-auto max-w-6xl px-4 py-12 md:py-20">
      <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <h1 className="text-4xl font-bold leading-[1.05] tracking-tight md:text-6xl">
            Resuelve retos y el cubo se mueve solo.
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-apagado">
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

        <CuboRubik inicial={DESORDEN_DEMO} autoRotar pie={false} className="aspect-square w-full" />
      </div>

      <div className="mt-16 border-t border-borde pt-8">
        <p className="text-sm text-apagado">
          Seis categorías, un color del cubo para cada una.
        </p>
        <ul className="mt-4 grid gap-x-8 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
          {CATEGORIAS.map((categoria) => (
            <li key={categoria.nombre} className="flex items-center gap-3">
              <span
                className="h-3 w-3 rounded-full"
                style={{ backgroundColor: categoria.color }}
              />
              {categoria.nombre}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
