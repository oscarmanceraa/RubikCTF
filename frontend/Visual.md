# Guía Tailwind – CTF temática Cubo de Rubik

Complemento de `guia-estilos-ctf-rubik.md`. Traduce la paleta, tipografía y espacios a configuración y clases de Tailwind CSS. Incluye las dos variantes de configuración: **Tailwind v3** (`tailwind.config.js`) y **Tailwind v4** (`@theme` en CSS). Usa la que corresponda a tu proyecto (revisa tu `package.json`).

---

## 1. Fuente Appleberry

Coloca los archivos en `public/fonts/` (o la carpeta de assets de tu framework) y declara el `@font-face` en tu CSS principal (`globals.css`, `app.css`, etc.).

```css
@font-face {
  font-family: "Appleberry";
  src: url("/fonts/Appleberry.woff2") format("woff2"),
       url("/fonts/Appleberry.ttf") format("truetype");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
```

> Verifica la licencia de la fuente antes de publicar. Como Appleberry tiene un solo peso, evita `font-bold` (genera negrita sintética).

---

## 2. Configuración del tema

### 2.1 Tailwind v3 – `tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js,jsx,ts,tsx,vue,svelte}", "./index.html"],
  theme: {
    extend: {
      colors: {
        cube: {
          white: "#FFFFFF",
          yellow: "#FFD500",
          red: "#B71234",
          orange: "#FF5800",
          blue: "#0046AD",
          green: "#009B48",
        },
        surface: {
          body: "#0D0D0F",
          DEFAULT: "#17171B",
          elevated: "#23232A",
        },
        line: "#34343D",
        muted: "#A6A6B3",
      },
      fontFamily: {
        sans: ['"Appleberry"', '"Segoe UI"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', '"Fira Code"', "ui-monospace", "Consolas", "monospace"],
      },
      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "16px",
      },
      maxWidth: {
        page: "1200px",
      },
      boxShadow: {
        focus: "0 0 0 3px rgba(255, 213, 0, 0.25)",
      },
      keyframes: {
        shake: {
          "0%, 100%": { transform: "translateX(0)" },
          "25%": { transform: "translateX(-6px)" },
          "75%": { transform: "translateX(6px)" },
        },
      },
      animation: {
        shake: "shake 300ms ease-in-out",
      },
    },
  },
  plugins: [],
};
```

### 2.2 Tailwind v4 – CSS con `@theme`

```css
@import "tailwindcss";

@theme {
  /* Stickers del cubo */
  --color-cube-white: #FFFFFF;
  --color-cube-yellow: #FFD500;
  --color-cube-red: #B71234;
  --color-cube-orange: #FF5800;
  --color-cube-blue: #0046AD;
  --color-cube-green: #009B48;

  /* Base */
  --color-surface-body: #0D0D0F;
  --color-surface: #17171B;
  --color-surface-elevated: #23232A;
  --color-line: #34343D;
  --color-muted: #A6A6B3;

  /* Tipografía */
  --font-sans: "Appleberry", "Segoe UI", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", ui-monospace, Consolas, monospace;

  /* Radios */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;

  /* Contenedor */
  --container-page: 1200px;

  /* Animación */
  --animate-shake: shake 300ms ease-in-out;
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-6px); }
    75% { transform: translateX(6px); }
  }
}
```

Con ambas variantes quedan disponibles clases como `bg-cube-yellow`, `text-cube-red`, `border-line`, `bg-surface-elevated`, `text-muted`, `font-mono`, `rounded-md`, `max-w-page` y `animate-shake`.

---

## 3. Estilos base

Aplica el fondo oscuro y la tipografía en el `body` (o en el layout raíz).

```html
<body class="bg-surface-body text-cube-white font-sans antialiased">
```

---

## 4. Espacios con la escala por defecto de Tailwind

La escala por defecto de Tailwind ya es de 4 px por unidad, así que **no necesitas configurar nada** para respetar la cuadrícula de 8 px. Equivalencias:

| Token de la guía | Clase Tailwind | Valor |
|---|---|---|
| `--space-1` | `p-1` / `gap-1` | 4 px |
| `--space-2` | `p-2` / `gap-2` | 8 px |
| `--space-3` | `p-4` / `gap-4` | 16 px |
| `--space-4` | `p-6` / `gap-6` | 24 px |
| `--space-5` | `p-8` / `gap-8` | 32 px |
| `--space-6` | `p-12` | 48 px |
| `--space-7` | `p-16` | 64 px |
| `--space-8` | `p-24` | 96 px |

**Regla práctica:** usa únicamente valores pares de la escala (`2, 4, 6, 8, 12, 16, 24`) para mantener múltiplos de 8 px. Evita `p-3`, `p-5`, `p-7` salvo ajustes finos.

---

## 5. Layout

### Contenedor de página

```html
<main class="mx-auto w-full max-w-page px-4 md:px-6">
  ...
</main>
```

### Header

```html
<header class="h-[72px] border-b border-line bg-surface">
  <div class="mx-auto flex h-full max-w-page items-center justify-between px-4 md:px-6">
    <!-- logo cubo -->
    <nav class="flex items-center gap-6">
      <a class="border-b-[3px] border-cube-yellow py-2 text-cube-white" href="#">Retos</a>
      <a class="border-b-[3px] border-transparent py-2 text-muted hover:text-cube-white" href="#">Ranking</a>
    </nav>
  </div>
</header>
```

### Grid de retos (3 / 2 / 1 columnas)

```html
<section class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
  <!-- tarjetas -->
</section>
```

Breakpoints por defecto de Tailwind: `sm` 640 px, `lg` 1024 px, coinciden con la guía.

### Ritmo vertical

- Entre secciones: `py-16` o `py-24`.
- Título → contenido: `mb-6`.
- Entre campos de formulario: `space-y-4`.

---

## 6. Componentes

### 6.1 Tarjeta de reto

```html
<article class="overflow-hidden rounded-md border border-line bg-surface transition
                hover:-translate-y-0.5 hover:border-cube-blue">
  <div class="h-1.5 bg-cube-blue"></div> <!-- franja de categoría -->
  <div class="p-6">
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-[22px] leading-tight">Título del reto</h3>
      <span class="rounded-sm bg-cube-green px-2.5 py-1 text-xs uppercase tracking-wider text-cube-white">
        Fácil
      </span>
    </div>
    <p class="mb-6 text-sm text-muted">Descripción breve del reto.</p>
    <div class="flex items-center justify-between">
      <span class="text-cube-yellow">100 pts</span>
      <button class="rounded-md bg-cube-yellow px-6 py-3 text-surface-body transition hover:bg-cube-orange">
        Abrir
      </button>
    </div>
  </div>
</article>
```

Estado **resuelto**: cambia `hover:border-cube-blue` por `border-cube-green`, la franja a `bg-cube-green` y añade `opacity-80` al contenido.

### 6.2 Colores por categoría y dificultad (importante en Tailwind)

Tailwind **no detecta clases construidas dinámicamente** (por ejemplo `` `bg-cube-${color}` ``). Usa un mapa con los nombres de clase completos:

```js
export const categoryStyles = {
  web:      { bar: "bg-cube-blue",   border: "hover:border-cube-blue" },
  crypto:   { bar: "bg-cube-yellow", border: "hover:border-cube-yellow" },
  forensic: { bar: "bg-cube-green",  border: "hover:border-cube-green" },
  reversing:{ bar: "bg-cube-red",    border: "hover:border-cube-red" },
  misc:     { bar: "bg-cube-orange", border: "hover:border-cube-orange" },
  welcome:  { bar: "bg-cube-white",  border: "hover:border-cube-white" },
};

export const difficultyStyles = {
  easy:   "bg-cube-green text-cube-white",
  medium: "bg-cube-yellow text-surface-body",
  hard:   "bg-cube-orange text-surface-body",
  expert: "bg-cube-red text-cube-white",
};
```

Uso: `<div className={categoryStyles[challenge.category].bar} />`

### 6.3 Botones

```html
<!-- Primario -->
<button class="min-h-11 rounded-md bg-cube-yellow px-6 py-3 text-surface-body transition
               hover:bg-cube-orange focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-cube-yellow/40
               disabled:cursor-not-allowed disabled:bg-surface-elevated disabled:text-muted">
  Enviar
</button>

<!-- Secundario -->
<button class="min-h-11 rounded-md border-2 border-cube-white px-6 py-3 text-cube-white transition
               hover:bg-cube-white hover:text-surface-body">
  Cancelar
</button>

<!-- Éxito -->
<button class="min-h-11 rounded-md bg-cube-green px-6 py-3 text-cube-white transition hover:brightness-90">
  Confirmar
</button>

<!-- Peligro -->
<button class="min-h-11 rounded-md bg-cube-red px-6 py-3 text-cube-white transition hover:brightness-90">
  Eliminar
</button>
```

### 6.4 Campo de flag

```html
<input
  type="text"
  placeholder="CTF{...}"
  class="w-full rounded-sm border-2 border-line bg-surface-elevated px-4 py-3 font-mono text-cube-white
         placeholder:text-muted focus:border-cube-yellow focus:outline-none focus:shadow-focus"
/>
```

Estados (alterna con lógica de tu framework):

- Correcto: `border-cube-green`
- Incorrecto: `border-cube-red animate-shake`

### 6.5 Scoreboard

```html
<table class="w-full border-collapse text-left">
  <thead>
    <tr class="border-b-2 border-cube-yellow text-sm uppercase tracking-wider text-muted">
      <th class="px-4 py-3">#</th>
      <th class="px-4 py-3">Equipo</th>
      <th class="px-4 py-3">Puntos</th>
    </tr>
  </thead>
  <tbody>
    <tr class="odd:bg-surface even:bg-surface-elevated">
      <td class="px-4 py-3 text-cube-yellow">1</td>
      <td class="px-4 py-3">Equipo Alfa</td>
      <td class="px-4 py-3">1500</td>
    </tr>
    <!-- 2.º: text-cube-white · 3.º: text-cube-orange -->
  </tbody>
</table>
```

### 6.6 Formulario de login

```html
<form class="mx-auto w-full max-w-[420px] space-y-4 rounded-lg border border-line bg-surface p-8">
  <label class="block text-sm text-muted">
    Usuario
    <input class="mt-2 w-full rounded-sm border-2 border-line bg-surface-elevated px-4 py-3 text-cube-white
                  focus:border-cube-yellow focus:outline-none focus:shadow-focus" />
  </label>
  <p class="text-sm text-cube-red">Mensaje de error</p>
</form>
```

### 6.7 Modal

```html
<div class="fixed inset-0 flex items-center justify-center bg-surface-body/80 backdrop-blur-sm">
  <div class="w-full max-w-[560px] rounded-lg border border-line bg-surface p-8">
    ...
  </div>
</div>
```

### 6.8 Toast

```html
<div class="rounded-md border border-line border-l-4 border-l-cube-green bg-surface px-4 py-3">
  ¡Flag correcta!
</div>
```

Cambia `border-l-cube-green` por `border-l-cube-red`, `border-l-cube-orange` o `border-l-cube-blue` según el tipo.

---

## 7. Detalles temáticos

### Logo cubo 3×3

```html
<div class="grid h-9 w-9 grid-cols-3 gap-0.5 rounded-sm bg-surface-body p-0.5">
  <span class="rounded-[2px] bg-cube-red"></span>
  <span class="rounded-[2px] bg-cube-white"></span>
  <span class="rounded-[2px] bg-cube-blue"></span>
  <span class="rounded-[2px] bg-cube-orange"></span>
  <span class="rounded-[2px] bg-cube-yellow"></span>
  <span class="rounded-[2px] bg-cube-green"></span>
  <span class="rounded-[2px] bg-cube-blue"></span>
  <span class="rounded-[2px] bg-cube-red"></span>
  <span class="rounded-[2px] bg-cube-white"></span>
</div>
```

### Fondo con patrón de cuadrícula (hero)

```html
<section class="relative bg-surface-body py-24
  [background-image:linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)]
  [background-size:48px_48px]">
  ...
</section>
```

### Movimiento reducido

Usa los modificadores `motion-safe:` y `motion-reduce:` de Tailwind:

```html
<div class="motion-safe:hover:-translate-y-0.5 motion-reduce:transition-none">
```

---

## 8. Accesibilidad con Tailwind

- Foco visible siempre: `focus-visible:ring-[3px] focus-visible:ring-cube-yellow/40`.
- Texto negro (`text-surface-body`) sobre amarillo, naranja y blanco; texto blanco sobre azul, rojo y verde.
- Áreas táctiles mínimas: `min-h-11` (44 px).
- No depender solo del color: acompaña estados con íconos o texto (✓ / ✗).
- Texto mínimo: `text-sm` (14 px).

---

## 9. Checklist

- [ ] Confirmar versión de Tailwind (v3 o v4) y usar su configuración correspondiente.
- [ ] Declarar `@font-face` de Appleberry y verificar la licencia.
- [ ] Añadir colores `cube-*`, `surface-*`, `line` y `muted` al tema.
- [ ] Aplicar `bg-surface-body text-cube-white font-sans` al body.
- [ ] Usar `font-mono` en flags, hashes y bloques de código.
- [ ] Mapas de clases completas para categorías y dificultades (sin concatenar nombres).
- [ ] Grid de retos `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6`.
- [ ] Estados `hover`, `focus-visible`, `disabled` en botones e inputs.
- [ ] Revisar contraste y comportamiento en móvil.