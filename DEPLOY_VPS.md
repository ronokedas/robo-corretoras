# Instalação no VPS — robolite.4dtech.com.br

## 1. DNS

No provedor DNS, crie um registro:

```text
Tipo: A
Nome: robolite
Valor: IP_PÚBLICO_DO_VPS
Proxy: desativado durante a primeira emissão do certificado
```

Se houver IPv6 funcional, um registro `AAAA` também pode ser usado. Não crie `AAAA` apontando para um endereço sem conectividade.

## 2. Instalação limpa

Comandos para Ubuntu 22.04/24.04 ou Debian 12, executados no SSH:

```bash
sudo apt-get update
sudo apt-get install -y git ca-certificates curl
sudo install -d -m 0755 /opt/robo-corretoras
sudo chown "$USER":"$USER" /opt/robo-corretoras
git clone https://github.com/ronokedas/robo-corretoras.git /opt/robo-corretoras
cd /opt/robo-corretoras
sudo EVE_DOMAIN=robolite.4dtech.com.br ADMIN_EMAIL=SEU_EMAIL bash licensing/vps/install.sh
```

O instalador:

- instala Docker pelo repositório oficial;
- habilita o serviço no boot;
- libera SSH, 80/TCP, 443/TCP e 443/UDP no UFW;
- cria senhas fortes e um par Ed25519 novo;
- grava `.env.production` com permissão `600`;
- constrói e inicia os containers;
- executa migrations;
- cria o primeiro administrador;
- remove a senha temporária do ambiente após a criação;
- mostra a senha administrativa uma única vez;
- mostra a chave pública necessária para compilar o `.exe`.

Depois, abra `https://robolite.4dtech.com.br` e troque a senha temporária.

## 3. Gerar o `.exe` para o servidor de produção

No Windows, copie a chave pública exibida pelo instalador do VPS e execute:

```powershell
cd C:\novaiq
.\configure-production-client.ps1 -LicenseUrl 'https://robolite.4dtech.com.br' -PublicKey 'CHAVE_PUBLICA_EXIBIDA_NO_VPS'
.\build-desktop.ps1
```

O arquivo `evepulse_desktop/production_config.py` contém somente dados públicos, mas é ignorado pelo Git para evitar builds acidentais com ambientes misturados.

Para mostrar novamente somente a chave pública no VPS:

```bash
cd /opt/robo-corretoras
sudo bash licensing/vps/show-public-key.sh
```

## 4. Atualização

```bash
cd /opt/robo-corretoras
sudo bash licensing/vps/backup.sh
sudo bash licensing/vps/update.sh
```

## 5. Backup

```bash
cd /opt/robo-corretoras
sudo bash licensing/vps/backup.sh
sudo ls -lah /var/backups/evepulse
```

Backups com mais de 30 dias são removidos automaticamente pelo script. Para agendar diariamente às 03:15:

```bash
echo '15 3 * * * root cd /opt/robo-corretoras && bash licensing/vps/backup.sh >> /var/log/evepulse-backup.log 2>&1' | sudo tee /etc/cron.d/evepulse-backup
sudo chmod 644 /etc/cron.d/evepulse-backup
```

## 6. Restauração

```bash
cd /opt/robo-corretoras
sudo bash licensing/vps/restore.sh /var/backups/evepulse/NOME_DO_BACKUP.sql.gz
```

## 7. Diagnóstico

```bash
cd /opt/robo-corretoras/licensing
sudo docker compose --env-file .env.production -f compose.production.yml ps
sudo docker compose --env-file .env.production -f compose.production.yml logs --tail=200 caddy license-api mysql
curl -I https://robolite.4dtech.com.br/up
```

O MySQL não publica porta no host. A chave privada, senhas e banco não devem ser copiados para o GitHub.
