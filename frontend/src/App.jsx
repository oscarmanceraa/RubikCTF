import { Route, Routes } from "react-router-dom";

import BarraNavegacion from "./componentes/BarraNavegacion.jsx";
import RutaProtegida from "./componentes/RutaProtegida.jsx";
import Clasificacion from "./paginas/Clasificacion.jsx";
import DetalleReto from "./paginas/DetalleReto.jsx";
import Inicio from "./paginas/Inicio.jsx";
import IniciarSesion from "./paginas/IniciarSesion.jsx";
import NoEncontrado from "./paginas/NoEncontrado.jsx";
import Panel from "./paginas/Panel.jsx";
import Perfil from "./paginas/Perfil.jsx";
import Registro from "./paginas/Registro.jsx";
import Retos from "./paginas/Retos.jsx";

export default function App() {
  return (
    <div className="flex min-h-full flex-col">
      <BarraNavegacion />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/iniciar-sesion" element={<IniciarSesion />} />
          <Route path="/registro" element={<Registro />} />

          <Route
            path="/panel"
            element={
              <RutaProtegida>
                <Panel />
              </RutaProtegida>
            }
          />
          <Route
            path="/retos"
            element={
              <RutaProtegida>
                <Retos />
              </RutaProtegida>
            }
          />
          <Route
            path="/retos/:slug"
            element={
              <RutaProtegida>
                <DetalleReto />
              </RutaProtegida>
            }
          />
          <Route
            path="/perfil"
            element={
              <RutaProtegida>
                <Perfil />
              </RutaProtegida>
            }
          />
          <Route
            path="/clasificacion"
            element={
              <RutaProtegida>
                <Clasificacion />
              </RutaProtegida>
            }
          />

          <Route path="*" element={<NoEncontrado />} />
        </Routes>
      </main>
    </div>
  );
}
