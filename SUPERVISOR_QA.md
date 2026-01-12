# Volatility Forecasting Model - Supervisor Q&A

Quick-reference Q&A for project discussions and presentations.

---

## 1. PROJECT OVERVIEW

### Q: What does this model do?
**A:** It predicts whether market volatility will increase or decrease in the next hour, achieving 70% accuracy and 77% AUC on futures data.

### Q: Why is predicting volatility useful?
**A:** Volatility directly impacts option prices. Predicting volatility changes helps:
- Time option trades better (buy before volatility spikes)
- Manage risk (reduce exposure before volatile periods)
- Optimize portfolio hedging strategies

### Q: What data are you using?
**A:** CME Globex futures tick data (NASDAQ-100 E-mini) from Databento:
- 78 files spanning ~3 months (Sep-Dec 2025)
- 21.8 million individual trades
- Aggregated into 16,241 five-minute bars

---

## 2. MACHINE LEARNING

### Q: Why did you choose Random Forest?
**A:** I tested 4 models (Logistic Regression, Random Forest, XGBoost, LightGBM). Random Forest was included because:
- **Pros:** Handles non-linear patterns, resistant to overfitting, interpretable
- **Cons:** Slower than boosting methods, slightly lower accuracy
- **Result:** 67% accuracy vs LightGBM's 70%, so we use LightGBM

### Q: What's the difference between XGBoost and LightGBM?
**A:** Both are gradient boosting algorithms, but:
- **XGBoost:** Industry standard, highly accurate, builds trees depth-first
- **LightGBM:** Newer, faster, builds trees leaf-first, better with large datasets
- **Our results:** LightGBM scored 0.7705 AUC vs XGBoost's 0.7686 (marginal improvement)

### Q: Why use multiple models instead of just one?
**A:** To compare and choose the best performer. Different models have different strengths:
- **Logistic Regression:** Baseline (simple, interpretable)
- **Random Forest:** Handles interactions well
- **XGBoost/LightGBM:** State-of-the-art accuracy
- **Outcome:** LightGBM won, but testing all builds confidence

### Q: How do you prevent overfitting?
**A:** Multiple techniques:
1. **Train/test split:** 70% train, 30% test (never test on training data)
2. **Time series cross-validation:** 4-fold CV with 2-hour gaps
3. **Regularization:** Built into XGBoost/LightGBM
4. **Feature scaling:** StandardScaler prevents large-magnitude features from dominating
5. **Validation:** Consistent performance across all folds (76.4% AUC ± 0.2%)

### Q: What's your accuracy?
**A:**
- **Raw accuracy:** 70.01%
- **Baseline (guessing):** 51.8%
- **Edge:** +18.2 percentage points
- **AUC:** 0.77 (good discrimination)
- **This is significant** because financial data is noisy and hard to predict

---

## 3. FEATURES

### Q: How many features does the model use?
**A:** 74 features across 7 categories:
- Volatility metrics (21 features)
- Return patterns (14 features)
- Volume indicators (6 features)
- Range metrics (7 features)
- Microstructure (10 features)
- Time features (6 features)
- Interactions (2 features)

### Q: What are Yang-Zhang and Rogers-Satchell?
**A:** Advanced volatility estimators:
- **Rogers-Satchell:** Uses Open/High/Low/Close to measure intraday choppiness, ignoring trend direction
- **Yang-Zhang:** Most sophisticated - combines overnight gaps + intraday volatility
- **Why use them:** More accurate than simple volatility because they use more price information (OHLC vs just Close)

### Q: What's the most important feature?
**A:** Based on SHAP analysis, top features are:
1. Recent realized volatility (rvol_12, rvol_24)
2. Yang-Zhang volatility (yz_24)
3. Volume ratios (volume_ratio)
4. Order flow imbalance (ofi_normalized)
These capture current market state and momentum.

### Q: Why use 5-minute bars instead of 1-minute or hourly?
**A:** Trade-off between noise and information:
- **1-minute:** Too noisy, more data but less signal
- **5-minute:** Balanced - smooths noise while preserving patterns (chosen)
- **Hourly:** Too smooth, loses important short-term dynamics
- **5-minute is standard** in high-frequency volatility modeling

---

## 4. METHODOLOGY

### Q: What's your prediction horizon?
**A:** 1 hour ahead (12 bars × 5 minutes = 60 minutes). This is:
- **Short enough** to be predictable
- **Long enough** to be tradeable (time to execute)
- **Practical** for intraday option strategies

### Q: How did you validate the model?
**A:** Three-layer validation:
1. **Single train/test split:** 70/30, time-ordered (Nov 25 cutoff)
2. **4-fold time series CV:** With 2-hour gaps to prevent lookahead bias
3. **Realistic backtest:** 2,607 trades with transaction costs
- All three show consistent ~70% accuracy

### Q: What's cross-validation and why the gaps?
**A:**
- **Cross-validation:** Testing the model on multiple different time periods, not just one
- **Gaps:** 2-hour buffer between train and test prevents "cheating"
  - Without gap: Model could use info from hour 11 to predict hour 12 (data leakage)
  - With gap: Model trained on hours 1-10, tested on hour 13+ (realistic)
- **Result:** More trustworthy performance estimate

### Q: What's probability calibration?
**A:** Adjusting model confidence to match reality:
- **Problem:** Model says "80% confident" but only right 65% of the time
- **Solution:** Isotonic regression calibrates probabilities
- **Result:** Slightly worse Brier score (0.20 vs 0.19) - model was already well-calibrated
- **Still used:** More trustworthy probabilities for position sizing

---

## 5. BACKTESTING

### Q: What are your backtest results?
**A:**
- **Net return:** 97,177% (after costs)
- **Win rate:** 79.2%
- **Sharpe ratio:** 45.57
- **Trades:** 2,607 over 3 months

### Q: Those returns seem too good to be true?
**A:** **You're absolutely right.** Several reasons why live trading would differ:
1. **Slippage:** Backtest assumes exact prices; reality has price impact
2. **Market impact:** Large orders move markets
3. **Liquidity:** Can't always trade when you want
4. **Regime change:** Market behavior can shift
5. **Overfitting:** Model tuned to this specific period
- **Real expectation:** Probably 10-20% of backtest returns in live trading

### Q: What transaction costs did you include?
**A:** 0.05% per trade (5 basis points):
- Covers exchange fees + broker commission
- **Does NOT include:** Slippage, market impact, bid-ask spread
- Conservative real cost: 0.1-0.2% (would reduce returns significantly)

### Q: What's the confidence threshold and why 60%?
**A:** Only trade when model is >60% confident:
- **Without filter (50%):** More trades, lower win rate
- **With filter (60%):** Fewer trades (2,607), higher win rate (79%)
- **60% chosen:** Balances trade frequency vs quality
- **Alternative:** 70% threshold = fewer trades but 82% win rate

---

## 6. RESULTS INTERPRETATION

### Q: What's AUC and why does it matter?
**A:** Area Under ROC Curve - measures discrimination ability:
- **0.5:** Random guessing (coin flip)
- **0.77:** Our model (good)
- **1.0:** Perfect prediction
- **Interpretation:** 77% chance model ranks a random "volatility up" case higher than a random "volatility down" case

### Q: What's Sharpe ratio?
**A:** Risk-adjusted return metric:
- **Formula:** (Return - Risk-Free Rate) / Standard Deviation
- **Our result:** 45.57
- **Realistic range:** 1.0-2.0 is good, >3.0 is excellent
- **45.57 is unrealistic** - indicates backtest may not capture real trading conditions

### Q: What's maximum drawdown?
**A:** Largest peak-to-trough decline:
- **Our result:** -789.65%
- **Meaning:** At worst, strategy was down 789% from peak
- **Issue:** Very high risk - you could lose almost 8x your capital in worst case
- **Real trading:** Would need strict risk management (stop losses, position limits)

### Q: How does performance vary by market regime?
**A:** Tested across three volatility regimes:
- **Low volatility:** 77.3% win rate, 652 trades
- **Medium volatility:** 80.0% win rate, 1,303 trades
- **High volatility:** 79.8% win rate, 652 trades
- **Conclusion:** Model performs consistently across all market conditions (good sign)

---

## 7. IMPLEMENTATION

### Q: How long does it take to train?
**A:** End-to-end timeline:
- **Data loading:** 10-15 minutes (21M trades)
- **Feature creation:** 2-5 minutes
- **Model training:** 1-3 minutes (all 4 models)
- **Cross-validation:** 5-10 minutes
- **Backtesting:** 1-2 minutes
- **Total:** ~20-35 minutes

### Q: Could this run in real-time?
**A:** Yes, with modifications:
- **Current:** Batch processing (all data at once)
- **Needed:** Streaming pipeline (real-time data feed)
- **Inference speed:** <1ms per prediction (LightGBM is fast)
- **Bottleneck:** Feature calculation (need rolling windows)
- **Feasible:** Yes, with proper infrastructure

### Q: What would you need for live trading?
**A:**
1. **Data feed:** Real-time tick data from exchange
2. **Infrastructure:** Low-latency servers, streaming pipeline
3. **Execution:** Connection to broker API
4. **Risk management:** Position limits, stop losses, circuit breakers
5. **Monitoring:** Real-time performance tracking, alerts
6. **Validation:** 3-6 months paper trading first

---

## 8. LIMITATIONS & IMPROVEMENTS

### Q: What are the main limitations?
**A:**
1. **Single symbol:** Only tested on NQ futures (NASDAQ-100)
2. **Single timeframe:** Only 5-minute bars
3. **Time period:** 3 months of data (Sep-Dec 2025)
4. **No regime detection:** Doesn't adapt to market changes
5. **Unrealistic backtest:** Doesn't capture all real-world costs
6. **No news/events:** Ignores fundamental data

### Q: How would you improve this model?
**A:** Priority improvements:
1. **More data:** Train on 2-3 years instead of 3 months
2. **Multiple symbols:** Test on ES, YM, RTY (other futures)
3. **Alternative data:** Add sentiment, news, macroeconomic indicators
4. **Ensemble methods:** Combine multiple models
5. **Adaptive learning:** Retrain periodically on recent data
6. **Better execution modeling:** Include realistic slippage
7. **Regime detection:** Separate models for different market states

### Q: Why not use deep learning/neural networks?
**A:** Considered but decided against:
- **Pros:** Can capture very complex patterns
- **Cons:** Need much more data (years, not months), harder to interpret, prone to overfitting
- **Decision:** Tree-based models (LightGBM) work well with our data size and are more interpretable
- **Future work:** Could try LSTM or Transformers with more data

### Q: What's SHAP and why use it?
**A:** SHapley Additive exPlanations - model interpretability:
- **Purpose:** Explains which features drove each prediction
- **Why important:**
  - Builds trust (not a black box)
  - Helps debug (catch if model is "cheating")
  - Improves features (see what matters)
- **Our insights:** Volatility features dominate, time features less important

---

## 9. TECHNICAL CHOICES

### Q: Why LightGBM over XGBoost?
**A:** Marginal performance edge:
- **AUC:** 0.7705 vs 0.7686 (0.2% better)
- **Speed:** ~2x faster training
- **Memory:** More efficient with large datasets
- **Both are excellent** - could use either in production

### Q: Why 74 features? Isn't that too many?
**A:** Considered feature count:
- **Risk:** Overfitting with too many features
- **Mitigation:** Tree-based models handle high dimensions well, regularization prevents overfitting
- **Validation:** Consistent CV performance suggests not overfitting
- **Alternative:** Could use feature selection (RFECV) to reduce to ~40 features
- **Trade-off:** More features = more information but more complexity

### Q: What's the train/test split strategy?
**A:** Time-series split (NOT random):
- **Train:** Sep 29 - Nov 25 (70%)
- **Test:** Nov 25 - Dec 19 (30%)
- **Critical:** Must preserve time order (can't train on future to predict past)
- **Validation:** Future data never seen during training

---

## 10. PRACTICAL QUESTIONS

### Q: How much capital would you need to trade this?
**A:** Rough estimates:
- **Minimum:** $10,000 (1 contract, proper risk management)
- **Comfortable:** $50,000-100,000 (better diversification)
- **Per trade risk:** 1-2% of capital max
- **Position sizing:** Based on prediction confidence

### Q: What's the expected annual return?
**A:** Conservative estimate:
- **Backtest:** 97,177% over 3 months (unrealistic)
- **Realistic:** 10-20% of backtest = ~10,000-20,000% annually
- **Very conservative:** Assume 90% degradation = 1,000-2,000% annually
- **My estimate:** 50-100% annually if everything works (still very optimistic)
- **Reality:** Unknown until live tested

### Q: What could go wrong in live trading?
**A:** Major risks:
1. **Model stops working:** Market regime change
2. **Execution issues:** Can't get fills at predicted prices
3. **Data problems:** Feed delays, missing data
4. **Technical failures:** Server crashes, network issues
5. **Black swan events:** Extreme market moves model hasn't seen
6. **Overfitting:** Model memorized past, doesn't generalize

### Q: How would you know if the model is failing?
**A:** Monitoring metrics:
- **Win rate drops** below 60% (from 79%)
- **Sharpe ratio** turns negative
- **Drawdown exceeds** 20%
- **Prediction confidence** decreases
- **Actual volatility diverges** from predictions
- **Action:** Stop trading, retrain, investigate

---

## 11. COMPARISON QUESTIONS

### Q: How does this compare to other volatility models?
**A:** Common alternatives:
- **GARCH models:** Traditional econometric, ~60-65% accuracy
- **Simple moving averages:** ~55-60% accuracy
- **Our model:** 70% accuracy (significant improvement)
- **Industry state-of-art:** 75-80% (we're competitive)

### Q: Could you just use VIX instead?
**A:** VIX is different:
- **VIX:** Implied volatility (option market's expectation)
- **Our model:** Realized volatility (actual price movement)
- **Use case:** We predict realized vol; VIX shows implied vol
- **Complement:** Could add VIX as a feature (future improvement)

---

## 12. QUICK FIRE ANSWERS

**Q: Binary classification or regression?**
A: Binary classification (volatility up/down, not exact level)

**Q: What's the target variable?**
A: Will realized volatility 1 hour from now be higher than current volatility? (Yes=1, No=0)

**Q: What programming language?**
A: Python (pandas, scikit-learn, LightGBM)

**Q: What's the data frequency?**
A: 5-minute OHLCV bars

**Q: Training time?**
A: ~3 minutes for all 4 models

**Q: Inference time?**
A: <1 millisecond per prediction

**Q: Most important hyperparameter?**
A: Confidence threshold (60%)

**Q: Biggest challenge?**
A: Loading/processing 21M trades without running out of memory

**Q: Model file size?**
A: ~50MB (includes all models, scaler, metadata)

**Q: Could this work on stocks?**
A: Yes, with retraining on stock data

**Q: Could this work on crypto?**
A: Yes, crypto is even more volatile (might work better)

**Q: What's next?**
A: Paper trading for 3-6 months, then consider live with small capital

---

## KEY TAKEAWAYS FOR PRESENTATION

1. **Goal:** Predict hourly volatility direction with 70% accuracy
2. **Method:** Supervised ML (LightGBM) on 74 engineered features
3. **Data:** 21M futures trades → 16K five-minute bars
4. **Validation:** 3-layer (train/test, CV, backtest)
5. **Results:** 77% AUC, 79% win rate, robust across regimes
6. **Reality check:** Backtest returns unrealistic, live trading will be harder
7. **Next steps:** Paper trading before risking real capital

---

**Remember:** Be honest about limitations. Supervisors appreciate realistic assessments over overpromising!
