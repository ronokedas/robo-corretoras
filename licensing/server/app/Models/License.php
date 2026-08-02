<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class License extends Model
{
    protected $fillable = [
        'customer_id', 'key_hash', 'key_hint', 'status', 'expires_at',
        'device_hash', 'device_name', 'bound_at', 'activation_token_hash',
        'active_install_id', 'lease_expires_at', 'last_heartbeat_at',
        'last_ip', 'app_version',
    ];

    protected function casts(): array
    {
        return [
            'expires_at' => 'datetime',
            'bound_at' => 'datetime',
            'lease_expires_at' => 'datetime',
            'last_heartbeat_at' => 'datetime',
        ];
    }

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function auditEvents(): HasMany
    {
        return $this->hasMany(AuditEvent::class);
    }
}
