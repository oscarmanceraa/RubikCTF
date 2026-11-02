<?php
$error = "";
$mensaje = "";
$subidos = glob("uploads/*");

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    if (!isset($_FILES["archivo"]) || $_FILES["archivo"]["error"] !== UPLOAD_ERR_OK) {
        $error = "No se ha recibido ningun archivo.";
    } else {
        $nombre = basename($_FILES["archivo"]["name"]);
        $extension = strtolower(pathinfo($nombre, PATHINFO_EXTENSION));

        // Comprobacion debil: solo mira la ULTIMA extension.
        $bloqueadas = ["php", "phtml", "php5", "php7", "phar", "pht"];
        if (in_array($extension, $bloqueadas, true)) {
            $error = "Tipo de archivo no permitido. Sube una imagen o un PDF.";
        } else {
            $destino = "uploads/" . $nombre;
            if (move_uploaded_file($_FILES["archivo"]["tmp_name"], $destino)) {
                $mensaje = "Receta subida correctamente.";
            } else {
                $error = "No se pudo guardar el archivo.";
            }
        }
    }
    $subidos = glob("uploads/*");
}

function h($texto) {
    return htmlspecialchars($texto, ENT_QUOTES, "UTF-8");
}
?>
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Clinica Vita - Mis recetas</title>
  <style>
    :root{--fondo:#071a16;--panel:#0d2a24;--borde:#1e4a40;--texto:#e7f5f0;
      --muted:#8fb8ac;--verde:#34d399;--verde2:#5eead4;}
    *{box-sizing:border-box}
    body{margin:0;min-height:100vh;color:var(--texto);
      font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;
      background:radial-gradient(900px 500px at 100% -10%, rgba(52,211,153,.16), transparent 58%),
                 radial-gradient(700px 500px at 0% 110%, rgba(94,234,212,.08), transparent 55%),
                 var(--fondo);}
    a{color:inherit;text-decoration:none}
    .topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;
      padding:15px 28px;border-bottom:1px solid var(--borde);background:rgba(7,26,22,.85);
      backdrop-filter:blur(8px);position:sticky;top:0}
    .marca{display:flex;align-items:center;gap:11px}
    .logo{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;
      font-weight:800;font-size:17px;color:#06231b;
      background:linear-gradient(135deg,var(--verde2),var(--verde));
      box-shadow:0 8px 22px rgba(52,211,153,.3)}
    .marca strong{display:block;font-size:15px}
    .marca span{display:block;font-size:10px;color:var(--muted);letter-spacing:.16em;text-transform:uppercase}
    nav{display:flex;gap:20px;font-size:14px;color:var(--muted)}
    nav a:hover{color:var(--texto)}
    main{max-width:680px;margin:0 auto;padding:44px 20px 60px}
    .eyebrow{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--verde2);margin:0 0 8px}
    h1{font-size:30px;margin:0 0 8px;letter-spacing:-.5px}
    .lead{color:var(--muted);margin:0 0 24px;line-height:1.55}
    form{background:var(--panel);border:1px solid var(--borde);border-radius:16px;padding:20px;
      display:grid;gap:12px;box-shadow:0 20px 50px rgba(0,0,0,.3)}
    label{font-size:13px;color:#a9d0c4}
    input[type=text],input[type=file]{width:100%;padding:10px 12px;border-radius:10px;
      border:1px solid var(--borde);background:#071a16;color:var(--texto);outline:none}
    button{justify-self:start;padding:10px 20px;border:0;border-radius:10px;font-weight:700;
      color:#06231b;cursor:pointer;background:linear-gradient(135deg,var(--verde2),var(--verde))}
    .aviso{margin-top:16px;padding:12px 14px;border-radius:11px;font-size:14px}
    .ok{border:1px solid #1f5c46;background:#0a1a16;color:#7CF2A8}
    .ko{border:1px solid #5c1f2b;background:#1a0c11;color:#ff9bb0}
    .tarjeta{margin-top:22px;background:var(--panel);border:1px solid var(--borde);
      border-radius:16px;overflow:hidden}
    .tarjeta header{padding:13px 18px;border-bottom:1px solid var(--borde);
      font-size:12px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
    ul{list-style:none;margin:0;padding:0}
    li{padding:13px 18px;border-bottom:1px solid var(--borde);font-size:14px}
    li:last-child{border-bottom:0}
    li a{color:var(--verde2)}
    li a:hover{text-decoration:underline}
    .vacio{padding:20px 18px;color:var(--muted);font-size:14px}
    .nota{margin-top:18px;font-size:12px;color:#5f8a7d;line-height:1.6}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="marca"><div class="logo">CV</div>
      <div><strong>Clinica Vita</strong><span>Portal del paciente</span></div></div>
    <nav><a href="#">Citas</a><a href="#">Resultados</a><a href="#">Mis recetas</a></nav>
  </header>

  <main>
    <p class="eyebrow">Area del paciente</p>
    <h1>Sube tu receta</h1>
    <p class="lead">Adjunta la receta en formato JPG, PNG o PDF. Nuestro equipo la revisara en 24h.</p>

    <form method="post" enctype="multipart/form-data" action="/">
      <div>
        <label>Nombre del paciente</label>
        <input type="text" name="paciente" placeholder="Ana Torres">
      </div>
      <div>
        <label>Archivo de la receta</label>
        <input type="file" name="archivo">
      </div>
      <button type="submit">Subir receta</button>
    </form>

    <?php if ($mensaje): ?><div class="aviso ok"><?= h($mensaje) ?></div><?php endif; ?>
    <?php if ($error): ?><div class="aviso ko"><?= h($error) ?></div><?php endif; ?>

    <div class="tarjeta">
      <header>Recetas subidas</header>
      <?php if ($subidos): ?>
        <ul>
          <?php foreach ($subidos as $f): ?>
            <?php if (is_file($f)): ?>
              <li><a href="<?= h($f) ?>"><?= h(basename($f)) ?></a></li>
            <?php endif; ?>
          <?php endforeach; ?>
        </ul>
      <?php else: ?>
        <p class="vacio">Todavia no has subido ninguna receta.</p>
      <?php endif; ?>
    </div>

    <p class="nota">Por seguridad solo se admiten imagenes y PDF. Los archivos ejecutables
      estan bloqueados.</p>
  </main>
</body>
</html>
