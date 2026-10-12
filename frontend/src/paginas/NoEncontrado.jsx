import { Link } from "react-router-dom";

export default function NoEncontrado() {
  return (
    <section className="mx-auto max-w-xl px-4 py-28 text-center">
      <p className="text-6xl font-bold tracking-tight text-acento-suave">404</p>
      <p className="mt-4 text-apagado">La página que buscas no existe.</p>
      <Link to="/" className="boton-primario mt-8">
        Volver al inicio
      </Link>
    </section>
  );
}
