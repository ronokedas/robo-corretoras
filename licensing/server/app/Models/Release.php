<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Release extends Model
{
    protected $fillable = [
        'version', 'minimum_version', 'download_url', 'sha256', 'signature', 'active',
    ];

    protected function casts(): array
    {
        return ['active' => 'boolean'];
    }
}
