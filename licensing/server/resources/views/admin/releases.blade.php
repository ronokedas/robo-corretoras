@extends('layouts.admin')
@section('content')
<header class="page-head"><div><h2>Versões</h2><p>Publique somente instaladores assinados e verificados.</p></div></header>
<section class="form-panel"><form method="post" action="{{ route('admin.releases.create') }}">@csrf<label>Versão<input name="version" placeholder="1.0.1" required></label><label>Versão mínima<input name="minimum_version" placeholder="1.0.0" required></label><label>URL do instalador<input name="download_url" type="url" required></label><label>SHA-256<input name="sha256" minlength="64" maxlength="64" required></label><label>Assinatura<input name="signature" required></label><button class="primary">PUBLICAR VERSÃO</button></form></section>
<section class="table-wrap"><table><thead><tr><th>Versão</th><th>Mínima</th><th>SHA-256</th><th>Ativa</th></tr></thead><tbody>@forelse($releases as $release)<tr><td>{{ $release->version }}</td><td>{{ $release->minimum_version }}</td><td><code>{{ Str::limit($release->sha256,24) }}</code></td><td>{{ $release->active ? 'Sim' : 'Não' }}</td></tr>@empty<tr><td colspan="4" class="empty">Nenhuma versão publicada.</td></tr>@endforelse</tbody></table></section>
@endsection
