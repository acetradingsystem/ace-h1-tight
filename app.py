import streamlit as st
import requests
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACE H1 Tight Scanner",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

* { font-family: 'Syne', sans-serif; }
.stApp { background-color: #0a0a0f; }
#MainMenu, footer, header { visibility: hidden; }

.ace-header {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1a2e 50%, #0a0a0f 100%);
    border-bottom: 1px solid #1a2a4a;
    padding: 2rem 0 1.5rem 0;
    text-align: center;
    margin-bottom: 2rem;
}
.ace-logo {
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem;
    font-weight: 700;
    letter-spacing: 0.3em;
    background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s infinite;
}
@keyframes shimmer { 0% { background-position: 0% } 100% { background-position: 200% } }
.ace-subtitle { color: #a0c8e8; font-size: 0.75rem; letter-spacing: 0.4em; text-transform: uppercase; margin-top: 0.3rem; }
.ace-tagline  { color: #4a6080; font-size: 0.65rem; letter-spacing: 0.3em; text-transform: uppercase; margin-top: 0.2rem; }

.rule-box {
    background: #0d1520;
    border: 1px solid #1a3a1a;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #6a90b0;
    line-height: 2;
}
.rule-highlight { color: #FFD700; font-weight: 700; }

.bull-header { color: #00d4aa; font-family: 'Space Mono', monospace; font-size: 0.75rem; letter-spacing: 0.3em; margin-bottom: 1rem; }
.bear-header { color: #ff6b6b; font-family: 'Space Mono', monospace; font-size: 0.75rem; letter-spacing: 0.3em; margin-bottom: 1rem; margin-top: 2rem; }

.bull-card {
    background: #0a1a0a;
    border: 1px solid #00d4aa;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 20px rgba(0,212,170,0.08);
}
.bear-card {
    background: #1a0a0a;
    border: 1px solid #ff6b6b;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 20px rgba(255,107,107,0.08);
}
.holy-grail-card {
    background: #0d1a0d;
    border: 2px solid #FFD700;
    border-radius: 8px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 0 30px rgba(255,215,0,0.15);
}

.coin-name { font-size: 1.2rem; font-weight: 700; font-family: 'Space Mono', monospace; }
.bull-name { color: #00d4aa; }
.bear-name { color: #ff6b6b; }
.gold-name { color: #FFD700; }

.metric-label { font-size: 0.58rem; letter-spacing: 0.2em; text-transform: uppercase; color: #6a90b0; margin-bottom: 2px; }
.metric-value { font-size: 0.88rem; font-family: 'Space Mono', monospace; color: #b0d0f0; }
.metric-green { color: #00d4aa; }
.metric-red   { color: #ff6b6b; }
.metric-gold  { color: #FFD700; }

.ma-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    background: #FFD700;
    color: #000;
    margin-left: 8px;
}
.h1-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    background: #4a90e2;
    color: #fff;
    margin-left: 8px;
}

.stat-box {
    background: #0d1520;
    border: 1px solid #1a2a3a;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.stat-number { font-size: 2rem; font-weight: 700; font-family: 'Space Mono', monospace; }
.stat-label  { font-size: 0.6rem; letter-spacing: 0.3em; text-transform: uppercase; color: #6a90b0; margin-top: 0.2rem; }

.no-results {
    text-align: center;
    padding: 3rem;
    color: #6a90b0;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.15em;
    border: 1px dashed #1a2a3a;
    border-radius: 8px;
    line-height: 2.5;
}
.timestamp { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: #4a6080; text-align: center; margin-bottom: 1.2rem; }

.timing-box {
    background: #0d1a2e;
    border: 1px solid #1a3a5a;
    border-radius: 8px;
    padding: 0.8rem 1.5rem;
    margin-bottom: 1.5rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #4a90e2;
    text-align: center;
    letter-spacing: 0.15em;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ace-header">
    <div class="ace-logo">♠ACE</div>
    <div class="ace-subtitle">Accumulation Computation Engine</div>
    
</div>
""", unsafe_allow_html=True)

# ── Rule Box ───────────────────────────────────────────────────────────────────
st.markdown("""
    <div class="rule-box" style="text-align: center;">
        <span class="rule-highlight">H1 TIGHT CONSOLIDATION BREAKOUT SCANNER — TSX — HOURLY TIMEFRAME</span><br>
        Scan at <span class="rule-highlight">10:00am ET</span> after 9:30am candle closes &nbsp;|&nbsp;
        Entry: <span class="rule-highlight">10:00am open</span> &nbsp;|&nbsp;
        Exit: <span class="rule-highlight">~3:00pm ET</span><br>
        MA20 ≈ MA200 within 3% on H1 &nbsp;|&nbsp; Elephant Bar: body larger than 70% of last 20 bars (Oliver Velez)
    </div>
""", unsafe_allow_html=True)


# ── Scanner Functions ──────────────────────────────────────────────────────────
def get_tsx_symbols():
    try:
        url = "https://www.tsx.com/json/company-directory/search/tsx/^*"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        data = r.json()
        excluded = ["etf","cdr","trust","fund","index","ishares","vanguard",
                    "horizons","debenture","warrant","bond","preferred","reit"]
        symbols = []
        for c in data.get("results", []):
            sym  = c.get("symbol","").strip()
            name = c.get("name","").lower()
            if not sym or "." in sym: continue
            if any(k in name for k in excluded): continue
            symbols.append(f"{sym}.TO")
        return symbols
    except:
        return ["SHOP.TO","BB.TO","LSPD.TO","NFI.TO","MRE.TO","TLRY.TO",
                "ATZ.TO","GIL.TO","DOL.TO","MRU.TO","WSP.TO","CAE.TO"]

def fetch_h1_tight(symbol):
    try:
        import yfinance as yf

        # ── Fetch H1 data ─────────────────────────────────────────────────────
        # Need ~200 hourly candles for MA200 + buffer
        # yfinance H1 max is 730 days but returns ~200 candles per request
        # Use 60d to get enough H1 candles (60d x 6.5h = ~390 hourly candles)
        ticker = yf.Ticker(symbol)
        hist   = ticker.history(period="60d", interval="1h")

        if hist.empty or len(hist) < 210:
            return None

        # ── Filter to market hours only (9:30am - 4:00pm ET) ─────────────────
        hist.index = hist.index.tz_convert("America/Toronto")
        hist = hist.between_time("09:30", "16:00")

        if len(hist) < 210:
            return None

        # ── Trigger candle = last completed H1 candle (9:30am candle) ─────────
        # When run at 10am, iloc[-1] is the 9:30am candle that just closed
        today_candle = hist.iloc[-1]

        close     = float(today_candle["Close"])
        vol_today = float(today_candle["Volume"])
        t_open    = float(today_candle["Open"])
        t_high    = float(today_candle["High"])
        t_low     = float(today_candle["Low"])

        if close < 5:
            return None

        # ── MA20 and MA200 on H1 candles (excluding trigger candle) ───────────
        # These are 20-hour and 200-hour moving averages
        ma20  = float(hist["Close"].iloc[-21:-1].mean())
        ma200 = float(hist["Close"].iloc[-201:-1].mean())

        # ── THREE FINGERS TIGHT on H1 — MA20 within 3% of MA200 ──────────────
        ma_diff_pct = abs(ma20 - ma200) / ma200 * 100
        if ma_diff_pct > 3.0:
            return None

        # ── Verify narrow state persisted for previous 10 hourly candles ─────
        narrow_candles = 0
        for i in range(2, 12):
            try:
                ma20_i  = float(hist["Close"].iloc[-(20+i):-(i)].mean())
                ma200_i = float(hist["Close"].iloc[-(200+i):-(i)].mean())
                diff_i  = abs(ma20_i - ma200_i) / ma200_i * 100
                if diff_i <= 3.0:
                    narrow_candles += 1
            except: pass
        if narrow_candles < 5:
            return None

        # ── Previous trading day consolidation box (7 hourly candles) ─────────
        # Oliver: look back ~1 full trading day for H1
        # Previous day = candles at index -8 to -2 (7 candles, excluding trigger)
        prev_candles = hist.iloc[-8:-1]
        if len(prev_candles) < 5:
            return None

        high_prev_day = float(prev_candles["High"].max())
        low_prev_day  = float(prev_candles["Low"].min())

        # ── OLIVER VELEZ ELEPHANT BAR DEFINITION ─────────────────────────────
        # Body must be larger than 70% of the last 20 bars
        last_20_bodies = []
        for i in range(2, 22):
            try:
                bar_open  = float(hist["Open"].iloc[-i])
                bar_close = float(hist["Close"].iloc[-i])
                last_20_bodies.append(abs(bar_close - bar_open))
            except: pass

        if len(last_20_bodies) < 10:
            return None

        today_body = abs(close - t_open)
        last_20_sorted = sorted(last_20_bodies)
        percentile_70  = last_20_sorted[int(len(last_20_sorted) * 0.70)]

        if today_body <= percentile_70:
            return None

        # How many bars does today's body beat (for display)
        bars_beaten = sum(1 for b in last_20_bodies if today_body > b)
        eb_pct      = round(bars_beaten / len(last_20_bodies) * 100, 1)
        body_pct    = abs(close - t_open) / close * 100

        # ── Close position in candle range ────────────────────────────────────
        day_range = t_high - t_low
        close_pos = (close - t_low) / day_range * 100 if day_range > 0 else 0

        # ── Breakout detection ────────────────────────────────────────────────
        # BULL: trigger candle closes ABOVE previous day high
        is_bull = (close > high_prev_day and
                   close > t_open and
                   close_pos >= 70.0)

        # BEAR: trigger candle closes BELOW previous day low
        is_bear = (close < low_prev_day and
                   close < t_open and
                   close_pos <= 30.0)

        if not is_bull and not is_bear:
            return None

        direction = "BULL" if is_bull else "BEAR"
        breakout  = (close - high_prev_day) / high_prev_day * 100 if is_bull else (low_prev_day - close) / low_prev_day * 100

        # ── Sector filter ─────────────────────────────────────────────────────
        try:
            info     = ticker.info
            sector   = (info.get("sector","") or "").lower()
            industry = (info.get("industry","") or "").lower()
            excl_s   = ["basic materials","energy","utilities","real estate"]
            excl_i   = ["gold","silver","copper","mining","oil","gas","coal","uranium","etf","trust"]
            if any(s in sector   for s in excl_s): return None
            if any(s in industry for s in excl_i): return None
        except: pass

        # ── Scoring ───────────────────────────────────────────────────────────
        # MA tightness (0-4)
        if ma_diff_pct < 0.5:   ma_score = 4
        elif ma_diff_pct < 1.0: ma_score = 3
        elif ma_diff_pct < 2.0: ma_score = 2
        else:                   ma_score = 1

        # Elephant Bar strength (0-3) — Oliver Velez definition
        if eb_pct >= 95:    eb_score = 3
        elif eb_pct >= 85:  eb_score = 2
        else:               eb_score = 1

        # Close position score (0-2)
        if close_pos >= 90:   pos_score = 2
        elif close_pos >= 70: pos_score = 1
        else:                 pos_score = 0

        # Breakout score (0-2)
        if breakout >= 2:     bo_score = 2
        elif breakout >= 0.5: bo_score = 1
        else:                 bo_score = 0

        total = ma_score + eb_score + pos_score + bo_score

        # Previous day range %
        range_pct = (high_prev_day - low_prev_day) / high_prev_day * 100 if high_prev_day > 0 else 0

        return {
            "symbol":        symbol.replace(".TO",""),
            "direction":     direction,
            "score":         total,
            "ma_score":      ma_score,
            "eb_score":      eb_score,
            "pos_score":     pos_score,
            "bo_score":      bo_score,
            "close":         round(close, 2),
            "volume":        int(vol_today),
            "eb_pct":        eb_pct,
            "body_pct":      round(body_pct, 1),
            "close_pos":     round(close_pos, 1),
            "ma20":          round(ma20, 2),
            "ma200":         round(ma200, 2),
            "ma_diff_pct":   round(ma_diff_pct, 2),
            "high_prev_day": round(high_prev_day, 2),
            "low_prev_day":  round(low_prev_day, 2),
            "range_pct":     round(range_pct, 2),
            "breakout_pct":  round(breakout, 2),
        }
    except: return None

def run_h1_tight_scan():
    progress = st.progress(0, text="Fetching TSX symbol list from TMX...")
    symbols  = get_tsx_symbols()
    total    = len(symbols)
    progress.progress(10, text=f"Scanning {total} TSX stocks for H1 Tight setups (3-5 min)...")
    results  = []
    done     = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_h1_tight, s): s for s in symbols}
        for f in as_completed(futures):
            done += 1
            if done % 60 == 0:
                pct = 10 + int(done/total*85)
                progress.progress(pct, text=f"Progress: {done}/{total} | H1 Tight setups found: {len(results)}")
            try:
                r = f.result()
                if r: results.append(r)
            except: pass
    results.sort(key=lambda x: (-x["score"], -x["eb_pct"]))
    progress.progress(100, text="Scan complete!")
    time.sleep(0.5)
    progress.empty()
    return results

def score_badge(score):
    if score >= 10: bg, fg = "#FFD700", "#000"
    elif score >= 8: bg, fg = "#00d4aa", "#000"
    elif score >= 6: bg, fg = "#4FC3F7", "#000"
    else: bg, fg = "#1a2a3a", "#6a90b0"
    return f'<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:3px;font-family:Space Mono,monospace;font-weight:700;font-size:0.9rem">{score}</span>'

def display_results(results):
    bulls = [r for r in results if r["direction"] == "BULL"]
    bears = [r for r in results if r["direction"] == "BEAR"]
    holy  = [r for r in results if r["score"] >= 9]

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-number metric-gold">{len(holy)}</div><div class="stat-label">🏆 Holy Grail (9+)</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-number metric-green">{len(bulls)}</div><div class="stat-label">🐘 Bull Elephants</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-number metric-red">{len(bears)}</div><div class="stat-label">🐻 Bear Elephants</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#fff">{len(results)}</div><div class="stat-label">Total Setups</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def render_card(r, card_class, name_class):
        direction_emoji = "🐘" if r["direction"] == "BULL" else "🐻"
        close_color = "metric-green" if r["direction"] == "BULL" else "metric-red"
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem">
                <span class="coin-name {name_class}">{direction_emoji} {r['symbol']}</span>
                <div style="display:flex;align-items:center;gap:0.5rem">
                    <span class="h1-badge">H1</span>
                    <span class="ma-badge">MA∆ {r['ma_diff_pct']}%</span>
                    {score_badge(r['score'])}
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0.8rem;margin-bottom:0.8rem">
                <div><div class="metric-label">Price CAD</div><div class="metric-value {close_color}">${r['close']:,.2f}</div></div>
                <div><div class="metric-label">EB Strength</div><div class="metric-value metric-gold">{r['eb_pct']}%ile</div></div>
                <div><div class="metric-label">Body %</div><div class="metric-value">{r['body_pct']}%</div></div>
                <div><div class="metric-label">Close Pos</div><div class="metric-value">{r['close_pos']}%</div></div>
                <div><div class="metric-label">Breakout</div><div class="metric-value {close_color}">+{r['breakout_pct']}%</div></div>
                <div><div class="metric-label">Volume</div><div class="metric-value">{r['volume']:,}</div></div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.8rem">
                <div><div class="metric-label">MA20 (H1)</div><div class="metric-value">${r['ma20']}</div></div>
                <div><div class="metric-label">MA200 (H1)</div><div class="metric-value">${r['ma200']}</div></div>
                <div><div class="metric-label">Prev Day High</div><div class="metric-value">${r['high_prev_day']}</div></div>
                <div><div class="metric-label">Prev Day Low</div><div class="metric-value">${r['low_prev_day']}</div></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Holy Grail setups first
    if holy:
        st.markdown('<div class="bull-header">🏆 HOLY GRAIL SETUPS — SCORE 9+ — HIGHEST CONVICTION</div>', unsafe_allow_html=True)
        for r in holy:
            render_card(r, "holy-grail-card", "gold-name")

    # Bull Elephants
    regular_bulls = [r for r in bulls if r["score"] < 9]
    if bulls:
        st.markdown('<div class="bull-header">🐘 BULL ELEPHANTS — LONG SETUPS</div>', unsafe_allow_html=True)
        for r in regular_bulls:
            render_card(r, "bull-card", "bull-name")

    if not bulls:
        st.markdown('<div style="color:#1a3a1a;font-family:Space Mono,monospace;font-size:0.75rem;text-align:center;padding:1rem;border:1px dashed #1a3a1a;border-radius:8px;margin-bottom:1rem">🐘 No Bull Elephant setups today</div>', unsafe_allow_html=True)

    # Bear Elephants
    if bears:
        st.markdown('<div class="bear-header">🐻 BEAR ELEPHANTS — SHORT SETUPS (Questrade Margin)</div>', unsafe_allow_html=True)
        for r in bears:
            render_card(r, "bear-card", "bear-name")
    else:
        st.markdown('<div style="color:#3a1a1a;font-family:Space Mono,monospace;font-size:0.75rem;text-align:center;padding:1rem;border:1px dashed #3a1a1a;border-radius:8px">🐻 No Bear Elephant setups today</div>', unsafe_allow_html=True)

    if not results:
        st.markdown("""
        <div class="no-results">
            NO H1 TIGHT SETUPS TODAY<br><br>
            MA20 and MA200 are not tight enough on any TSX stock (H1)<br>
            OR no elephant bars fired from a tight MA state<br><br>
            Run at 10:00am ET after the 9:30am candle closes<br>
            Enter at 10:00am open — Exit around 3:00pm ET<br><br>
            Patience is the strategy
        </div>""", unsafe_allow_html=True)

# ── Timing Reminder ────────────────────────────────────────────────────────────
now_et = datetime.utcnow() - timedelta(hours=4)
st.markdown(f"""
<div class="timing-box">
    ⏰ &nbsp; RUN THIS SCAN AT 10:00am ET &nbsp;|&nbsp; 
    Current ET time: {now_et.strftime("%H:%M")} &nbsp;|&nbsp;
    Entry: 10:00am open &nbsp;|&nbsp; Exit: ~3:00pm ET
</div>
""", unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run = st.button("▶  RUN H1 TSX TIGHT SCAN", type="primary", use_container_width=True)

if run:
    with st.spinner(""):
        results = run_h1_tight_scan()
        st.session_state["h1t_results"] = results
        st.session_state["h1t_time"]    = datetime.now().strftime("%Y-%m-%d %H:%M ET")

if "h1t_results" in st.session_state:
    st.markdown(f'<div class="timestamp">Last scan: {st.session_state["h1t_time"]}</div>', unsafe_allow_html=True)
    display_results(st.session_state["h1t_results"])
else:
    st.markdown("""
    <div class="no-results">
        CLICK RUN SCAN TO START<br><br>
        Scans 640+ TSX stocks on the 1-Hour timeframe<br>
        Detects when MA20 ≈ MA200 within 3% on H1 candles<br>
        Lookback = Previous trading day (7 hourly candles)<br><br>
        Best run at 10:00am ET on trading days
    </div>""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;margin-top:3rem;padding-top:1rem;border-top:1px solid #1a2a3a">
    <span style="font-family:Space Mono,monospace;font-size:0.6rem;letter-spacing:0.4em;color:#2a4060">
        NARROW STATE SCANNER - {market} {timeframe} TIMEFRAME
    </span>
</div>
""", unsafe_allow_html=True)
