# முன்சந்தை அறிக்கை — புதன், 25 நவம்பர் 2026

> காகித வர்த்தகம் (paper trading) மட்டும். இது முதலீட்டு ஆலோசனை அல்ல. உண்மையான ஆர்டர் எதுவும் வைக்க வேண்டாம்.

> ✅ **சந்தைப் போக்கு: NIFTY 50 அதன் 200 நாள் EMA-க்கு மேல்** (23 நவ நிறைவு 25,349.65 vs EMA200 24,061.58). விதிப்படி புதிய காகித வர்த்தகங்கள் அனுமதிக்கப்படுகின்றன. இன்று **2 பரிந்துரைகள்**.

## அடிப்படைத் தகவல்

- **கடைசியாக முடிந்த அமர்வு (candle):** திங்கள், 23 நவம்பர் 2026. செவ்வாய் 24 நவம்பர் (குரு நானக் ஜெயந்தி) NSE விடுமுறை என்பதால் இதுவே முந்தைய வர்த்தக நாள் — தரவு புதியது (stale அல்ல). இன்று (25 நவ) வர்த்தக நாள்.
- **ஸ்கேன் நேரம்:** 24 நவம்பர் 2026, 14:56 UTC.
- **சந்தைப் போக்கு (NIFTY 50 vs EMA200):** மேலே (above_ema200 = true).
- **தரவு மூலம்:** Yahoo Finance via yfinance (அதிகாரப்பூர்வமற்றது; தாமதமானது).
- **NSE சரிபார்ப்பு (முதன்மை, அதிகாரப்பூர்வ bhavcopy):** status **ok** — 489 ஒப்பிடப்பட்டன, 489 ஒத்துப்போனது, 0 முரண்பாடு (சகிப்பு 0.5%). BIRET, EMBASSY bhavcopy-யில் இல்லை (REIT-கள்).
- **BSE சரிபார்ப்பு (இரண்டாம் நிலை, ISIN மூலம்):** status **ok** — 489 ஒப்பிடப்பட்டன, 488 ஒத்துப்போனது, 1 முரண்பாடு: CRAFTSMAN (நம் ₹11,649.00 vs BSE ₹11,784.35, 1.15%). BSE, CDSL ஆகியவை BSE-யில் கிடைக்கவில்லை. இன்றைய பரிந்துரைகள் இரண்டிலும் bse_warning இல்லை.
- **ஸ்கேன் எண்ணிக்கை:** Nifty 500 — 501 இல் 491 பகுப்பாய்வு; 10 பிழை (புதிய பட்டியல்கள் / போதுமான வரலாறு இல்லை). SETUP 30 · WATCH 117 · NO TRADE 344 · STALE DATA 0.
- **Screener.in:** இந்த ஓட்டத்தில் எந்த நிறுவனத்தின் Screener பக்கமும் திறக்க முடியவில்லை (அனுமதி கோரிக்கை நேரம் கடந்தது). Promoter holding / கடன் விவரங்கள் வேறு மூலங்களிலிருந்து (கீழே பெயருடன்) எடுக்கப்பட்டவை.
- **முக்கியம்:** கீழே உள்ள "நுழைவு" என்பது **தூண்டுதல் நிலை (trigger)**, தற்போதைய சந்தை விலை அல்ல. சந்தை திறந்த பிறகு விலை கடைசி நிறைவு விலைக்கு மேல் வர்த்தகமானால் மட்டுமே. இரண்டு நாள் இடைவெளிக்குப் பின் (விடுமுறை) இன்று திறப்பதால் gap அபாயம் அதிகம் — "துரத்த வேண்டாம்" நிலையைக் கண்டிப்பாகப் பின்பற்றவும்.

## காகித வர்த்தக விதிகள்

| விதி | அளவு |
|---|---|
| மூலதனம் | ₹1,00,000 |
| ஒரு வர்த்தகத்துக்கு அதிகபட்ச ஒதுக்கீடு | ₹30,000 |
| ஒரு வர்த்தகத்துக்கு அதிகபட்ச இழப்பு (stop-loss அடித்தால்) | ₹500 |
| தினசரி இழப்பு வரம்பு | ₹2,000 |
| ஒரே நேரத்தில் அதிகபட்ச திறந்த வர்த்தகங்கள் | 3 |

இன்றைய இரண்டு பரிந்துரைகளின் மொத்த அபாயம்: **₹985.01** (₹496.85 + ₹488.16) — ஒவ்வொன்றும் ₹500க்குள்; மொத்தம் தினசரி வரம்பு ₹2,000க்குள். மொத்த ஒதுக்கீடு ₹15,590.40 (ஒவ்வொன்றும் ₹30,000க்குள்). திறந்த வர்த்தகங்கள்: 2 (வரம்பு 3).

---

## பரிந்துரை 1: OBEROIRLTY (Oberoi Realty)

| | |
|---|---|
| கடைசி நிறைவு (23 நவ) | ₹1,860.00 (NSE ₹1,860.00 · BSE ₹1,861.70) |
| நுழைவு தூண்டுதல் | ₹1,860.00க்கு மேல் வர்த்தகமானால் மட்டும் |
| துரத்த வேண்டாம் | ₹1,897.20க்கு (+2%) மேல் இருந்தால் தவிர்க்கவும் |
| Stop-loss | ₹1,760.63 (−5.34%) |
| இலக்கு (Target) | ₹2,058.74 (+10.69%) |
| அளவு | 5 பங்குகள் (செலவு ₹9,300.00) |
| அபாயம் / வாய்ப்பு | ₹496.85 / ₹993.70 (1:2) |
| RSI14 · Volume ratio · 20 நாள் breakout | 65.4 · 1.25× · ஆம் |
| ஸ்கேனர் மதிப்பெண் | 100 |

**ஏன் இந்த setup:** EMA20 > EMA50 > EMA200, விலை EMA20-க்கு மேல்; RSI 50–70 வரம்பில்; MACD சிக்னலுக்கு மேல்; ADX ≥ 20, +DI > −DI; அளவு 20 நாள் சராசரியின் 1.25 மடங்கு; முந்தைய 20 நாள் உச்சத்துக்கு மேல் நிறைவு. குறிப்பு: backtest-இல் 100 மதிப்பெண் 85–99-ஐ விடச் சிறந்ததல்ல — செய்தி/துறை ஆதரவுக்காகவே தேர்வு.

**செய்தி:**
- **21 அக்டோபர் 2026 — PL Capital (Q2 FY27 முடிவு அறிக்கை):** முன்விற்பனை (pre-sales) ஆண்டுக்கு ~7 மடங்கு உயர்ந்தது (பெரும்பகுதி குருகிராம் 360 North திட்டம்); வசூல் +40%, வாடகை வருவாய் +18%. கணக்கியல் வருவாய் சற்றுக் குறைவு, லாபம் நிலையானது. PL "BUY" ஆக மேம்படுத்தியது.
  → **பொருள்:** எதிர்கால வருவாய்க்கான முன்விற்பனை வலுவானது — setup-ஐ ஆதரிக்கிறது.
- **23 நவம்பர் 2026 — Business Standard:** BSE Realty குறியீடு நவம்பரில் ~17% உயர்ந்து 52 வார உச்சம்; MOFSL, H2 FY27-இல் Oberoi உள்ளிட்ட நிறுவனங்கள் சிறப்பாகச் செயல்படும் என எதிர்பார்க்கிறது.
  → **பொருள்:** முழுத் துறையும் ஏறுமுகம் — breakout-க்கு துறை ஆதரவு உண்டு; அளவு உயர்வு (1.25×) மிதமானது, விளக்கமற்றது அல்ல.
- **23 நவம்பர் 2026 — Business Today (SMC Global தொழில்நுட்பப் பரிந்துரை):** இறங்கு trendline முறிவு, 200 நாள் சராசரி மீட்பு எனக் குறிப்பிட்டு குறுகிய கால "Buy" (அவர்களது stop ₹1,720, இலக்கு ~₹1,975).
  → **பொருள்:** நம் தொழில்நுட்பப் பார்வையுடன் ஒத்துப்போகிறது; நம் stop (₹1,760.63) அவர்களதை விட இறுக்கமானது.
- 2–25 நவம்பரில் block deal, promoter விற்பனை/pledge, நிர்வாக மாற்றம் எதுவும் கண்டறியப்படவில்லை.

**⚠ முரண்பாடு / சரிபார்க்கப்படாதவை:**
- 360 North வழக்கு: ஜூலை 2026-இல் உயர்நீதிமன்றம் புதிய ஒதுக்கீடுகளைத் தடை செய்தது; ICICI Direct (18 ஆக) "திட்டம் தொடரலாம்" என்கிறது, ஆனால் PL (21 அக்) வழக்கு இன்னும் நடைபெறுவதாகக் குறிப்பிடுகிறது. முன்விற்பனை ஒரே திட்டத்தைச் சார்ந்திருப்பது அபாயம்.
- Realty துறை ஒரு மாதத்தில் ~17% ஏறியுள்ளது — திடீர் பின்வாங்கல் அபாயம். 18 நவ delivery அளவு குறைவு (MarketsMojo, தானியங்கிக் கட்டுரை).
- Screener பக்கம் திறக்க முடியவில்லை — promoter holding/pledge நேரடியாகச் சரிபார்க்கப்படவில்லை.

---

## பரிந்துரை 2: VIJAYA (Vijaya Diagnostic Centre)

| | |
|---|---|
| கடைசி நிறைவு (23 நவ) | ₹1,572.60 (NSE ₹1,572.60 · BSE ₹1,571.60) |
| நுழைவு தூண்டுதல் | ₹1,572.60க்கு மேல் வர்த்தகமானால் மட்டும் |
| துரத்த வேண்டாம் | ₹1,604.05க்கு (+2%) மேல் இருந்தால் தவிர்க்கவும் |
| Stop-loss | ₹1,450.56 (−7.76%) |
| இலக்கு (Target) | ₹1,816.68 (+15.52%) |
| அளவு | 4 பங்குகள் (செலவு ₹6,290.40) |
| அபாயம் / வாய்ப்பு | ₹488.16 / ₹976.32 (1:2) |
| RSI14 · Volume ratio · 20 நாள் breakout | 65.1 · 2.12× · இல்லை |
| ஸ்கேனர் மதிப்பெண் | 85 |

**ஏன் இந்த setup:** EMA20 > EMA50 > EMA200, விலை EMA20-க்கு மேல்; RSI 50–70; MACD சிக்னலுக்கு மேல்; ADX ≥ 20, +DI > −DI; அளவு 20 நாள் சராசரியின் 2.12 மடங்கு. 20 நாள் உச்சத்தை இன்னும் முறியடிக்கவில்லை — எனவே தூண்டுதல் நிலைக்கு மேல் உறுதியான வர்த்தகம் அவசியம்.

**செய்தி:**
- **3 நவம்பர் 2026 — multibagg.ai (Q2 FY27):** வருவாய் ₹255.4 கோடி (+26.7%), EBITDA margin 44.1% (முன்பு 40.6%), லாபம் +37.4%; சோதனை எண்ணிக்கை +16.5%. H2-இல் மேலும் 3 hub, 7 spoke திட்டம்.
  → **பொருள்:** வலுவான வருவாய் வளர்ச்சியும் margin விரிவும் — ஏற்றத்துக்கு அடிப்படை ஆதரவு.
- **21 நவம்பர் 2026 — MarketsMojo:** 16–20 நவ வாரத்தில் பங்கு ~11% உயர்ந்து 52 வார உச்சத்தை நெருங்கியது; கடன்/பங்கு விகிதம் ~0.08 (கடன் மிகக் குறைவு).
  → **பொருள்:** அளவு உயர்வு (2.12×) முடிவுகளுக்குப் பிந்தைய வேகம் + 52 வார உச்சம் நோக்கிய நகர்வுடன் ஒத்துப்போகிறது; தனி நிறுவன அறிவிப்பு இல்லை.
- **23 நவம்பர் 2026 — MarketsMojo:** மதிப்பீடு (valuation) காரணமாக அவர்களது தானியங்கி மதிப்பீட்டை "Buy"-இலிருந்து "Hold" ஆகக் குறைத்தது; ஒரு வருடத்தில் பங்கு ~55% உயர்வு.
  → **பொருள்:** விலை ஏற்கனவே அதிகம் — அளவு சிறியது (4 பங்குகள்), stop கட்டாயம்.
- **Upstox (பங்குதாரர் முறை, செப் 2026):** promoter பங்கு ~52.5% நிலையானது (மிகச் சிறிய குறைவு); mutual fund பங்கு 28% → 31.4% உயர்வு; pledge பற்றிய தகவல் கிடைக்கவில்லை.
- 2–25 நவம்பரில் block deal, promoter விற்பனை, ஒழுங்குமுறைப் பிரச்சினை எதுவும் கண்டறியப்படவில்லை.

**⚠ முரண்பாடு / சரிபார்க்கப்படாதவை:**
- FII பங்கு தொடர்ந்து குறைவு (15.1% → 10.7%, டிச 2025 – செப் 2026).
- MarketsMojo கட்டுரைகள் 52 வார உச்ச எண்ணில் முரண்படுகின்றன (₹1,592 vs ₹1,635.9) — தானியங்கி உள்ளடக்கம்; நம் விலைகள் NSE bhavcopy-யுடன் ஒத்துப்போகின்றன.
- Q2-க்கு earnings call பதிவு வெளியிடப்படவில்லை. Screener பக்கம் திறக்க முடியவில்லை.

---

## கண்காணிப்பு மட்டும் (பரிந்துரை அல்ல)

- **LGEINDIA (LG Electronics India) — மதிப்பெண் 85, RSI 58.6, vol 2.67×, breakout இல்லை:** Q2 FY27 சுத்தமான முடிவுகள் — வருவாய் +19.5%, லாபம் +25.7% (Upstox, 5 நவ); PL "Accumulate", இலக்கு ₹1,881 (9 நவ). ஆனால் 20–23 நவ அளவு உயர்வுக்கு சரிபார்க்கப்பட்ட காரணம் இல்லை; தற்போதைய விலை PL இலக்குக்கு அருகில்; Screener திறக்கவில்லை.
- **FEDERALBNK (Federal Bank) — மதிப்பெண் 85, RSI 56.9, vol 2.29×, breakout இல்லை:** சாதனை Q2 லாபம் +45%, GNPA 1.32% / NNPA 0.17% (Upstox, 16 அக்); FII பங்கு தொடர்ந்து உயர்வு. ஆனால் அளவு உயர்வுக்குக் காரணம் கண்டறியப்படவில்லை (Univest, 20 நவ: "நிறுவனம் சார்ந்த காரணம் இல்லை"). காரணம் தெரியும் வரை கண்காணிப்பு.
- **JSWINFRA (JSW Infrastructure) — மதிப்பெண் 85, RSI 62.0, vol 2.6×, breakout ஆம்:** வலுவான FY28 வளர்ச்சி வழிகாட்டல், நிகர ரொக்கம் (InvestyWise, 13 நவ). ஆனால் Q2 லாபம் −12% (forex இழப்பு), margin குறைவு (Upstox); promoter இன்னும் குறைந்தபட்ச பொதுப் பங்கு விதிக்காகப் பங்கு விற்க வேண்டியிருக்கலாம்; அளவு உயர்வு விளக்கமற்றது.
- **PRESTIGE — மதிப்பெண் 85, RSI 64.1, vol 3.42×, breakout இல்லை:** முன்விற்பனை +20%, FY27 இலக்கு ₹36,000 கோடிக்கு உயர்வு, பல கையகப்படுத்தல்கள் (multibagg, 7 & 17 நவ). ஆனால் Q2 லாபம் 44–48% சரிவு (மூலங்களுக்கிடையே எண் முரண்பாடு), நிகரக் கடன் உயர்வு (₹12,122 கோடி); 3.4× அளவுக்கு காரணம் இல்லை.

## தவிர்க்கப்பட்டவை

- **ASTERDM (Aster DM Quality Care) — மதிப்பெண் 100, RSI 69.2:** Q2 செயல்பாடு வலுவானது (PL "BUY", 9 நவ), 20 நவ மருத்துவமனைத் துறை ஏற்றம். ஆனால் promoter (Blackstone) தனது முழுப் பங்கையும் (~28.6%) pledge செய்துள்ளது (InvestyWise, 22 ஆக); TPG block விற்பனை (ஆக 2026); P/E ~105–117; இணைப்புக்குப் பின் கடன் கடுமையாக உயர்வு; Narayana சொத்து வாங்குதல் பேச்சு உறுதிப்படுத்தப்படவில்லை. முரண்பட்ட / சரிபார்க்கப்படாத தகவல் — தவிர்க்கவும்.
- **PERSISTENT — மதிப்பெண் 85, RSI 67.9:** Q2 லாபம் ஆண்டுக்கு −25.4% (நிறுவன அறிக்கை, 15 அக்); Nagarro கையகப்படுத்தலுக்கான கடன் மற்றும் QIP மூலம் பங்கு நீர்த்தல் (அக் 2026); 20 நவ ஏற்றம் IT துறை முழுவதுமானது, நிறுவனச் செய்தி அல்ல (5paisa). paper_qty 1 மட்டும். அடிப்படை ஆதரவு இல்லை.
- **DIVISLAB:** paper_qty 0 (ஒரு பங்கு விலையே ₹500 அபாய வரம்பை மீறுகிறது).
- **HONASA (RSI 74.1):** 75-க்கு அருகில்; ஆய்வு செய்யப்படவில்லை.
- ADANIENSOL, LALPATHLAB, PIDILITIND, IDFCFIRSTB, GROWW, PHOENIXLTD, KARURVYSYA, AXISBANK, PRIVISCL, ADANIGREEN: இன்று ஆய்வு செய்யப்படவில்லை (முதல் 8 மட்டும்).

---

*நினைவூட்டல்: backtest-இல் இந்த உத்தியின் நன்மை (edge) சிறியது — backtest.html பார்க்கவும்.*

## மூலங்கள்

- ClearTax — NSE விடுமுறைகள் 2026: https://cleartax.in/s/nse-holidays-2026
- PL Capital, 21 அக் 2026 — Oberoi Realty Q2: https://www.plindia.com/ResReport/OBER-21-10-26-PL.pdf
- Business Standard, 23 நவ 2026 — BSE Realty நவம்பர் ஏற்றம்: https://www.business-standard.com/markets/news/bse-realty-index-soars-17-in-november-what-s-driving-real-estate-stocks-126112300352_1.html
- Business Today, 23 நவ 2026 — குறுகிய காலப் பரிந்துரைகள் (Oberoi): https://www.businesstoday.in/markets/trending-stocks/story/oberoi-realty-sbi-life-exide-among-top-stocks-to-buy-for-short-term-gains-check-targets-568995-2026-11-23
- MarketsMojo, 19 நவ 2026 — Oberoi open interest: https://www.marketsmojo.com/news/stocks-in-action/oberoi-realty-sees-significant-open-interest-surge-amid-mixed-market-signals-4268532
- ICICI Direct, 18 ஆக 2026 — 360 North வழக்கு: https://www.icicidirect.com/research/equity/blog/oberoi-realty-has-been-cleared-to-continue-with-360-north-project-by-the-high-court
- multibagg.ai, 3 நவ 2026 — Vijaya Q2 FY27: https://www.multibagg.ai/market-pulse/articles/vijaya-q2-fy27-results-cmw0z3mkm002z31ql6jezy0nr
- MarketsMojo, 21 நவ 2026 — Vijaya வார ஏற்றம்: https://www.marketsmojo.com/news/stocks-in-action/vijaya-diagnostic-centre-ltd-surges-1141-key-financial-and-technical-drivers-behind-the-rally-4270278
- MarketsMojo, 23 நவ 2026 — Vijaya மதிப்பீடு Hold: https://www.marketsmojo.com/news/stock-recommendation/vijaya-diagnostic-centre-downgraded-to-hold-amid-mixed-technical-and-valuation-signals-4271664
- Upstox — Vijaya பங்குதாரர் முறை: https://upstox.com/stocks/vijaya-diagnostic-cen-ltd-shareholding/
- Upstox, 5 நவ 2026 — LG Electronics Q2: https://upstox.com/news/market-news/earnings/lg-electronics-q2-results-net-profit-jumps-26-yo-y-to-489-crore-revenue-grows-to-7-380-crore/article-203031/
- Prabhudas Lilladher, 9 நவ 2026 — LGEL: https://plindia.com/ResReport/LGEL-9-11-26-PL.pdf
- Upstox, 16 அக் 2026 — Federal Bank Q2: https://upstox.com/news/market-news/earnings/federal-bank-q2-results-net-profit-soars-45-yo-y-to-1-386-crore-asset-quality-improves/article-201993/
- Univest, 20 நவ 2026 — Federal Bank 52 வார உச்சம்: https://univest.in/blogs/why-the-federal-bank-ltd-share-price-52-week-high-today-2026
- Upstox, அக் 2026 — JSW Infrastructure Q2: https://upstox.com/news/market-news/earnings/jsw-infrastructure-q2-results-net-profit-declines-12-on-unrealised-forex-losses-revenue-rises-to-1-481-crore/article-202486/
- InvestyWise, 13 நவ 2026 — JSW Infrastructure investor presentation: https://www.investywise.com/jsw-infrastructure-investor-presentation-november-2026
- multibagg.ai, 7 நவ 2026 — Prestige Q2: https://www.multibagg.ai/market-pulse/articles/prestige-estates-q2-profit-fall-cmw6hqh9t00032fph8z9ao1yy
- multibagg.ai, 7 நவ 2026 — Prestige பணப்புழக்கம்/கடன்: https://www.multibagg.ai/market-pulse/articles/prestige-group-profit-cash-flow-ppt-cmw5l3fcx005y2bnxlpy82zmq
- multibagg.ai, 17 நவ 2026 — Prestige / Allure Developers: https://www.multibagg.ai/market-pulse/articles/prestige-estates-allure-developers-acquisition-cmwkqbf2m00352smy6v6jxy1d
- PL Capital, 9 நவ 2026 — Aster DM Q2: https://plindia.com/ResReport/ASTERDM-9-11-26-PL.pdf
- InvestyWise, 22 ஆக 2026 — Aster DM pledge: https://www.investywise.com/aster-dm-quality-care-disclosure-of-encumbrance-on-shares
- Business Standard, 20 நவ 2026 — மருத்துவமனைப் பங்குகள் ஏற்றம்: https://www.business-standard.com/markets/news/bse-hospitals-index-soars-3-apollo-max-narayana-hrudayalaya-surge-5-126112000298_1.html
- Persistent Systems, 15 அக் 2026 — Q2 FY27: https://www.persistent.com/media/press-releases/q2-fy27-results/
- 5paisa, 20 நவ 2026 — IT பங்குகள் ஏற்றம்: https://www.5paisa.com/blog/persistent-systems-tcs-it-shares-rally-20-november-2026

*ஸ்கேனர் மதிப்பெண்கள் நிகழ்தகவுகள் அல்ல. Stop-loss நிறைவேற்றம் உத்தரவாதம் இல்லை. கட்டணம், வரி, slippage சேர்க்கப்படவில்லை.*
