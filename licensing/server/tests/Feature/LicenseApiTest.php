<?php

namespace Tests\Feature;

use App\Models\Customer;
use App\Models\License;
use App\Services\LeaseSigner;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class LicenseApiTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->app->instance(LeaseSigner::class, new class extends LeaseSigner {
            public function signedResponse(License $license): array
            {
                return ['payload' => 'cGF5bG9hZA', 'signature' => 'c2lnbmF0dXJl'];
            }
        });
    }

    private function createLicense(string $key, int $days = 30): License
    {
        $customer = Customer::create(['name' => 'Cliente '.substr($key, -4)]);
        return License::create([
            'customer_id' => $customer->id,
            'key_hash' => hash('sha256', $key),
            'key_hint' => 'RVV5-****-'.substr($key, -4),
            'status' => 'ACTIVE',
            'expires_at' => now()->addDays($days),
        ]);
    }

    private function activation(string $key, string $device, string $install): array
    {
        return [
            'key' => $key,
            'device_hash' => hash('sha256', $device),
            'device_name' => $device,
            'install_id' => $install,
            'app_version' => '1.0.0',
        ];
    }

    public function test_same_key_is_rejected_on_second_computer(): void
    {
        $key = 'RVV5-AAAA-BBBB-CCCC-DDDD';
        $this->createLicense($key);
        $this->postJson('/api/licenses/activate', $this->activation(
            $key, 'PC-1', '11111111-1111-4111-8111-111111111111'
        ))->assertOk();
        $this->postJson('/api/licenses/activate', $this->activation(
            $key, 'PC-2', '22222222-2222-4222-8222-222222222222'
        ))->assertStatus(409);
    }

    public function test_different_keys_work_from_same_ip(): void
    {
        $keyA = 'RVV5-AAAA-BBBB-CCCC-0001';
        $keyB = 'RVV5-AAAA-BBBB-CCCC-0002';
        $this->createLicense($keyA);
        $this->createLicense($keyB);
        $server = ['REMOTE_ADDR' => '203.0.113.10'];
        $this->withServerVariables($server)->postJson('/api/licenses/activate', $this->activation(
            $keyA, 'PC-A', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
        ))->assertOk();
        $this->withServerVariables($server)->postJson('/api/licenses/activate', $this->activation(
            $keyB, 'PC-B', 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
        ))->assertOk();
    }

    public function test_expired_license_cannot_activate(): void
    {
        $key = 'RVV5-EXPI-RADA-0000-0001';
        $license = $this->createLicense($key);
        $license->update(['expires_at' => now()->subMinute()]);
        $this->postJson('/api/licenses/activate', $this->activation(
            $key, 'PC-1', '11111111-1111-4111-8111-111111111111'
        ))->assertStatus(403);
    }

    public function test_heartbeat_extends_offline_lease_for_72_hours(): void
    {
        config(['services.licensing.lease_minutes' => 4320]);
        $key = 'EVP1-AAAAA-BBBBB-CCCCC-DDDDD';
        $license = $this->createLicense($key);
        $activation = $this->postJson('/api/licenses/activate', $this->activation(
            $key, 'PC-1', '11111111-1111-4111-8111-111111111111'
        ))->assertOk()->json();
        $this->postJson('/api/licenses/heartbeat', [
            'activation_token' => $activation['activation_token'],
            'device_hash' => hash('sha256', 'PC-1'),
            'install_id' => '11111111-1111-4111-8111-111111111111',
            'app_version' => '1.0.0',
        ])->assertOk();
        $this->assertTrue($license->fresh()->lease_expires_at->between(now()->addHours(71), now()->addHours(73)));
    }
}
