<?php

namespace App\Console\Commands;

use App\Models\User;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Hash;

class CreateAdmin extends Command
{
    protected $signature = 'admin:create {--email=} {--password=} {--name=Administrador}';
    protected $description = 'Cria ou atualiza o administrador proprietário';

    public function handle(): int
    {
        $email = $this->option('email') ?: $this->ask('E-mail');
        $password = $this->option('password') ?: $this->secret('Senha');
        if (!$email || !$password || strlen($password) < 12) {
            $this->error('Informe e-mail e senha com pelo menos 12 caracteres.');
            return self::FAILURE;
        }
        $existing = User::query()->where('email', strtolower($email))->first();
        if ($existing) {
            $this->info('Administrador já existe; senha preservada.');
            return self::SUCCESS;
        }
        User::create([
            'email' => strtolower($email),
            'name' => $this->option('name'),
            'password' => Hash::make($password),
            'must_change_password' => true,
        ]);
        $this->info('Administrador criado.');
        return self::SUCCESS;
    }
}
