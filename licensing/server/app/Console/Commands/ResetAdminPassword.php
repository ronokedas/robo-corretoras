<?php

namespace App\Console\Commands;

use App\Models\User;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Hash;

class ResetAdminPassword extends Command
{
    protected $signature = 'admin:reset-password {--email=} {--password=}';
    protected $description = 'Redefine a senha do administrador e exige troca no próximo login';

    public function handle(): int
    {
        $email = strtolower($this->option('email') ?: $this->ask('E-mail'));
        $password = $this->option('password') ?: $this->secret('Nova senha temporária');
        if (!$password || strlen($password) < 12) {
            $this->error('A senha precisa ter pelo menos 12 caracteres.');
            return self::FAILURE;
        }
        $user = User::query()->where('email', $email)->first();
        if (!$user) {
            $this->error('Administrador não encontrado.');
            return self::FAILURE;
        }
        $user->update(['password' => Hash::make($password), 'must_change_password' => true]);
        $this->info('Senha temporária redefinida.');
        return self::SUCCESS;
    }
}
