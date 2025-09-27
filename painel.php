<?php
// Usuário e senha corretos
$usuarioCorreto = "admin";
$senhaCorreta = "1234";

// Recebe dados do formulário
$usuario = $_POST['usuario'] ?? '';
$senha = $_POST['senha'] ?? '';

// Verifica login
if ($usuario === $usuarioCorreto && $senha === $senhaCorreta) {
    echo "<h1>Bem-vindo ao Painel!</h1>";
} else {
    echo "<h1>Usuário ou senha incorretos!</h1>";
    echo '<a href="login.html">Voltar</a>';
}
?>
