import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import "@fontsource-variable/space-grotesk";

import App from "./App.jsx";
import { ProveedorAutenticacion } from "./contexto/ContextoAutenticacion.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("raiz")).render(
  <React.StrictMode>
    <BrowserRouter>
      <ProveedorAutenticacion>
        <App />
      </ProveedorAutenticacion>
    </BrowserRouter>
  </React.StrictMode>
);
