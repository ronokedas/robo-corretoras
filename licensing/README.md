# EvePulse License Center

Servidor Laravel para clientes, chaves de ativação, renovações, bloqueio por computador e licenças offline assinadas por Ed25519.

## Produção

O ambiente de produção usa:

- Caddy com HTTPS automático;
- Laravel 12;
- MySQL 8.4 em rede interna;
- Docker Compose;
- domínio padrão `robolite.4dtech.com.br`;
- segredos exclusivos criados no próprio VPS.

Consulte [DEPLOY_VPS.md](../DEPLOY_VPS.md) para os comandos completos.

## Instalação local no Windows

```powershell
cd C:\novaiq\licensing
.\install-local.ps1
```

Painel local: `http://127.0.0.1:8042`.

## API do cliente

- `POST /api/licenses/activate`
- `POST /api/licenses/heartbeat`
- `POST /api/licenses/deactivate`
- `GET /api/client/version`

A chave privada permanece exclusivamente no servidor. Somente a chave pública é incorporada ao aplicativo Windows.
