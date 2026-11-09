import { NavLink } from "react-router-dom";

import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

const enlaces = [
  { a: "/panel", texto: "Panel" },
  { a: "/retos", texto: "Retos" },
  { a: "/clasificacion", texto: "Clasificación" },
  { a: "/perfil", texto: "Perfil" },
];

function claseEnlace({ isActive }) {
  return [
    "border-b-[3px] py-2 text-sm transition-colors",
    isActive
      ? "border-cube-yellow text-cube-white"
      : "border-transparent text-muted hover:text-cube-white",
  ].join(" ");
}

export default function BarraNavegacion() {
  const { usuario, cerrarSesion } = useAutenticacion();

  return (
    <header className="sticky top-0 z-20 h-[72px] border-b border-line bg-surface shadow-[0_4px_20px_rgba(0,0,0,0.45)]">
      <nav className="mx-auto flex h-full max-w-page items-center justify-between gap-4 px-4 md:px-6">
        <NavLink to="/" className="flex items-center gap-2.5">
          <span className="grid h-9 w-9 grid-cols-3 gap-0.5 rounded-sm bg-surface-body p-0.5">
            <span className="rounded-[2px] bg-cube-red" />
            <span className="rounded-[2px] bg-cube-white" />
            <span className="rounded-[2px] bg-cube-blue" />
            <span className="rounded-[2px] bg-cube-orange" />
            <span className="rounded-[2px] bg-cube-yellow" />
            <span className="rounded-[2px] bg-cube-green" />
            <span className="rounded-[2px] bg-cube-blue" />
            <span className="rounded-[2px] bg-cube-red" />
            <span className="rounded-[2px] bg-cube-white" />
          </span>
          <span className="text-[15px] font-bold tracking-tight text-cube-white">
            RubikCTF
          </span>
        </NavLink>

        <div className="flex items-center gap-6">
          {usuario ? (
            <>
              <nav className="flex items-center gap-6">
                {enlaces.map((enlace) => (
                  <NavLink key={enlace.a} to={enlace.a} className={claseEnlace}>
                    {enlace.texto}
                  </NavLink>
                ))}
              </nav>
              <div className="flex items-center gap-3">
                <span className="rounded-full border border-line px-3 py-1.5 text-sm text-cube-white">
                  {usuario.nombre_visible || usuario.usuario}
                  <span className="ml-2 font-semibold text-cube-yellow">
                    {usuario.puntuacion} pts
                  </span>
                </span>
                <button className="boton ml-1" onClick={cerrarSesion}>
                  Salir
                </button>
              </div>
            </>
          ) : (
            <>
              <NavLink to="/iniciar-sesion" className={claseEnlace}>
                Entrar
              </NavLink>
              <NavLink to="/registro" className="boton-primario">
                Crear cuenta
              </NavLink>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
