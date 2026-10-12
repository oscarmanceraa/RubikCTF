import { Navigate, useLocation } from "react-router-dom";

import { useAutenticacion } from "../contexto/ContextoAutenticacion.jsx";

export default function RutaProtegida({ children }) {
  const { usuario, cargando } = useAutenticacion();
  const ubicacion = useLocation();

  if (cargando) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-apagado">
        Cargando…
      </div>
    );
  }

  if (!usuario) {
    return <Navigate to="/iniciar-sesion" replace state={{ desde: ubicacion.pathname }} />;
  }

  return children;
}
