<?php

namespace App\Http\Controllers;

use App\Models\AuditEvent;
use App\Models\Customer;
use App\Models\License;
use App\Models\Release;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AdminController extends Controller
{
    public function licenses()
    {
        return view('admin.licenses', [
            'licenses' => License::with('customer')->latest()->paginate(50),
            'active' => License::where('status', 'ACTIVE')->where('expires_at', '>', now())->count(),
            'expiring' => License::where('status', 'ACTIVE')->whereBetween('expires_at', [now(), now()->addDays(15)])->count(),
            'expired' => License::where('expires_at', '<=', now())->count(),
            'suspended' => License::where('status', 'SUSPENDED')->count(),
        ]);
    }

    public function createLicense(Request $request)
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:150'],
            'email' => ['nullable', 'email', 'max:255'],
            'phone' => ['nullable', 'string', 'max:32'],
            'days' => ['required', 'integer', 'min:1', 'max:3650'],
        ]);
        [$plain, $license] = DB::transaction(function () use ($data, $request) {
            $customer = Customer::create($data);
            do {
                $alphabet = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
                $raw = '';
                for ($i = 0; $i < 20; $i++) {
                    $raw .= $alphabet[random_int(0, strlen($alphabet) - 1)];
                }
                $plain = 'EVP1-'.implode('-', str_split($raw, 5));
                $hash = hash('sha256', $plain);
            } while (License::where('key_hash', $hash)->exists());

            $license = License::create([
                'customer_id' => $customer->id,
                'key_hash' => $hash,
                'key_hint' => 'EVP1-*****-*****-*****-'.substr($plain, -5),
                'status' => 'ACTIVE',
                'expires_at' => now()->addDays((int) $data['days']),
            ]);
            $this->audit($license, 'LICENSE_CREATED', ['days' => (int) $data['days']], $request);
            return [$plain, $license];
        });
        return redirect()->route('admin.licenses')
            ->with('plain_key', $plain)
            ->with('selected_license', $license->id);
    }

    public function renew(Request $request, License $license)
    {
        $data = $request->validate(['days' => ['required', 'integer', 'min:1', 'max:3650']]);
        $base = $license->expires_at->isFuture() ? $license->expires_at : now();
        $license->update(['expires_at' => $base->copy()->addDays((int) $data['days']), 'status' => 'ACTIVE']);
        $this->audit($license, 'LICENSE_RENEWED', $data, $request);
        return back()->with('success', 'Licença renovada.');
    }

    public function expiresAt(Request $request, License $license)
    {
        $data = $request->validate(['expires_at' => ['required', 'date', 'after:today']]);
        $license->update(['expires_at' => $data['expires_at'].' 23:59:59', 'status' => 'ACTIVE']);
        $this->audit($license, 'LICENSE_EXPIRATION_SET', $data, $request);
        return back()->with('success', 'Data de validade atualizada.');
    }

    public function status(Request $request, License $license)
    {
        $data = $request->validate(['status' => ['required', 'in:ACTIVE,SUSPENDED,REVOKED']]);
        $license->update([
            'status' => $data['status'],
            'activation_token_hash' => $data['status'] === 'ACTIVE' ? $license->activation_token_hash : null,
            'active_install_id' => $data['status'] === 'ACTIVE' ? $license->active_install_id : null,
            'lease_expires_at' => $data['status'] === 'ACTIVE' ? $license->lease_expires_at : null,
        ]);
        $this->audit($license, 'LICENSE_STATUS_CHANGED', $data, $request);
        return back()->with('success', 'Estado atualizado.');
    }

    public function resetDevice(Request $request, License $license)
    {
        $license->update([
            'device_hash' => null,
            'device_name' => null,
            'bound_at' => null,
            'activation_token_hash' => null,
            'active_install_id' => null,
            'lease_expires_at' => null,
        ]);
        $this->audit($license, 'DEVICE_RELEASED', [], $request);
        return back()->with('success', 'Computador liberado.');
    }

    public function releases()
    {
        return view('admin.releases', ['releases' => Release::latest()->get()]);
    }

    public function createRelease(Request $request)
    {
        $data = $request->validate([
            'version' => ['required', 'regex:/^\d+\.\d+\.\d+$/', 'unique:releases'],
            'minimum_version' => ['required', 'regex:/^\d+\.\d+\.\d+$/'],
            'download_url' => ['required', 'url'],
            'sha256' => ['required', 'regex:/^[a-fA-F0-9]{64}$/'],
            'signature' => ['required', 'string'],
        ]);
        Release::query()->update(['active' => false]);
        Release::create([...$data, 'active' => true]);
        return back()->with('success', 'Versão publicada.');
    }

    private function audit(License $license, string $type, array $context, Request $request): void
    {
        AuditEvent::create([
            'user_id' => $request->user()?->id,
            'license_id' => $license->id,
            'event_type' => $type,
            'context' => $context,
            'ip_address' => $request->ip(),
            'created_at' => now(),
        ]);
    }
}
