@extends('layouts.admin')
@section('content')
<header class="page-head"><div><h2>Licenças</h2><p>Clientes, validade e computadores autorizados.</p></div><button onclick="document.getElementById('new-license').showModal()" class="primary">+ GERAR CHAVE</button></header>
@if(session('plain_key'))
<div class="key-reveal"><b>Copie agora — esta chave não será mostrada novamente:</b><div class="copy-row"><code id="new-key">{{ session('plain_key') }}</code><button type="button" onclick="navigator.clipboard.writeText(document.getElementById('new-key').textContent);this.textContent='Copiada'">Copiar</button></div></div>
@endif
<section class="metrics"><div><small>Ativas</small><b>{{ $active }}</b></div><div><small>Vencendo em 15 dias</small><b>{{ $expiring }}</b></div><div><small>Expiradas</small><b>{{ $expired }}</b></div><div><small>Suspensas</small><b>{{ $suspended }}</b></div></section>
<section class="table-wrap"><table><thead><tr><th>Cliente</th><th>Contato</th><th>Chave</th><th>Dispositivo</th><th>Validade</th><th>Última conexão</th><th>Estado</th><th>Ações</th></tr></thead><tbody>
@forelse($licenses as $license)
<tr>
  <td><b>{{ $license->customer->name }}</b></td>
  <td>{{ $license->customer->phone ?: '—' }}<small>{{ $license->customer->email ?: 'Sem e-mail' }}</small></td>
  <td><code>{{ $license->key_hint }}</code></td>
  <td>{{ $license->device_name ?: 'Não vinculado' }}<small>{{ $license->app_version ? 'Versão '.$license->app_version : '' }}</small></td>
  <td>{{ $license->expires_at->format('d/m/Y') }}<small>{{ $license->expires_at->isPast() ? 'Expirada' : $license->expires_at->diffForHumans() }}</small></td>
  <td>{{ $license->last_heartbeat_at?->format('d/m/Y H:i') ?: 'Nunca' }}</td>
  <td><span class="tag {{ strtolower($license->status) }}">{{ $license->status }}</span></td>
  <td><details><summary>Gerenciar</summary><div class="actions">
    <form method="post" action="{{ route('admin.licenses.renew',$license) }}">@csrf<input name="days" type="number" value="30" min="1" max="3650"><button>Adicionar dias</button></form>
    <form method="post" action="{{ route('admin.licenses.expires-at',$license) }}">@csrf<input name="expires_at" type="date" min="{{ now()->addDay()->format('Y-m-d') }}" required><button>Definir data</button></form>
    <form method="post" action="{{ route('admin.licenses.status',$license) }}">@csrf<select name="status"><option value="ACTIVE">Ativa</option><option value="SUSPENDED">Suspensa</option><option value="REVOKED">Revogada</option></select><button>Alterar estado</button></form>
    <form method="post" action="{{ route('admin.licenses.reset',$license) }}" onsubmit="return confirm('Liberar o computador desta licença?')">@csrf<button class="danger">Liberar computador</button></form>
    <div class="audit-list"><b>Histórico recente</b>@forelse($license->auditEvents()->latest('id')->limit(4)->get() as $event)<small>{{ $event->created_at->format('d/m H:i') }} · {{ $event->event_type }}</small>@empty<small>Sem eventos</small>@endforelse</div>
  </div></details></td>
</tr>
@empty<tr><td colspan="8" class="empty">Nenhuma licença criada.</td></tr>@endforelse
</tbody></table></section>{{ $licenses->links() }}
<dialog id="new-license"><form method="post" action="{{ route('admin.licenses.create') }}">@csrf<h3>Gerar nova chave</h3><label>Nome do cliente<input name="name" required maxlength="150"></label><label>Telefone<input name="phone" maxlength="32"></label><label>E-mail<input name="email" type="email"></label><label>Validade em dias<input name="days" type="number" value="30" min="1" max="3650" required></label><div class="dialog-actions"><button type="button" onclick="this.closest('dialog').close()">Cancelar</button><button class="primary">GERAR CHAVE</button></div></form></dialog>
@endsection
