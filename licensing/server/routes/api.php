<?php

use App\Http\Controllers\Api\LicenseController;
use App\Http\Controllers\Api\VersionController;
use Illuminate\Support\Facades\Route;

Route::middleware('throttle:60,1')->group(function () {
    Route::post('/licenses/activate', [LicenseController::class, 'activate']);
    Route::post('/licenses/heartbeat', [LicenseController::class, 'heartbeat']);
    Route::post('/licenses/deactivate', [LicenseController::class, 'deactivate']);
    Route::get('/client/version', VersionController::class);
});
