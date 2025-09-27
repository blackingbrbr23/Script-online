<?php
session_start();

// Credenciais fixas (mude se quiser)
$USUARIO_OK = 'admin';
$SENHA_OK   = '1234';

// Função simples para escapar texto ao exibir
function h($s) { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }

// Caminho do arquivo de publicação
$arquivo_publicar = __DIR__ . '/publicar.txt';

// ----- Ação: logout -----
if (isset($_GET['acao']) && $_GET['acao'] === 'logout') {
    session_unset();
    session_destroy();
    header("Location: index.html");
    exit;
}

// ----- Ação: login -----
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['acao'] ?? '') === 'login') {
    $usuario = $_POST['usuario'] ?? '';
    $senha   = $_POST['senha'] ?? '';

    if ($usuario === $USUARIO_OK && $senha === $SENHA_OK) {
        $_SESSION['user'] = $usuario;
        // Redireciona para evitar re-submissão do form
        header("Location: painel.php");
        exit;
    } else {
        $erro_login = "Usuário ou senha incorretos.";
    }
}

// ----- Ação: publicar (apenas para usuário logado) -----
if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['acao'] ?? '') === 'publicar') {
    if (empty($_SESSION['user'])) {
        $erro_publicar = "Você precisa estar logado.";
    } else {
        $texto = $_POST['texto'] ?? '';
        // Opcional: pode validar/tampar tamanho aqui
        // Salva o texto no arquivo (substitui)
        if (file_put_contents($arquivo_publicar, $texto) !== false) {
            $sucesso_publicar = "Publicado com sucesso!";
        } else {
            $erro_publicar = "Erro ao salvar a publicação.";
        }
    }
}

// Le o conteúdo atual (se existir)
$conteudo_atual = '';
if (file_exists($arquivo_publicar)) {
    $conteudo_atual = file_get_contents($arquivo_publicar);
}
?>
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Painel - Publicar</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; background:#f5f7fb; margin:0; padding:30px; }
    .wrap { max-width:900px; margin:0 auto; }
    header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
    .card { background:#fff; padding:18px; border-radius:10px; box-shadow:0 6px 20px rgba(0,0,0,0.06); }
    textarea { width:100%; min-height:140px; resize:vertical; padding:10px; border-radius:8px; border:1px solid #ddd; box-sizing:border-box; }
    button { padding:10px 16px; background:#28a745; color:#fff; border:none; border-radius:8px; cursor:pointer; }
    .btn-logout { background:#dc3545; }
    .msg { margin:10px 0; padding:10px; border-radius:8px; }
    .ok { background:#e6ffed; color:#08602a; border:1px solid #b6f0c7; }
    .err { background:#ffecec; color:#9a1c1c; border:1px solid #f2b0b0; }
    pre { white-space:pre-wrap; word-wrap:break-word; background:#f8f9fb; padding:12px; border-radius:8px; border:1px solid #eee; }
    .note { font-size:13px; color:#666; margin-top:8px; }
    .top-links a { text-decoration:none; color:#007bff; margin-left:10px; }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Painel de Publicação</h1>
      <div class="top-links">
        <?php if (!empty($_SESSION['user'])): ?>
          <span>Logado como <strong><?= h($_SESSION['user']) ?></strong></span>
          <a href="painel.php?acao=logout" class="btn-logout" style="padding:8px 12px;background:#dc3545;color:#fff;border-radius:6px;">Sair</a>
        <?php else: ?>
          <a href="index.html">Voltar ao Login</a>
        <?php endif; ?>
      </div>
    </header>

    <?php if (!empty($erro_login)): ?>
      <div class="msg err"><?= h($erro_login) ?></div>
    <?php endif; ?>

    <?php if (empty($_SESSION['user'])): ?>
      <!-- Form de login (caso o usuário acesse painel.php direto) -->
      <div class="card">
        <h2>Entrar</h2>
        <form method="POST">
          <input type="hidden" name="acao" value="login">
          <input type="text" name="usuario" placeholder="Usuário" required style="width:100%;padding:10px;margin:8px 0;border-radius:6px;border:1px solid #ccc;">
          <input type="password" name="senha" placeholder="Senha" required style="width:100%;padding:10px;margin:8px 0;border-radius:6px;border:1px solid #ccc;">
          <button type="submit">Entrar</button>
        </form>
        <p class="note">Credenciais padrão: <strong>admin / 1234</strong></p>
      </div>

    <?php else: ?>
      <!-- Painel de publicação -->
      <div class="card" style="margin-bottom:18px;">
        <h2>Escreva sua publicação</h2>

        <?php if (!empty($sucesso_publicar)): ?>
          <div class="msg ok"><?= h($sucesso_publicar) ?></div>
        <?php endif; ?>
        <?php if (!empty($erro_publicar)): ?>
          <div class="msg err"><?= h($erro_publicar) ?></div>
        <?php endif; ?>

        <form method="POST">
          <input type="hidden" name="acao" value="publicar">
          <textarea name="texto" placeholder="Escreva aqui..." required><?= h($conteudo_atual) ?></textarea>
          <div style="margin-top:10px;">
            <button type="submit">Publicar</button>
            <a href="https://blackingbr.netlify.app/" target="_blank" style="margin-left:12px;text-decoration:none;color:#007bff;">Ver site Netlify</a>
          </div>
        </form>

        <p class="note">Ao publicar, o conteúdo será salvo em <code>/publicar.txt</code> neste servidor (Render). No seu site Netlify, faça um <code>fetch</code> para: <code>https://meu-sitee.onrender.com/publicar.txt</code>.</p>
      </div>

      <!-- Visualizar conteúdo atual -->
      <div class="card">
        <h3>Conteúdo atual salvo</h3>
        <pre><?= h($conteudo_atual !== '' ? $conteudo_atual : 'Nenhum conteúdo publicado ainda.') ?></pre>
      </div>

    <?php endif; ?>
  </div>
</body>
</html>
