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
    "rounded-full px-3 py-1.5 text-sm transition-colors",
    isActive ? "bg-superficie text-tinta" : "text-apagado hover:text-tinta",
  ].join(" ");
}

export default function BarraNavegacion() {
  const { usuario, cerrarSesion } = useAutenticacion();

  return (
    <header className="sticky top-0 z-20 border-b border-borde bg-grafito/85 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <NavLink to="/" className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 grid-cols-2 grid-rows-2 overflow-hidden rounded-[7px]">
            <span className="bg-[#2ecc71]" />
            <span className="bg-[#3b82f6]" />
            <span className="bg-[#ff4d4d]" />
            <span className="bg-[#ffd23f]" />
          </span>
          <span className="text-[15px] font-bold tracking-tight">RubikCTF</span>
        </NavLink>

        <div className="flex flex-wrap items-center gap-1">
          {usuario ? (
            <>
              {enlaces.map((enlace) => (
                <NavLink key={enlace.a} to={enlace.a} className={claseEnlace}>
                  {enlace.texto}
                </NavLink>
              ))}
              <span className="ml-2 rounded-full border border-borde px-3 py-1.5 text-sm text-tinta">
                {usuario.nombre_visible || usuario.usuario}
                <span className="ml-2 font-semibold text-acento-suave">
                  {usuario.puntuacion} pts
                </span>
              </span>
              <button className="boton ml-1" onClick={cerrarSesion}>
                Salir
              </button>
            </>
          ) : (
            <>
              <NavLink to="/iniciar-sesion" className={claseEnlace}>
                Entrar
              </NavLink>
              <NavLink to="/registro" className="boton-primario ml-1">
                Crear cuenta
              </NavLink>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
