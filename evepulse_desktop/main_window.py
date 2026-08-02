from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QFrame,
    QHBoxLayout, QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QSpinBox, QStackedWidget, QTableWidget,
    QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)

from .config import APP_VERSION, Settings, resource_path
from .google_auth import GoogleAuthWorker
from .licensing import LicenseClient, LicenseError
from .worker import BotWorker


class LicenseTask(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, client: LicenseClient, *, key: str | None = None) -> None:
        super().__init__()
        self.client = client
        self.key = key

    def run(self) -> None:
        try:
            result = self.client.activate(self.key) if self.key is not None else self.client.validate_startup()
            self.completed.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


def label(text: str, object_name: str = "") -> QLabel:
    widget = QLabel(text)
    if object_name:
        widget.setObjectName(object_name)
    return widget


def card_layout() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(8)
    return frame, layout


class EvePulseWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"EvePulse Trader • {APP_VERSION}")
        self.setWindowIcon(QIcon(str(resource_path("assets/evepulse.svg"))))
        self.resize(1320, 820)
        self.setMinimumSize(1080, 700)
        self.license_client = LicenseClient()
        self.settings = Settings()
        self.lease: dict[str, Any] | None = None
        self.evemex_token: str | None = None
        self.auth_worker: GoogleAuthWorker | None = None
        self.bot_worker: BotWorker | None = None
        self.license_worker: LicenseTask | None = None
        self.signal_count = 0
        self.result_count = 0
        self._build_ui()
        QTimer.singleShot(150, self._validate_license)

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(20, 24, 20, 20)
        brand_row = QHBoxLayout()
        icon = QLabel("⌁")
        icon.setStyleSheet("font-size: 31px; color:#48E0CD; font-weight:700")
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(label("EvePulse", "brand"))
        names.addWidget(label("TRADER", "brandSub"))
        brand_row.addWidget(icon)
        brand_row.addLayout(names)
        brand_row.addStretch()
        side.addLayout(brand_row)
        side.addSpacing(34)
        self.nav_buttons = []
        for index, text in enumerate(("Visão geral", "Atividade", "Licença")):
            button = QPushButton(text)
            button.setObjectName("nav")
            button.setProperty("active", index == 0)
            button.clicked.connect(lambda checked=False, i=index: self._navigate(i))
            side.addWidget(button)
            self.nav_buttons.append(button)
        side.addStretch()
        side.addWidget(label(f"Versão {APP_VERSION}", "muted"))
        side.addWidget(label("Estratégia M1 • OTC", "muted"))
        outer.addWidget(self.sidebar)

        self.shell = QStackedWidget()
        self.shell.addWidget(self._activation_page())
        self.shell.addWidget(self._application_page())
        outer.addWidget(self.shell, 1)
        self.sidebar.hide()

    def _activation_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.addStretch()
        row = QHBoxLayout()
        row.addStretch()
        card, box = card_layout()
        card.setFixedWidth(500)
        title = label("Ative o EvePulse Trader", "pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = label("Insira sua chave para liberar este computador. A validação offline dura até 72 horas.", "muted")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("EVP1-XXXXX-XXXXX-XXXXX-XXXXX")
        self.key_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_input.setMaxLength(29)
        self.activate_button = QPushButton("Ativar licença")
        self.activate_button.setObjectName("primary")
        self.activate_button.clicked.connect(self._activate_license)
        self.activation_status = label("Verificando licença local…", "muted")
        self.activation_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(label("⌁", "metricGreen"), alignment=Qt.AlignmentFlag.AlignCenter)
        box.addWidget(title)
        box.addWidget(subtitle)
        box.addSpacing(10)
        box.addWidget(self.key_input)
        box.addWidget(self.activate_button)
        box.addWidget(self.activation_status)
        row.addWidget(card)
        row.addStretch()
        layout.addLayout(row)
        layout.addStretch()
        return page

    def _application_page(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(30, 24, 30, 25)
        layout.setSpacing(18)
        top = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.page_title = label("Visão geral", "pageTitle")
        self.page_subtitle = label("Monitoramento inteligente da estratégia de três velas", "muted")
        titles.addWidget(self.page_title)
        titles.addWidget(self.page_subtitle)
        top.addLayout(titles)
        top.addStretch()
        self.connection_badge = label("Evemex desconectada", "badgeAmber")
        top.addWidget(self.connection_badge)
        layout.addLayout(top)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._overview_page())
        self.pages.addWidget(self._activity_page())
        self.pages.addWidget(self._license_page())
        layout.addWidget(self.pages, 1)
        return wrapper

    def _overview_page(self) -> QWidget:
        page = QWidget()
        body = QVBoxLayout(page)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(15)
        metrics = QHBoxLayout()
        self.metric_labels = {}
        for title, initial, key, green in (
            ("ATIVOS ANALISADOS", "—", "assets", False),
            ("SINAIS NA SESSÃO", "0", "signals", True),
            ("OPERAÇÕES", "0", "operations", False),
            ("P&L DA SESSÃO", "R$ 0,00", "pnl", True),
        ):
            frame, box = card_layout()
            box.addWidget(label(title, "eyebrow"))
            value = label(initial, "metricGreen" if green else "metric")
            box.addWidget(value)
            self.metric_labels[key] = value
            metrics.addWidget(frame)
        body.addLayout(metrics)

        content = QHBoxLayout()
        content.setSpacing(15)
        control, controls = card_layout()
        control.setFixedWidth(330)
        controls.addWidget(label("Sessão de operação", "brand"))
        controls.addWidget(label("Configure os limites antes de iniciar.", "muted"))
        controls.addSpacing(8)
        form = QFormLayout()
        self.account = QComboBox(); self.account.addItems(["DEMO", "REAL"])
        self.account.setCurrentText(str(self.settings.values["account"]))
        self.amount = QDoubleSpinBox(); self.amount.setRange(1, 100000); self.amount.setDecimals(2); self.amount.setPrefix("R$ "); self.amount.setValue(float(self.settings.values["amount"]))
        self.stop_loss = QDoubleSpinBox(); self.stop_loss.setRange(0, 1000000); self.stop_loss.setDecimals(2); self.stop_loss.setPrefix("R$ "); self.stop_loss.setSpecialValueText("Desativado"); self.stop_loss.setValue(float(self.settings.values["stop_loss"]))
        self.max_ops = QSpinBox(); self.max_ops.setRange(0, 10000); self.max_ops.setSpecialValueText("Sem limite"); self.max_ops.setValue(int(self.settings.values["max_operations"]))
        form.addRow("Conta", self.account); form.addRow("Valor por entrada", self.amount); form.addRow("Stop-loss", self.stop_loss); form.addRow("Máximo de operações", self.max_ops)
        controls.addLayout(form)
        self.dry_run = QCheckBox("Modo simulado — não envia ordens")
        self.dry_run.setChecked(bool(self.settings.values["dry_run"]))
        controls.addWidget(self.dry_run)
        controls.addSpacing(6)
        self.google_button = QPushButton("Conectar conta Google")
        self.google_button.setObjectName("secondary")
        self.google_button.clicked.connect(self._start_google_login)
        controls.addWidget(self.google_button)
        self.start_button = QPushButton("Iniciar monitoramento")
        self.start_button.setObjectName("primary")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._toggle_bot)
        controls.addWidget(self.start_button)
        self.session_status = label("Conecte sua conta Evemex para começar.", "muted")
        self.session_status.setWordWrap(True)
        controls.addWidget(self.session_status)
        controls.addStretch()
        content.addWidget(control)

        table_card, table_box = card_layout()
        table_title = QHBoxLayout()
        table_title.addWidget(label("Acurácia por ativo", "brand")); table_title.addStretch()
        table_title.addWidget(label("mínimo 13/20", "badgeGreen"))
        table_box.addLayout(table_title)
        table_box.addWidget(label("Somente padrões com acurácia estritamente acima de 60% são qualificados.", "muted"))
        self.stats_table = QTableWidget(0, 4)
        self.stats_table.setHorizontalHeaderLabels(["ATIVO", "3 VERDES → DOWN", "3 VERMELHAS → UP", "STATUS"])
        self.stats_table.verticalHeader().hide()
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stats_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.stats_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        table_box.addWidget(self.stats_table)
        content.addWidget(table_card, 1)
        body.addLayout(content, 1)
        return page

    def _activity_page(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 0, 0, 0)
        card, box = card_layout(); box.addWidget(label("Linha do tempo da sessão", "brand")); box.addWidget(label("Sinais, decisões, ordens e resultados aparecem aqui sem dados de autenticação.", "muted"))
        self.activity = QTextEdit(); self.activity.setReadOnly(True); self.activity.setPlaceholderText("A sessão ainda não gerou eventos.")
        box.addWidget(self.activity); layout.addWidget(card)
        return page

    def _license_page(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 0, 0, 0)
        card, box = card_layout(); card.setMaximumWidth(720)
        box.addWidget(label("Licença EvePulse", "brand"))
        self.license_info = label("Carregando…", "muted"); self.license_info.setWordWrap(True); box.addWidget(self.license_info)
        deactivate = QPushButton("Desativar neste computador"); deactivate.setObjectName("danger"); deactivate.clicked.connect(self._deactivate_license); box.addWidget(deactivate, alignment=Qt.AlignmentFlag.AlignLeft)
        box.addStretch(); layout.addWidget(card); layout.addStretch()
        return page

    def _validate_license(self) -> None:
        self.license_worker = LicenseTask(self.license_client)
        self.license_worker.completed.connect(self._startup_license_result)
        self.license_worker.failed.connect(lambda _message: self._startup_license_result(None))
        self.license_worker.start()

    def _startup_license_result(self, lease: object) -> None:
        if isinstance(lease, dict):
            self._license_ready(lease)
        else:
            self.activation_status.setText("Informe sua chave de ativação.")

    def _activate_license(self) -> None:
        key = self.key_input.text().strip()
        if not key:
            self.activation_status.setText("Digite a chave recebida.")
            return
        self.activate_button.setEnabled(False); self.activation_status.setText("Validando com o servidor…")
        self.license_worker = LicenseTask(self.license_client, key=key)
        self.license_worker.completed.connect(self._activation_result)
        self.license_worker.failed.connect(self._activation_failed)
        self.license_worker.start()

    def _activation_result(self, lease: object) -> None:
        self.activate_button.setEnabled(True)
        if isinstance(lease, dict):
            self._license_ready(lease)
            self.key_input.clear()

    def _activation_failed(self, message: str) -> None:
        self.activate_button.setEnabled(True)
        self.activation_status.setText(message)

    def _license_ready(self, lease: dict[str, Any]) -> None:
        self.lease = lease
        self.shell.setCurrentIndex(1); self.sidebar.show()
        expiry = str(lease.get("expires_at", "")).replace("T", " ")[:16]
        offline = str(lease.get("lease_expires_at", "")).replace("T", " ")[:16]
        self.license_info.setText(f"Licença ativa até {expiry} UTC.\nPermissão offline renovada até {offline} UTC.\nComputador autorizado e assinatura Ed25519 verificada.")

    def _deactivate_license(self) -> None:
        if QMessageBox.question(self, "Desativar licença", "Deseja remover a ativação deste computador?") != QMessageBox.StandardButton.Yes:
            return
        self.license_client.deactivate(); self.lease = None; self.evemex_token = None
        self.sidebar.hide(); self.shell.setCurrentIndex(0); self.activation_status.setText("Licença desativada.")

    def _start_google_login(self) -> None:
        if self.auth_worker and self.auth_worker.isRunning():
            return
        self.google_button.setEnabled(False)
        self.auth_worker = GoogleAuthWorker()
        self.auth_worker.status.connect(self.session_status.setText)
        self.auth_worker.failed.connect(self._auth_failed)
        self.auth_worker.authenticated.connect(self._auth_ready)
        self.auth_worker.start()

    def _auth_ready(self, token: str, accounts: object) -> None:
        self.evemex_token = token
        modes = ", ".join(str(item.get("mode")) for item in accounts if isinstance(item, dict))
        self.connection_badge.setText("Evemex conectada"); self.connection_badge.setObjectName("badgeGreen"); self.connection_badge.style().unpolish(self.connection_badge); self.connection_badge.style().polish(self.connection_badge)
        self.google_button.setText("Reconectar conta Google"); self.google_button.setEnabled(True)
        self.start_button.setEnabled(True)
        self.session_status.setText(f"Login concluído • contas disponíveis: {modes or 'Evemex'}")
        self._log("Conta Evemex autenticada com segurança; token mantido somente em memória.")

    def _auth_failed(self, message: str) -> None:
        self.google_button.setEnabled(True); self.session_status.setText(message)
        QMessageBox.warning(self, "Login Evemex", message)

    def _toggle_bot(self) -> None:
        if self.bot_worker and self.bot_worker.isRunning():
            self.start_button.setEnabled(False); self.session_status.setText("Encerrando com segurança…"); self.bot_worker.stop(); return
        if not self.evemex_token:
            QMessageBox.information(self, "Conta Evemex", "Conecte sua conta Google primeiro."); return
        account = self.account.currentText(); dry_run = self.dry_run.isChecked()
        if account == "REAL" and not dry_run:
            confirmation, ok = QInputDialog.getText(self, "Confirmação de conta real", 'Digite exatamente "CONFIRMAR REAL" para permitir ordens reais:')
            if not ok or confirmation != "CONFIRMAR REAL":
                QMessageBox.warning(self, "Conta real", "Operação real cancelada."); return
        config = {"account": account, "amount": self.amount.value(), "stop_loss": self.stop_loss.value(), "max_operations": self.max_ops.value(), "dry_run": dry_run}
        self.settings.save(**config)
        self.bot_worker = BotWorker(self.evemex_token, config)
        self.bot_worker.status.connect(self.session_status.setText)
        self.bot_worker.event.connect(self._bot_event)
        self.bot_worker.ready.connect(self._bot_ready)
        self.bot_worker.failed.connect(self._bot_failed)
        self.bot_worker.stopped.connect(self._bot_stopped)
        self._set_controls(False); self.start_button.setEnabled(True); self.start_button.setText("Parar monitoramento"); self.start_button.setObjectName("danger"); self._refresh_style(self.start_button)
        self.bot_worker.start(); self._log(f"Sessão iniciada em {account} • {'simulação' if dry_run else 'ordens habilitadas'}.")

    def _bot_ready(self, data: object) -> None:
        if not isinstance(data, dict): return
        self.metric_labels["assets"].setText(str(data.get("assets", 0)))
        stats = data.get("stats", {})
        self.stats_table.setRowCount(0)
        for symbol in sorted(stats):
            directional = stats[symbol]; green = directional["GREEN"]; red = directional["RED"]
            row = self.stats_table.rowCount(); self.stats_table.insertRow(row)
            qualified = green.qualifies or red.qualifies
            values = (symbol, self._stat_text(green), self._stat_text(red), "QUALIFICADO" if qualified else "AGUARDANDO")
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 3: item.setForeground(Qt.GlobalColor.green if qualified else Qt.GlobalColor.gray)
                self.stats_table.setItem(row, column, item)

    @staticmethod
    def _stat_text(stat: object) -> str:
        sample = int(getattr(stat, "sample_size", 0)); wins = int(getattr(stat, "wins", 0))
        return f"{wins}/{sample}  •  {getattr(stat, 'accuracy', 0):.0%}" if sample else "sem 20 ocorrências"

    def _bot_event(self, event: str, fields: object) -> None:
        data = fields if isinstance(fields, dict) else {}
        if event == "signal":
            self.signal_count += 1; self.metric_labels["signals"].setText(str(self.signal_count))
            self._log(f"Sinal {data.get('symbol')} • {data.get('direction')} • {float(data.get('accuracy', 0)):.0%}")
        elif event in {"dry_run_operation", "operation_opened"}:
            self.metric_labels["operations"].setText(str(int(self.metric_labels["operations"].text()) + 1)); self._log(f"{'Simulação' if event.startswith('dry') else 'Ordem'}: {data.get('symbol')} {data.get('direction')}")
        elif event == "operation_result":
            pnl = float(data.get("session_pnl", 0)); self.metric_labels["pnl"].setText(f"R$ {pnl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")); self._log(f"Resultado {data.get('symbol')}: {data.get('result')} • R$ {float(data.get('profit', 0)):.2f}")
        elif "error" in event:
            self._log(f"Atenção: {data.get('error', event)}")

    def _bot_failed(self, message: str) -> None:
        self._log("Erro: " + message); QMessageBox.critical(self, "EvePulse", message)

    def _bot_stopped(self) -> None:
        self._set_controls(True); self.start_button.setEnabled(bool(self.evemex_token)); self.start_button.setText("Iniciar monitoramento"); self.start_button.setObjectName("primary"); self._refresh_style(self.start_button); self.session_status.setText("Monitoramento parado com segurança.")

    def _set_controls(self, enabled: bool) -> None:
        for widget in (self.account, self.amount, self.stop_loss, self.max_ops, self.dry_run, self.google_button): widget.setEnabled(enabled)

    def _log(self, message: str) -> None:
        self.activity.append(f"<span style='color:#4AE0CD'>{datetime.now():%H:%M:%S}</span>  {message}")

    def _navigate(self, index: int) -> None:
        names = (("Visão geral", "Monitoramento inteligente da estratégia de três velas"), ("Atividade", "Histórico em tempo real da sessão"), ("Licença", "Status e ativação deste computador"))
        self.pages.setCurrentIndex(index); self.page_title.setText(names[index][0]); self.page_subtitle.setText(names[index][1])
        for i, button in enumerate(self.nav_buttons): button.setProperty("active", i == index); self._refresh_style(button)

    @staticmethod
    def _refresh_style(widget: QWidget) -> None:
        widget.style().unpolish(widget); widget.style().polish(widget)

    def closeEvent(self, event) -> None:
        if self.bot_worker and self.bot_worker.isRunning(): self.bot_worker.stop(); self.bot_worker.wait(3000)
        if self.auth_worker and self.auth_worker.isRunning(): self.auth_worker.requestInterruption(); self.auth_worker.wait(2000)
        if self.license_worker and self.license_worker.isRunning(): self.license_worker.wait(6500)
        event.accept()
