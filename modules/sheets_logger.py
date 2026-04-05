"""
MÓDULO: Google Sheets Logger
Guarda cada trade cerrado en Google Sheets para persistencia permanente.
"""
import logging
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger("bot.sheets")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID  = "11ktL1p2SdkJLsjFrepG_1bkeH20G6FzynnQ0eXT4KTk"
STRATEGY_VERSION = "v3.0-price-tp"

CREDENTIALS_INFO = {
    "type": "service_account",
    "project_id": "dental-studio-470921",
    "private_key_id": "",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDFeXb+kV5Dm4yk\nJBs7Ll9qtaM3TKjXs4uSZ8tzfA6ENZ51+YQ1lanA9XpdaOn3n031kwXh7OiCBEhz\njh/T50ycbT0FvFj0JBdiDafQs6wFFMt7gs0+//OwXldIqqPMS0CLnav73l/kAmHg\nvK5MCES5+sHGp1TbsMc6nQiFQnXt5daKffxa4sPsG8bDZjNafgH7rZLb/Bky9r4O\npubnPZ6Q8RMpcAzq+R7aJHMhXiHbGVTXbMIqnXrPCsBHhsKmWtUzOtXirr5ePTau\nPRoXapWkRROKsZmXxJn+4onN6MuS8kwKCciXw1IKVWp5mDK0wyFew96BNU2lrvEx\n4+UGkpIhAgMBAAECggEAJUQlomdtDl2rtisxL2MyMwlZpp0zLNevgn7PfHkAJU+Y\nGqPuoQ0gJq+8uqWKp8YauHoZLVhfzW+A+7upwnvfL5MG5c70S4iHGCRDE+XgU+on\nd2TJFndHdfRrzOUU+cAGy4JDG0pNNtKDRZ3d16/kxmMtz+8ymq36/xL08W8IIc99\n0QXgvc8RktZHneh2CY6Pu5kE/Aa43Qg1Y20TdfJARZJA3FuhLbhfzgbYOBoT5eBG\ncBafLWPUmSqSpg9cjCU2Kz9Z8Gj8/57lS+EilrucknLLFWCpy+gqRFy088pwvbz6\nGi+2SgkKw+OATyWdgIdW4artgNyBZZJod5wYsXKMtQKBgQDrPfQK0riw4OciVpS3\nxAeXbF+laWudKm093JQtFoV3X+yxeaQfGvzfNa7eYOFWR0zgBnmDSDufHpcluvfn\nvXNo5LklmXlx++cyLpRjYF1CWhZt4739Chp6F8MG1j5cejjij+u7zu6d1UX0kep6\na0cBZB6V2zwT+FTMmPofwUU93QKBgQDW5lqupPc8I26B3Tzz/P40vTWlWhqwVZ5h\n7PsLGYyvlLFOvVl2dxOvPOjT9mrxPXhMTP4rUX6Kwu1T9nWEbzWQzMJ7o0lbizv2\n5Mu2EijiioXMrocKrP5HKGx9ZPAfJJx/sv3hCDRPwahxV80rPbnXQMXJu0xqFdg9\njLG7bWwLFQKBgAUVKZiyRNtNgLD1PfFagu96n/Zq+LBEomebxHfU7L1PjUWoYyto\n4d3Qwx566WN71uVgPm/ft6oQdyORjpmrNjsl9foh/sW/s5cZ+orLIji0yZdGPGyj\nMz9AFC6pol9NJL2Abo94QR+X5BMMtAxBFR+qkh6axgmIbAyfoYfeHSjhAoGAZet2\nUqH2h9UeEgVFZUo1nfmmubdUNRFGPpdQMOF7McLJnNh814x+D3xJyE10RtmqdjWF\nzjGmXFU6jbmz3o2H0BbsngrBPeN5Gw1D+CQAtACSmJKlhVCqgEERwx7eK0cH2iCf\n+9wSQ0lLhAXqTnnF6+rSY2yrPx0BI5/Yo1WwCkkCgYEApB8RPZqb0wqI61lgESr1\n8T6JviHURJ1teb43VdzNQ09ydnJrTvKaHPfUuDSdMRVdAf0J8iqh3tQ3nRGbWW3K\nJwYZFFXLVvevo4TE3k5Z2v6Qj/+/gHJevFX9QLnwqGjgpTKtA6l3lTHQkIYcc0Wv\neEBdWXeF8AODUhfDCp+3vNY=\n-----END PRIVATE KEY-----\n",
    "client_email": "trading-bot@dental-studio-470921.iam.gserviceaccount.com",
    "client_id": "",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}

_client = None


def get_client():
    global _client
    if _client is None:
        creds   = Credentials.from_service_account_info(CREDENTIALS_INFO, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def log_trade_to_sheets(trade: dict):
    """Agrega una fila con el trade cerrado a Google Sheets."""
    try:
        client = get_client()
        sheet  = client.open_by_key(SPREADSHEET_ID).worksheet("bot-trading-v3")

        ao = trade.get("analysis_open", {})

        # Asegurarse que el symbol viene del trade directamente
        symbol = trade.get("symbol", "")

        row = [
            symbol,
            trade.get("side", ""),
            trade.get("entry_price", 0),
            trade.get("exit_price", 0),
            trade.get("pnl", 0),
            trade.get("reason_close", ""),
            str(trade.get("partial_tp_taken", False)),
            trade.get("opened_at", ""),
            trade.get("closed_at", ""),
            trade.get("duration_hours", 0),
            ao.get("regime", ""),
            ao.get("rsi", ""),
            ao.get("combined_score", ""),
            STRATEGY_VERSION,
        ]

        sheet.append_row(row)
        logger.info(f"✅ Trade guardado en Sheets: {symbol} {trade.get('side')} P&L=${trade.get('pnl'):+.2f} [{STRATEGY_VERSION}]")

    except Exception as e:
        logger.error(f"❌ Error guardando en Sheets: {e}")