<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Release;
use App\Services\LeaseSigner;

class VersionController extends Controller
{
    public function __invoke(LeaseSigner $signer)
    {
        $release = Release::query()->where('active', true)->latest('id')->first();
        if (!$release) {
            return response()->json($signer->signPayload([
                'update_available' => false,
                'published_at' => now('UTC')->toIso8601String(),
            ]));
        }
        return response()->json($signer->signPayload([
            'version' => $release->version,
            'minimum_version' => $release->minimum_version,
            'download_url' => $release->download_url,
            'sha256' => $release->sha256,
            'file_signature' => $release->signature,
            'published_at' => $release->created_at->utc()->toIso8601String(),
        ]));
    }
}
