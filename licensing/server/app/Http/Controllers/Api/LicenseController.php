<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\AuditEvent;
use App\Models\License;
use App\Services\LeaseSigner;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

class LicenseController extends Controller
{
    public function activate(Request $request, LeaseSigner $signer): JsonResponse
    {
        $data = $request->validate([
            'key' => ['required', 'string', 'max:64'],
            'device_hash' => ['required', 'regex:/^[a-f0-9]{64}$/'],
            'device_name' => ['required', 'string', 'max:100'],
            'install_id' => ['required', 'uuid'],
            'app_version' => ['required', 'string', 'max:32'],
        ]);

        $plainToken = null;
        $license = DB::transaction(function () use ($data, $request, &$plainToken) {
            $license = License::query()
                ->where('key_hash', hash('sha256', strtoupper(trim($data['key']))))
                ->lockForUpdate()
                ->first();
            abort_unless($license, 404, 'Chave de ativação inválida.');
            $this->assertUsable($license);

            if ($license->device_hash && !hash_equals($license->device_hash, $data['device_hash'])) {
                abort(409, 'Esta chave já está vinculada a outro computador.');
            }
            if ($license->lease_expires_at?->isFuture()
                && $license->active_install_id
                && $license->active_install_id !== $data['install_id']) {
                abort(409, 'A chave já está em uso em outra instância.');
            }

            $plainToken = Str::random(64);
            $license->fill([
                'device_hash' => $data['device_hash'],
                'device_name' => $data['device_name'],
                'bound_at' => $license->bound_at ?? now(),
                'activation_token_hash' => hash('sha256', $plainToken),
                'active_install_id' => $data['install_id'],
                'lease_expires_at' => now()->addMinutes(config('services.licensing.lease_minutes')),
                'last_heartbeat_at' => now(),
                'last_ip' => $request->ip(),
                'app_version' => $data['app_version'],
            ])->save();
            $this->audit($license, 'LICENSE_ACTIVATED', $request);
            return $license->fresh();
        });

        return response()->json([
            ...$signer->signedResponse($license),
            'activation_token' => $plainToken,
            'key_hint' => $license->key_hint,
        ]);
    }

    public function heartbeat(Request $request, LeaseSigner $signer): JsonResponse
    {
        $data = $request->validate([
            'activation_token' => ['required', 'string', 'size:64'],
            'device_hash' => ['required', 'regex:/^[a-f0-9]{64}$/'],
            'install_id' => ['required', 'uuid'],
            'app_version' => ['required', 'string', 'max:32'],
        ]);
        $license = DB::transaction(function () use ($data, $request) {
            $license = License::query()
                ->where('activation_token_hash', hash('sha256', $data['activation_token']))
                ->lockForUpdate()
                ->first();
            abort_unless($license, 401, 'Sessão de licença inválida.');
            $this->assertUsable($license);
            abort_unless(hash_equals($license->device_hash, $data['device_hash']), 409, 'Computador não autorizado.');
            abort_unless($license->active_install_id === $data['install_id'], 409, 'Instância não autorizada.');
            $license->update([
                'lease_expires_at' => now()->addMinutes(config('services.licensing.lease_minutes')),
                'last_heartbeat_at' => now(),
                'last_ip' => $request->ip(),
                'app_version' => $data['app_version'],
            ]);
            return $license->fresh();
        });
        return response()->json($signer->signedResponse($license));
    }

    public function deactivate(Request $request): JsonResponse
    {
        $data = $request->validate(['activation_token' => ['required', 'string', 'size:64']]);
        License::query()
            ->where('activation_token_hash', hash('sha256', $data['activation_token']))
            ->update(['activation_token_hash' => null, 'active_install_id' => null, 'lease_expires_at' => null]);
        return response()->json(['ok' => true]);
    }

    private function assertUsable(License $license): void
    {
        abort_unless($license->status === 'ACTIVE', 403, 'Licença suspensa ou revogada.');
        abort_if($license->expires_at->isPast(), 403, 'Licença vencida.');
    }

    private function audit(License $license, string $type, Request $request): void
    {
        AuditEvent::create([
            'license_id' => $license->id,
            'event_type' => $type,
            'context' => ['device_name' => $license->device_name],
            'ip_address' => $request->ip(),
            'created_at' => now(),
        ]);
    }
}
