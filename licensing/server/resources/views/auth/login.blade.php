<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin | EvePulse</title><link rel="stylesheet" href="{{ asset('admin.css') }}"></head>
<body class="login">
<form method="post" action="{{ route('login.submit') }}" class="login-box">
@csrf
<div class="brand-mark">EP</div><h1>EvePulse Trader</h1><p>Central de licenças</p>
<label>E-mail<input name="email" type="email" value="{{ old('email') }}" required autofocus></label>
<label>Senha<input name="password" type="password" required></label>
@error('email')<div class="error">{{ $message }}</div>@enderror
<button class="primary">ENTRAR NO PAINEL</button>
</form>
</body></html>
