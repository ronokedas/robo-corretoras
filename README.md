# EvePulse Trader

Aplicativo Windows e cliente não oficial da Evemex para a estratégia M1 de reversão de três velas. A API usada pelo site da corretora não é oficialmente documentada e pode mudar.

## VPS e domínio

O servidor de licenças pode ser publicado com Docker, Caddy e HTTPS automático em `robolite.4dtech.com.br`. Os comandos estão em [DEPLOY_VPS.md](DEPLOY_VPS.md).

## Aplicativo desktop

O EvePulse Trader possui:

- ativação vinculada a um computador;
- licença offline assinada por até 72 horas;
- login Google feito no Chrome ou Edge, sem pedir a senha Google ao programa;
- token Evemex mantido somente em memória;
- contas DEMO e REAL, com confirmação textual obrigatória para ordens reais;
- painel de ativos, acurácia, sinais, operações e P&L;
- configuração de entrada, stop-loss e máximo de operações;
- modo simulado ativado por padrão;
- logs JSONL sem credenciais.

Para executar no ambiente de desenvolvimento:

```powershell
.\run-desktop.ps1
```

Para recompilar e gerar o instalador:

```powershell
.\build-desktop.ps1
```

O instalador gerado fica em `release\EvePulseTrader-Setup-1.0.2.exe`.

Durante os testes locais, o servidor de licenças deve estar disponível em `http://127.0.0.1:8042`. Antes de distribuir a clientes, configure `EVEPULSE_LICENSE_URL` com o endereço HTTPS do VPS e gere uma nova versão.

## Estratégia

- Timeframe e vencimento: M1.
- Três verdes: entrada `DOWN` no segundo 59.
- Três vermelhas: entrada `UP` no segundo 59.
- Doji exige igualdade exata entre abertura e fechamento.
- Cada direção precisa de pelo menos 13 vitórias nas últimas 20 ocorrências não sobrepostas.
- Todos os ativos OTC ativos são analisados; ativos do mercado real são ignorados.

## Segurança

- O modo padrão é DEMO e simulado.
- O modo real exige digitar exatamente `CONFIRMAR REAL`.
- Senhas e tokens não são gravados nos logs.
- O token da licença fica no Gerenciador de Credenciais do Windows.
- A chave completa da licença não é persistida pelo aplicativo.
- Altere qualquer senha compartilhada durante o desenvolvimento antes de usar dinheiro real.

## Linha de comando legada

O robô também continua disponível sem interface:

```powershell
.\run_bot.ps1 --dry-run --once --account DEMO --amount 2 --stop-loss 20 --max-operations 10
```

## Testes

```powershell
.\run_tests.ps1
```

Os testes automatizados não abrem operações. O teste integrado da Evemex é somente leitura e permanece desativado por padrão.
