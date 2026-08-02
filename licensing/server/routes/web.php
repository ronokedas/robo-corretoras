<?php

use App\Http\Controllers\AdminController;
use App\Http\Controllers\AuthController;
use Illuminate\Support\Facades\Route;

Route::get('/login', [AuthController::class, 'form'])->name('login');
Route::post('/login', [AuthController::class, 'login'])->middleware('throttle:10,1');
Route::post('/logout', [AuthController::class, 'logout'])->middleware('auth');
Route::middleware('auth')->group(function () {
    Route::get('/change-password', [AuthController::class, 'changeForm'])->name('password.change');
    Route::post('/change-password', [AuthController::class, 'change'])->name('password.update');
});

Route::middleware(['auth', 'password.changed'])->prefix('admin')->name('admin.')->group(function () {
    Route::get('/', fn () => redirect()->route('admin.licenses'));
    Route::get('/licenses', [AdminController::class, 'licenses'])->name('licenses');
    Route::post('/licenses', [AdminController::class, 'createLicense'])->name('licenses.create');
    Route::post('/licenses/{license}/renew', [AdminController::class, 'renew'])->name('licenses.renew');
    Route::post('/licenses/{license}/expires-at', [AdminController::class, 'expiresAt'])->name('licenses.expires-at');
    Route::post('/licenses/{license}/status', [AdminController::class, 'status'])->name('licenses.status');
    Route::post('/licenses/{license}/reset-device', [AdminController::class, 'resetDevice'])->name('licenses.reset');
    Route::get('/releases', [AdminController::class, 'releases'])->name('releases');
    Route::post('/releases', [AdminController::class, 'createRelease'])->name('releases.create');
});

Route::redirect('/', '/admin/licenses');
