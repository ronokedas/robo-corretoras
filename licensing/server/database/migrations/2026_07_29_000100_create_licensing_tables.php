<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('customers', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('email')->nullable()->index();
            $table->string('phone', 32)->nullable();
            $table->text('notes')->nullable();
            $table->timestamps();
        });

        Schema::create('licenses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('customer_id')->constrained()->cascadeOnDelete();
            $table->char('key_hash', 64)->unique();
            $table->string('key_hint', 32);
            $table->string('status', 20)->default('ACTIVE')->index();
            $table->timestamp('expires_at')->index();
            $table->char('device_hash', 64)->nullable()->index();
            $table->string('device_name', 100)->nullable();
            $table->timestamp('bound_at')->nullable();
            $table->char('activation_token_hash', 64)->nullable()->unique();
            $table->uuid('active_install_id')->nullable();
            $table->timestamp('lease_expires_at')->nullable()->index();
            $table->timestamp('last_heartbeat_at')->nullable();
            $table->string('last_ip', 64)->nullable();
            $table->string('app_version', 32)->nullable();
            $table->timestamps();
        });

        Schema::create('releases', function (Blueprint $table) {
            $table->id();
            $table->string('version', 32)->unique();
            $table->string('minimum_version', 32);
            $table->text('download_url');
            $table->char('sha256', 64);
            $table->text('signature');
            $table->boolean('active')->default(true)->index();
            $table->timestamps();
        });

        Schema::create('audit_events', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('license_id')->nullable()->constrained()->nullOnDelete();
            $table->string('event_type', 64)->index();
            $table->json('context')->nullable();
            $table->string('ip_address', 64)->nullable();
            $table->timestamp('created_at')->useCurrent()->index();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('audit_events');
        Schema::dropIfExists('releases');
        Schema::dropIfExists('licenses');
        Schema::dropIfExists('customers');
    }
};
