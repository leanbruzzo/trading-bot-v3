"""
MÓDULO 6: Telegram Notifier
Envía alertas y notificaciones al usuario via Telegram Bot API.
Incluye comando /status para consultar posiciones abiertas.
"""
import requests
import logging
import threading
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger("bot.telegram")

try:
    from config.settings import DRY_RUN
except ImportError:
    DRY_RUN = False

DRY_LABEL = "🔵 <b>[SIMULADO]</b> " if DRY_RUN else ""

# Referencia global a open_trades (se setea desde main.py)
_open_trades_ref = None
_last_update_id  = 0


def set_trades_ref(trades: dict):
    """Registra la referencia al dict de posiciones abiertas."""
    global _open_trades_ref
    _open_trades_ref = trades


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "TU_TELEGRAM_BOT_TOKEN":
        logger.warning("Telegram no configurado — mensaje no enviado")
        return False
    try:
        url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": parse_mode}
        resp = requests.post(url, data=data, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Error enviando mensaje Telegram: {e}")
        return False


def handle_status_command(open_trades: dict):
    """Genera y envía el mensaje de status con posiciones abiertas."""
    from modules.order_executor import get_current_price
    from modules.risk_manager   import load_risk_state

    if not open_trades:
        send_message("📭 <b>No hay posiciones abiertas actualmente.</b>")
        return

    state    = load_risk_state()
    total_pnl = 0.0
    lines    = ["📊 <b>POSICIONES ABIERTAS</b>\n━━━━━━━━━━━━━━━"]

    for symbol, trade in open_trades.items():
        price = get_current_price(symbol)
        if not price:
            continue

        side  = trade["side"]
        entry = trade["entry"]
        qty   = trade["qty"]

        if side == "LONG":
            pnl = (price - entry) * qty
        else:
            pnl = (entry - price) * qty

        total_pnl += pnl
        pnl_emoji  = "🟢" if pnl >= 0 else "🔴"
        partial    = "✅ Partial TP tomado" if trade.get("partial_done") else "⏳ Esperando Partial TP"

        lines.append(
            f"\n{pnl_emoji} <b>{symbol}</b> — {side}\n"
            f"  Entrada:  ${entry:,.2f}\n"
            f"  Precio:   ${price:,.2f}\n"
            f"  P&L:      <b>${pnl:+.2f} USDT</b>\n"
            f"  Stop:     ${trade['stop']:,.2f}\n"
            f"  {partial}"
        )

    total_emoji = "🟢" if total_pnl >= 0 else "🔴"
    lines.append(f"\n━━━━━━━━━━━━━━━")
    lines.append(f"{total_emoji} <b>P&L Total: ${total_pnl:+.2f} USDT</b>")
    lines.append(f"📅 P&L del día: ${state.get('daily_pnl', 0):+.2f} USDT")

    send_message("\n".join(lines))


def handle_close_command(text: str, open_trades: dict, close_callback):
    """Cierra manualmente una posición por símbolo."""
    parts = text.strip().split()
    if len(parts) < 2:
        send_message("❌ Uso: /close SYMBOL\nEjemplo: /close ETHUSDT")
        return
    symbol = parts[1].upper()
    if symbol not in open_trades:
        send_message(f"⚠️ No hay posición abierta en <b>{symbol}</b>")
        return
    send_message(f"⏳ Cerrando posición <b>{symbol}</b>...")
    close_callback(symbol)


def poll_commands(open_trades: dict, close_callback):
    """Escucha comandos de Telegram en un hilo separado."""
    global _last_update_id
    while True:
        try:
            url  = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {"offset": _last_update_id + 1, "timeout": 30}
            resp = requests.get(url, params=params, timeout=35)
            if resp.status_code != 200:
                continue
            updates = resp.json().get("result", [])
            for update in updates:
                _last_update_id = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "")
                if text.startswith("/status"):
                    handle_status_command(open_trades)
                elif text.startswith("/close"):
                    handle_close_command(text, open_trades, close_callback)
                elif text.startswith("/help"):
                    send_message(
                        "🤖 <b>Comandos disponibles:</b>\n"
                        "/status — Ver posiciones abiertas y P&L\n"
                        "/close SYMBOL — Cerrar posición manualmente (ej: /close ETHUSDT)\n"
                        "/help — Ver esta ayuda"
                    )
        except Exception as e:
            logger.error(f"Error en poll_commands: {e}")
            import time
            time.sleep(10)


def start_command_listener(open_trades: dict, close_callback):
    """Inicia el listener de comandos en un hilo separado."""
    t = threading.Thread(target=poll_commands, args=(open_trades, close_callback), daemon=True)
    t.start()
    logger.info("✅ Listener de comandos Telegram iniciado")


def notify_trade_open(symbol: str, side: str, entry: float, stop: float, tp: float, size: float):
    emoji = "📈" if side == "LONG" else "📉"
    msg = (
        f"{DRY_LABEL}{emoji} <b>TRADE ABIERTO</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Par:        <b>{symbol}</b>\n"
        f"Dirección:  <b>{side}</b>\n"
        f"Entrada:    <b>${entry:,.2f}</b>\n"
        f"Stop-Loss:  <b>${stop:,.2f}</b>\n"
        f"Take-Profit:<b>${tp:,.2f}</b>\n"
        f"Tamaño:     <b>${size:.2f} USDT</b>"
    )
    send_message(msg)


def notify_trade_close(symbol: str, side: str, entry: float, exit_price: float,
                       pnl: float, reason: str):
    emoji = "✅" if pnl >= 0 else "❌"
    pnl_emoji = "🟢" if pnl >= 0 else "🔴"
    msg = (
        f"{DRY_LABEL}{emoji} <b>TRADE CERRADO</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Par:        <b>{symbol}</b>\n"
        f"Dirección:  <b>{side}</b>\n"
        f"Entrada:    <b>${entry:,.2f}</b>\n"
        f"Salida:     <b>${exit_price:,.2f}</b>\n"
        f"P&L:        {pnl_emoji} <b>${pnl:+.2f} USDT</b>\n"
        f"Motivo:     <i>{reason}</i>"
    )
    send_message(msg)


def notify_risk_alert(message: str):
    msg = f"⚠️ <b>ALERTA DE RIESGO</b>\n━━━━━━━━━━━━━━━\n{message}"
    send_message(msg)


def notify_bot_stopped(reason: str):
    msg = (
        f"🛑 <b>BOT DETENIDO</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{reason}\n\n"
        f"<i>Revisá el portfolio manualmente antes de reiniciar.</i>"
    )
    send_message(msg)


def notify_flash_crash(symbol: str, price: float, drop_pct: float):
    msg = (
        f"🚨 <b>FLASH CRASH DETECTADO</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Par:    <b>{symbol}</b>\n"
        f"Precio: <b>${price:,.2f}</b>\n"
        f"Caída:  <b>{drop_pct:.1f}% en 15 min</b>\n\n"
        f"<i>Cerrando posiciones de emergencia...</i>"
    )
    send_message(msg)


def notify_daily_summary(trades: int, pnl: float, open_pos: int):
    emoji = "🟢" if pnl >= 0 else "🔴"
    msg = (
        f"📊 <b>RESUMEN DIARIO</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Trades hoy:          <b>{trades}</b>\n"
        f"P&L del día:         {emoji} <b>${pnl:+.2f} USDT</b>\n"
        f"Posiciones abiertas: <b>{open_pos}</b>\n\n"
        f"<i>Usá /status para ver el detalle.</i>"
    )
    send_message(msg)
