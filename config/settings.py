# ============================================================
#  TRADING BOT V3 — CONFIGURACIÓN CENTRAL
#  Estrategia: 3-level TP basado en % precio con trailing stop
# ============================================================
import os

# --- BINANCE API ---
BINANCE_API_KEY    = os.getenv("BINANCE_API_KEY",    "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_TESTNET    = os.getenv("BINANCE_TESTNET", "False") == "True"
DRY_RUN            = os.getenv("DRY_RUN", "True") == "True"

# --- TELEGRAM ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "")

# --- ACTIVOS A OPERAR ---
SYMBOLS = ["ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]

# --- GESTIÓN DE RIESGO ---
CAPITAL_TOTAL_USDT      = float(os.getenv("CAPITAL_TOTAL_USDT", "500"))
MAX_POSITION_PCT        = 0.10
STOP_LOSS_PCT           = 0.035       # 3.5% movimiento de precio
TRAILING_STOP_PCT       = 0.02        # trailing stop para free ride
MAX_LOSS_DAILY_PCT      = 0.04
MAX_LOSS_WEEKLY_PCT     = 0.06
MAX_LOSS_MONTHLY_PCT    = 0.08
FLASH_CRASH_PCT         = 0.10
MAX_OPEN_POSITIONS      = 4
CASH_RESERVE_PCT        = 0.10

# --- TAKE PROFIT POR PRECIO ---
TP1_PRICE_PCT           = 0.02        # 2% precio → 8% ROI con 4x
TP2_PRICE_PCT           = 0.04        # 4% precio → 16% ROI con 4x
TP1_SIZE                = 0.50        # cierra 50% en TP1
TP2_SIZE                = 0.50        # cierra 50% del resto en TP2

# --- POSITION SIZING DINÁMICO ---
POSITION_SIZE_LOW       = 0.10
POSITION_SIZE_MID       = 0.13
POSITION_SIZE_HIGH      = 0.15

# --- UMBRALES DE SEÑAL ---
SIGNAL_THRESHOLD        = 0.45
SIGNAL_REVERSAL_COOLDOWN = 20

# --- PARÁMETROS TÉCNICOS ---
TIMEFRAME               = "15m"
MA_SHORT                = 20
MA_LONG                 = 50
RSI_PERIOD              = 14
RSI_OVERSOLD            = 30
RSI_OVERBOUGHT          = 70
ADX_PERIOD              = 14
ADX_TREND_THRESHOLD     = 25
ADX_FLAT_THRESHOLD      = 20

# --- SENTIMENT ANALYSIS ---
SENTIMENT_WEIGHT        = 0.10
TECHNICAL_WEIGHT        = 0.55
REGIME_WEIGHT           = 0.35
SENTIMENT_MIN_SOURCES   = 2
NEWSAPI_KEY             = os.getenv("NEWSAPI_KEY", "")
SENTIMENT_CACHE_MINUTES = 60

# --- LOOP PRINCIPAL ---
BOT_INTERVAL_SECONDS    = 60

# --- FUTUROS BINANCE ---
LEVERAGE                = 4
MARGIN_TYPE             = "ISOLATED"