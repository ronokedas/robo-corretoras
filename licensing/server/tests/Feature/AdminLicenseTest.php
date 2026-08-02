<?php

namespace Tests\Feature;

use App\Models\Customer;
use App\Models\License;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class AdminLicenseTest extends TestCase
{
    use RefreshDatabase;

    private function admin(bool $mustChange = false): User
    {
        return User::factory()->create(['must_change_password' => $mustChange]);
    }

    public function test_admin_creates_an_evepulse_key_and_only_hash_is_persisted(): void
    {
        $response = $this->actingAs($this->admin())->post('/admin/licenses', [
            'name' => 'Cliente Teste',
            'phone' => '11999999999',
            'email' => 'cliente@example.com',
            'days' => 30,
        ]);

        $response->assertRedirect('/admin/licenses');
        $plain = session('plain_key');
        $this->assertMatchesRegularExpression('/^EVP1-[0-9A-HJKMNP-TV-Z]{5}(?:-[0-9A-HJKMNP-TV-Z]{5}){3}$/', $plain);
        $license = License::firstOrFail();
        $this->assertSame(hash('sha256', $plain), $license->key_hash);
        $this->assertStringNotContainsString(substr($plain, 5, 5), $license->key_hint);
        $this->assertDatabaseHas('customers', ['name' => 'Cliente Teste', 'phone' => '11999999999']);
    }

    public function test_active_counter_excludes_expired_and_suspended_licenses(): void
    {
        $customer = Customer::create(['name' => 'Cliente']);
        License::create(['customer_id' => $customer->id, 'key_hash' => hash('sha256', 'A'), 'key_hint' => 'EVP1-*****-A', 'status' => 'ACTIVE', 'expires_at' => now()->addDays(10)]);
        License::create(['customer_id' => $customer->id, 'key_hash' => hash('sha256', 'B'), 'key_hint' => 'EVP1-*****-B', 'status' => 'ACTIVE', 'expires_at' => now()->subDay()]);
        License::create(['customer_id' => $customer->id, 'key_hash' => hash('sha256', 'C'), 'key_hint' => 'EVP1-*****-C', 'status' => 'SUSPENDED', 'expires_at' => now()->addDays(10)]);

        $this->actingAs($this->admin())->get('/admin/licenses')
            ->assertOk()
            ->assertViewHas('active', 1)
            ->assertViewHas('expired', 1)
            ->assertViewHas('suspended', 1);
    }

    public function test_renewal_starts_from_now_when_license_is_expired(): void
    {
        $customer = Customer::create(['name' => 'Cliente']);
        $license = License::create(['customer_id' => $customer->id, 'key_hash' => hash('sha256', 'D'), 'key_hint' => 'EVP1-*****-D', 'status' => 'ACTIVE', 'expires_at' => now()->subDay()]);
        $this->actingAs($this->admin())->post("/admin/licenses/{$license->id}/renew", ['days' => 30])->assertRedirect();
        $this->assertTrue($license->fresh()->expires_at->between(now()->addDays(29), now()->addDays(31)));
    }

    public function test_temporary_password_must_be_changed_before_admin_access(): void
    {
        $admin = $this->admin(true);
        $this->actingAs($admin)->get('/admin/licenses')->assertRedirect('/change-password');
    }

    public function test_password_change_clears_first_login_requirement(): void
    {
        $admin = User::factory()->create([
            'password' => Hash::make('TemporaryPass123!'),
            'must_change_password' => true,
        ]);
        $this->actingAs($admin)->post('/change-password', [
            'current_password' => 'TemporaryPass123!',
            'password' => 'A-New-Secure-Pass-123!',
            'password_confirmation' => 'A-New-Secure-Pass-123!',
        ])->assertRedirect('/admin/licenses');
        $this->assertFalse($admin->fresh()->must_change_password);
    }
}
