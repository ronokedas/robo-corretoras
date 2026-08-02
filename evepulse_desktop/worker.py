from __future__ import annotations

import threading

from PySide6.QtCore import QThread, Signal

from evemexapi import EvemexClient
from reversal_bot import JsonlLogger, ReversalBot
from .config import data_dir


class BotWorker(QThread):
    status = Signal(str)
    event = Signal(str, object)
    ready = Signal(object)
    failed = Signal(str)
    stopped = Signal()

    def __init__(self, token: str, config: dict) -> None:
        super().__init__()
        self.token = token
        self.config = config
        self.stop_flag = threading.Event()
        self.bot: ReversalBot | None = None

    def run(self) -> None:
        client = EvemexClient()
        try:
            self.status.emit("Conectando à Evemex…")
            client.connect_with_token(self.token)
            account = client.select_account(self.config["account"])
            self.status.emit(f"Conta {account.mode} conectada • saldo R$ {account.balance:.2f}")
            if float(self.config["amount"]) > account.balance:
                raise RuntimeError("O valor da entrada excede o saldo da conta.")
            self.bot = ReversalBot(
                client,
                amount=float(self.config["amount"]),
                stop_loss=float(self.config["stop_loss"]),
                max_operations=int(self.config["max_operations"]),
                dry_run=bool(self.config["dry_run"]),
                logger=JsonlLogger(data_dir() / "logs"),
                stop_event=self.stop_flag,
                event_callback=lambda name, fields: self.event.emit(name, fields),
            )
            self.status.emit("Mapeando ativos OTC e calculando estatísticas…")
            self.bot.initialize()
            self.ready.emit({"assets": len(self.bot.symbols), "stats": self.bot.stats})
            self.status.emit("Monitorando o mercado • aguardando sinais no segundo 59")
            self.bot.run()
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            client.close()
            self.stopped.emit()

    def stop(self) -> None:
        self.stop_flag.set()
