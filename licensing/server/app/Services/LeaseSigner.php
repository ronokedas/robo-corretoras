<?php

namespace App\Services;

use App\Models\License;
use RuntimeException;

class LeaseSigner
{
    private function decode(string $value): string
    {
        return sodium_base642bin($value, SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING);
    }

    private function encode(string $value): string
    {
        return sodium_bin2base64($value, SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING);
    }

    public function signedResponse(License $license): array
    {
        $private = config('services.licensing.private_key');
        if (!$private) {
            throw new RuntimeException('LICENSE_PRIVATE_KEY não configurada.');
        }
        $release = \App\Models\Release::query()->where('active', true)->latest('id')->first();
        $payload = [
            'license_id' => $license->id,
            'device_hash' => $license->device_hash,
            'issued_at' => now('UTC')->toIso8601String(),
            'expires_at' => $license->expires_at->utc()->toIso8601String(),
            'lease_expires_at' => $license->lease_expires_at->utc()->toIso8601String(),
            'minimum_version' => $release?->minimum_version ?? '1.0.0',
        ];
        return $this->signPayload($payload);
    }

    public function signPayload(array $payload): array
    {
        $private = config('services.licensing.private_key');
        if (!$private) {
            throw new RuntimeException('LICENSE_PRIVATE_KEY não configurada.');
        }
        $json = json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
        return [
            'payload' => $this->encode($json),
            'signature' => $this->encode(
                sodium_crypto_sign_detached($json, $this->decode($private))
            ),
        ];
    }
}
