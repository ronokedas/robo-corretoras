<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EvePulse Licenças</title><link rel="stylesheet" href="{{ asset('admin.css') }}"></head>
<body>
<aside>
  <div class="sidebar-brand"><div class="brand-mark">EP</div><h1>EvePulse <span>LICENSE CENTER</span></h1></div>
  <nav><a href="{{ route('admin.licenses') }}">Licenças</a><a href="{{ route('admin.releases') }}">Versões</a></nav>
  <div class="admin-name">{{ auth()->user()->name }}</div>
  <form method="post" action="{{ route('logout') }}">@csrf<button>Sair</button></form>
</aside>
<main>@if(session('success'))<div class="flash">{{ session('success') }}</div>@endif @yield('content')</main>
</body></html>
