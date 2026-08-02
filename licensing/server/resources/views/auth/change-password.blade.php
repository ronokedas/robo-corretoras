<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trocar senha | EvePulse</title><link rel="stylesheet" href="/admin.css"></head>
<body class="login">
<form method="post" action="{{ route('password.update') }}" class="login-box">
@csrf
<div class="brand-mark">EP</div><h1>Proteja seu painel</h1><p>Troque a senha temporária antes de continuar.</p>
<label>Senha temporária<input name="current_password" type="password" required autofocus></label>
<label>Nova senha<input name="password" type="password" minlength="12" required></label>
<label>Confirmar nova senha<input name="password_confirmation" type="password" minlength="12" required></label>
@foreach($errors->all() as $error)<div class="error">{{ $error }}</div>@endforeach
<button class="primary">SALVAR NOVA SENHA</button>
</form>
</body></html>
