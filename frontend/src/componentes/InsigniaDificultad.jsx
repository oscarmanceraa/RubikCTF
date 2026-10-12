const ESTILOS = {
  facil: "border-[#2ecc71]/40 text-[#2ecc71]",
  media: "border-acento/45 text-acento-suave",
  dificil: "border-aviso/45 text-aviso",
  experto: "border-peligro/45 text-peligro",
};

export default function InsigniaDificultad({ dificultad, etiqueta }) {
  const clase = ESTILOS[dificultad] || "border-borde text-apagado";
  return (
    <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${clase}`}>
      {etiqueta || dificultad}
    </span>
  );
}
