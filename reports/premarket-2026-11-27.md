# முன்சந்தை அறிக்கை — வெள்ளி, 27 நவம்பர் 2026

> காகித வர்த்தகம் (paper trading) மட்டும். இது முதலீட்டு ஆலோசனை அல்ல. உண்மையான ஆர்டர் எதுவும் வைக்க வேண்டாம்.

> ✅ **சந்தைப் போக்கு: NIFTY 50 அதன் 200 நாள் EMA-க்கு மேல்** (26 நவ நிறைவு 25,884.50 vs EMA200 24,096.84). விதிப்படி புதிய காகித வர்த்தகங்கள் அனுமதிக்கப்படுகின்றன. இன்று **1 பரிந்துரை** மட்டும் (MCX) — அதுவும் திறந்த வர்த்தக இடம் இருந்தால் மட்டும் (கீழே பார்க்கவும்).

## அடிப்படைத் தகவல்

- **கடைசியாக முடிந்த அமர்வு (candle):** வியாழன், 26 நவம்பர் 2026 — முந்தைய NSE வர்த்தக நாள்; தரவு புதியது (stale அல்ல). இன்று (27 நவ) வழக்கமான வர்த்தக நாள் (நவம்பர் விடுமுறைகள்: 10 நவ, 24 நவ மட்டும் — Angel One).
- **ஸ்கேன் நேரம்:** 26 நவம்பர் 2026, 14:57 UTC.
- **சந்தைப் போக்கு (NIFTY 50 vs EMA200):** மேலே (above_ema200 = true).
- **தரவு மூலம்:** Yahoo Finance via yfinance (அதிகாரப்பூர்வமற்றது; தாமதமானது).
- **NSE சரிபார்ப்பு (முதன்மை, அதிகாரப்பூர்வ bhavcopy):** status **ok** — 489 ஒப்பிடப்பட்டன, 489 ஒத்துப்போனது, 0 முரண்பாடு (சகிப்பு 0.5%).
- **BSE சரிபார்ப்பு (இரண்டாம் நிலை, ISIN மூலம்):** status **ok** — 487 ஒப்பிடப்பட்டன, 486 ஒத்துப்போனது, 1 முரண்பாடு: VBL (நம் ₹428.40 vs BSE ₹434.00, 1.29%). BSE, CDSL ஆகியவை BSE-யில் கிடைக்கவில்லை. இன்றைய பரிந்துரையில் bse_warning இல்லை.
- **ஸ்கேன் எண்ணிக்கை:** Nifty 500 — 501 இல் 491 பகுப்பாய்வு; 10 பிழை (புதிய பட்டியல்கள் / போதுமான வரலாறு இல்லை). SETUP 16 · WATCH 144 · NO TRADE 329 · STALE DATA 2 (BIRET, EMBASSY — 25 நவ தரவு).
- **Screener.in:** WOCKPHARMA, ACE பக்கங்கள் படிக்கப்பட்டன. LODHA, MCX, LGEINDIA, RUBICON, 360ONE, PRESTIGE பக்கங்கள் திறக்க முடியவில்லை (அனுமதி கோரிக்கை நேரம் கடந்தது) — அவற்றுக்கு செய்தித் தளங்கள் பயன்படுத்தப்பட்டன.
- **திறந்த காகித வர்த்தகங்கள்:** OBEROIRLTY (25 நவ பரிந்துரை) 26 நவ ₹1,905.20, VIJAYA ₹1,587.10 — இரண்டும் stop-க்கு மேல். நேற்றைய NH பரிந்துரை (தூண்டுதல் ₹2,003.70) 26 நவ **₹1,982.20-இல் நிறைவு** — தூண்டுதலுக்குக் கீழ். நாள் இடையில் ₹2,003.70-ஐத் தாண்டியதா என்பது நம் தரவில் தெரியவில்லை. **NH எடுக்கப்பட்டிருந்தால் 3 இடங்களும் நிரம்பியுள்ளன — இன்று புதிய வர்த்தகம் வேண்டாம்.** NH எடுக்கப்படவில்லை என்றால் 1 இடம் மீதம்.
- **முக்கியம்:** கீழே உள்ள "நுழைவு" என்பது **தூண்டுதல் நிலை (trigger)**, தற்போதைய சந்தை விலை அல்ல. சந்தை திறந்த பிறகு விலை கடைசி நிறைவு விலைக்கு மேல் வர்த்தகமானால் மட்டுமே.

## காகித வர்த்தக விதிகள்

| விதி | அளவு |
|---|---|
| மூலதனம் | ₹1,00,000 |
| ஒரு வர்த்தகத்துக்கு அதிகபட்ச ஒதுக்கீடு | ₹30,000 |
| ஒரு வர்த்தகத்துக்கு அதிகபட்ச இழப்பு (stop-loss அடித்தால்) | ₹500 |
| தினசரி இழப்பு வரம்பு | ₹2,000 |
| ஒரே நேரத்தில் அதிகபட்ச திறந்த வர்த்தகங்கள் | 3 |

இன்றைய பரிந்துரையின் அபாயம்: **₹284.71** (₹500க்குள்), ஒதுக்கீடு ₹3,835.00 (₹30,000க்குள்). OBEROIRLTY + VIJAYA திறந்திருந்தால் (₹985.01) மொத்தத் திறந்த அபாயம் ₹985.01 + ₹284.71 = **₹1,269.72**; NH-ஐயும் சேர்த்தாலும் (₹439.08) ₹1,708.80 — தினசரி வரம்பு ₹2,000க்குள். ஆனால் NH திறந்திருந்தால் 3 வர்த்தக வரம்பு காரணமாக MCX எடுக்கக் கூடாது.

---

## பரிந்துரை 1: MCX (Multi Commodity Exchange of India)

| | |
|---|---|
| கடைசி நிறைவு (26 நவ) | ₹3,835.00 (NSE ₹3,835.00 · BSE ₹3,837.00) |
| நுழைவு தூண்டுதல் | ₹3,835.00க்கு மேல் வர்த்தகமானால் மட்டும் |
| துரத்த வேண்டாம் | ₹3,911.70க்கு (+2%) மேல் இருந்தால் தவிர்க்கவும் |
| Stop-loss | ₹3,550.29 (−7.42%) |
| இலக்கு (Target) | ₹4,404.42 (+14.85%) |
| அளவு | 1 பங்கு (செலவு ₹3,835.00) |
| அபாயம் / வாய்ப்பு | ₹284.71 / ₹569.42 (1:2) |
| RSI14 · Volume ratio · 20 நாள் breakout | 67.0 · 1.88× · ஆம் |
| ஸ்கேனர் மதிப்பெண் | 100 |

**ஏன் இந்த setup:** EMA20 > EMA50 > EMA200, விலை EMA20-க்கு மேல்; RSI 50–70 வரம்பில்; MACD சிக்னலுக்கு மேல்; ADX 29.9, +DI (30.9) > −DI (13.4); அளவு 20 நாள் சராசரியின் 1.88 மடங்கு; முந்தைய 20 நாள் உச்சத்துக்கு மேல் நிறைவு — புதிய வாழ்நாள் உச்சம். குறிப்பு: backtest-இல் 100 மதிப்பெண் 85–99-ஐ விடச் சிறந்ததல்ல — தேர்வுக்குக் காரணம் ஏற்றத்துக்கான சரிபார்க்கப்பட்ட காரணமும் வலுவான முடிவுகளும்தான். திறந்த வர்த்தகங்களிலிருந்து வேறு துறை (realty / diagnostics / hospitals அல்ல) என்பதும் ஒரு காரணம்.

**செய்தி / அடிப்படை:**
- **18 நவம்பர் 2026 — Angel One:** H1 FY27 ஒருங்கிணைந்த மொத்த வருமானம் ஆண்டுக்கு ~99% உயர்வு (₹1,600 கோடி), நிகர லாபம் ~117% உயர்வு (₹868 கோடி), EBITDA margin ~75%. 16 நவ 52 வார உச்சம்.
  → **பொருள்:** லாப வளர்ச்சி மிக வலுவானது — breakout-க்கு அடிப்படை ஆதரவு.
- **26 நவம்பர் 2026 — Kotak Neo, EquityPandit:** முந்தைய நாள் US பணவீக்கத் தரவால் தங்கம்/வெள்ளி கடுமையாகச் சரிந்த பின் மீண்டதால், MCX காலையிலேயே ~5% உயர்ந்தது (முந்தைய நிறைவு ₹3,565). அன்று நிறுவனத்திடமிருந்து புதிய அறிவிப்பு இல்லை.
  → **பொருள்:** அளவு உயர்வுக்கு சரிபார்க்கப்பட்ட காரணம் உண்டு (கமாடிட்டி வர்த்தக அளவு எதிர்பார்ப்பு). ஆனால் பங்கு விலை bullion ஏற்ற இறக்கத்தைச் சார்ந்தது.
- **26 நவம்பர் 2026 — Upstox:** அன்று வாழ்நாள் உச்சம் தொட்ட 8 பங்குகளில் MCX; மூலதனச் சந்தைப் பங்குகள் மீதான ஆர்வம், கமாடிட்டி அளவு உயர்வு காரணம் எனக் குறிப்பு. ஆண்டு தொடக்கம் முதல் ~70%+ உயர்வு.
- **26 நவம்பர் 2026 — MarketsMojo:** P/E ~50×, P/B ~26× — மதிப்பீடு உயர்ந்தது; பெரிய எதிர்மறை நிதிக் காரணி இல்லை எனக் குறிப்பு.
- 7–26 நவம்பரில் block deal, ஒழுங்குமுறை (SEBI) நடவடிக்கை, நிர்வாக மாற்றம் எதுவும் படித்த மூலங்களில் கண்டறியப்படவில்லை.

**⚠ முரண்பாடு / சரிபார்க்கப்படாதவை:**
- Screener.in பக்கம் திறக்கவில்லை — காலாண்டு அட்டவணை, promoter/pledge விவரம் நேரடியாகச் சரிபார்க்கப்படவில்லை (MCX-க்கு promoter இல்லை; நிறுவன முதலீட்டாளர் பங்கு ~82% என MarketsMojo).
- 26 நவ நாள் இடை உச்சம் குறித்து மூலங்கள் முரண்: காலை அறிக்கைகள் ~₹3,747–3,759; Upstox ₹3,850. நம் NSE-சரிபார்க்கப்பட்ட நிறைவு ₹3,835 — அதனால் பிற்பகலில் மேலும் ஏறியது சாத்தியம்.
- Kotak Neo: US-இல் வட்டி உயர்வு எதிர்பார்ப்பு bullion-க்கு அழுத்தம் — தங்கம் மீண்டும் சரிந்தால் MCX-ம் பாதிக்கப்படலாம்.
- Stop தூரம் 7.4% (ATR ₹142) — பெரிய ஏற்ற இறக்கம்; ஒரு மாதத்தில் ~18–23% ஏற்றத்துக்குப் பின் நுழைவு.

---

## கண்காணிப்பு மட்டும் (பரிந்துரை அல்ல)

- **LODHA (Lodha Developers) — மதிப்பெண் 100, RSI 67.4, vol 1.96×, breakout ஆம்:** Q2 FY27 நிகர லாபம் ₹1,013 கோடி (+28%), வருவாய் +18%, pre-sales +10% (multibagg, 13 நவ). 26 நவ ~5% உயர்வு — நிறுவனச் செய்தி இல்லை, realty துறை ஏற்றம் (EquityPandit, Business Standard 26 நவ); MOFSL H2 outperformer எனக் குறிப்பு (Business Standard, 23 நவ). ஆனால்: ஒரு மாதத்தில் ~27% உயர்வு; நம் இலக்கு ₹1,443.64 Emkay இலக்கு ₹1,400-ஐ விட மேல், 52 வார உச்சம் ₹1,344.95 வழியில் தடையாக இருக்கலாம்; OBEROIRLTY ஏற்கனவே திறந்திருப்பதால் realty-யில் அதிகச் செறிவு. கண்காணிப்பு.
- **WOCKPHARMA (Wockhardt) — மதிப்பெண் 100, RSI 65.1, vol 2.36×, breakout ஆம்:** Screener: செப் 2026 காலாண்டு விற்பனை ₹969 கோடி (+24% ஆண்டுக்கு), ஆனால் நிகர லாபம் ₹73 கோடி (ஆண்டுக்கு −11%, காலாண்டுக்கு −32%), margin 21% → 18%; கடன் ~₹2,238 கோடி நிலையானது; promoter ~49.3%. 26 நவ 7.5% ஏற்றம் — காரணம் சரிபார்க்கப்படவில்லை (MarketsMojo காரணம் கூறவில்லை). சுயாதீன இயக்குநர் பதவிக்காலம் முடிவு (Medical Dialogues, 10 நவ) — வழக்கமானது. விளக்கமற்ற ஏற்றம் + லாபச் சரிவு காரணமாகக் கண்காணிப்பு.
- **RUBICON (Rubicon Research) — மதிப்பெண் 85, RSI 66.7, vol 2.59×, breakout ஆம்:** Screener பக்கம் திறக்கவில்லை; கடந்த 3 வாரச் செய்திகளைச் சரிபார்க்க முடியவில்லை. சரிபார்க்கப்படாததால் கண்காணிப்பு.
- **360ONE (360 ONE WAM) — மதிப்பெண் 85, RSI 64.1, vol 1.61×, breakout இல்லை:** Screener பக்கம் திறக்கவில்லை; கண்டறிந்த UBS கூட்டணிச் செய்தி 2025-ஐச் சேர்ந்தது. சமீபச் செய்தி சரிபார்க்கப்படவில்லை.

## தவிர்க்கப்பட்டவை

- **LGEINDIA (LG Electronics India) — மதிப்பெண் 85, RSI 53.9, vol 22.28×, breakout இல்லை:** 22 மடங்கு அளவுக்கு சரிபார்க்கப்பட்ட காரணம் இல்லை — Trendlyne-இல் நவம்பரில் bulk/block deal எதுவும் பட்டியலிடப்படவில்லை; 26 நவ காலை பங்கு ~2.9% சரிவில் இருந்தது (Trendlyne). MSCI நவம்பர் மாற்றங்களில் (30 நவ முதல்) பெயர் காணப்படவில்லை (Angel One). விளக்கமற்ற அளவு உயர்வு — தவிர்க்கவும்.
- **ACE (Action Construction Equipment) — RSI 74.0, vol 9.78×:** RSI 75-ஐ நெருங்குகிறது; Screener: Q2 லாபம் ₹164 கோடி (+82%) ஆனால் அதில் பெரும்பகுதி பிற வருமானம் (₹96 கோடி); கடன் ₹8 → ₹151 கோடி (செப் 2026) திடீர் உயர்வு. 26 நவ Kotak Midcap மாநாட்டுச் சந்திப்புகள் இருந்தன; ~10× அளவுக்கு நேரடிக் காரணம் சரிபார்க்கப்படவில்லை.
- **PRESTIGE — RSI 74.5, vol 8.41×:** 26 நவ ~8% ஏற்றம் realty ஏற்றம் மற்றும் Axis Securities "Buy" (இலக்கு ₹1,950) உடன் (Business Standard). RSI 75-க்கு அருகில், ஒரு மாதத்தில் ~31% உயர்வு; realty செறிவு — தவிர்க்கவும்.
- **J&KBANK (RSI 75.3), DLF (RSI 78.0):** RSI 75-க்கு மேல் — விதிப்படி தவிர்ப்பு.
- **OBEROIRLTY:** 25 நவ பரிந்துரை — ஏற்கனவே திறந்திருக்கலாம்; புதிய நுழைவு வேண்டாம் (stop ₹1,760.63).
- **BAJAJHLDNG:** paper_qty 0 (ஒரு பங்கின் அபாயம் ₹500-ஐத் தாண்டுகிறது).
- JSWINFRA, HEROMOTOCO, LAURUSLABS, WELSPUNLIV: இன்று ஆய்வு செய்யப்படவில்லை (முதல் 8 மட்டும்). JSWINFRA நேற்று ADX குறைவு, Q2 லாபச் சரிவு காரணமாகத் தவிர்க்கப்பட்டது (ADX இன்னும் 16.0).

---

*நினைவூட்டல்: backtest-இல் இந்த உத்தியின் நன்மை (edge) சிறியது — backtest.html பார்க்கவும்.*

## மூலங்கள்

- Angel One — NSE/BSE நவம்பர் 2026 விடுமுறைகள்: https://www.angelone.in/news/market-updates/stock-market-nse-bse-holidays-november-2026-key-dates-and-muhurat-trading
- Angel One, 18 நவ 2026 — MCX 52 வார உச்சம் / H1 முடிவுகள்: https://www.angelone.in/news/stocks/mcx-share-price-in-focus-hits-52-week-high-in-intraday-trading-on-november-16-2026
- Kotak Neo, 26 நவ 2026 — MCX, bullion மீட்சி: https://www.kotakneo.com/news/commodities/mcx-share-price-rises-as-gold-silver-rebound-after-crash/
- EquityPandit, 26 நவ 2026 — MCX 5% உயர்வு: https://www.equitypandit.com/mcx-shares-surge-5-as-gold-and-silver-prices-bounce-back/
- Upstox, 26 நவ 2026 — வாழ்நாள் உச்சம் தொட்ட 8 பங்குகள்: https://upstox.com/news/market-news/stocks/mcx-icici-bank-laurus-labs-8-stocks-that-hit-record-highs-on-november-26-here-s-what-charts-show/article-204029/
- MarketsMojo, 26 நவ 2026 — MCX வாழ்நாள் உச்சம்: https://www.marketsmojo.com/news/stocks-in-action/multi-commodity-exchange-of-india-ltd-hits-all-time-high-amid-robust-performance-4275614
- multibagg.ai, 13 நவ 2026 — Lodha Q2: https://www.multibagg.ai/market-pulse/articles/lodha-q2-profit-growth-cmwdz38vd00vb2dqpvbamr0t8
- EquityPandit, 26 நவ 2026 — Lodha 5% உயர்வு: https://www.equitypandit.com/lodha-developers-jumps-5-as-realty-rally-rolls-on/
- Business Standard, 26 நவ 2026 — Nifty Realty 52 வார உச்சம்: https://www.business-standard.com/markets/news/nifty-realty-hits-52-week-high-up-3-led-by-brigade-enterprises-prestige-estates-126112600658_1.html
- Business Standard, 23 நவ 2026 — BSE Realty நவம்பரில் 17% உயர்வு: https://www.business-standard.com/markets/news/bse-realty-index-soars-17-in-november-what-s-driving-real-estate-stocks-126112300352_1.html
- Screener.in — Wockhardt: https://www.screener.in/company/WOCKPHARMA/consolidated/
- multibagg.ai, 2 நவ 2026 — Wockhardt H1 முடிவுகள்: https://www.multibagg.ai/market-pulse/articles/wockhardt-limited-first-half-profit-announcement-cmvzke7on002d2vpecnbc9qlf
- Medical Dialogues, 10 நவ 2026 — Wockhardt சுயாதீன இயக்குநர்: https://medicaldialogues.in/amp/news/industry/pharma/wockhardt-independent-director-vinesh-kumar-jairath-steps-down-183035
- MarketsMojo, 26 நவ 2026 — Wockhardt 7.51% உயர்வு: https://www.marketsmojo.com/news/stocks-in-action/wockhardt-ltd-hits-intraday-high-with-751-surge-on-26-nov-2026-4275766
- Trendlyne — LG Electronics India bulk/block deals: https://trendlyne.com/equity/bulk-block-deals/LGEINDIA/3280897/lg-electronics-india-ltd/
- Angel One, 12 நவ 2026 — MSCI நவம்பர் 2026 மாற்றங்கள்: https://www.angelone.in/news/market-updates/msci-november-2026-rejig-lic-adani-green-coforge-meesho-added
- Screener.in — Action Construction Equipment: https://www.screener.in/company/ACE/consolidated/
- Angel One, 6 நவ 2025 — 360 ONE / UBS கூட்டணி (பழைய செய்தி): https://www.angelone.in/news/market-updates/360-one-wam-ubs-ag-join-hands-for-wealth-management-partnership

*ஸ்கேனர் மதிப்பெண்கள் நிகழ்தகவுகள் அல்ல. Stop-loss நிறைவேற்றம் உத்தரவாதம் இல்லை. கட்டணம், வரி, slippage சேர்க்கப்படவில்லை.*
