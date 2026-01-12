# NSE Options Pricer Platform
## Comprehensive System Documentation

---

## System Overview

The NSE Options Pricer Platform is a comprehensive web-based financial application designed to democratize access to derivatives trading education in Kenya. Built as both an educational tool and a professional-grade options pricing platform, the system integrates advanced quantitative models, artificial intelligence assistance, real-time market data, and mobile money payment infrastructure to create a complete ecosystem for understanding and analyzing options on futures contracts.

The platform addresses a critical gap in Kenya's emerging derivatives market by providing retail investors, institutional traders, and students with sophisticated analytical tools previously accessible only through expensive Bloomberg terminals or proprietary trading systems. By combining the Black-76 pricing model with machine learning-based volatility forecasting, an AI-powered financial advisor, and seamless M-Pesa integration, the system offers a uniquely Kenyan solution to financial education and market participation.

Unlike purely theoretical educational platforms, this system operates on actual NSE futures contract specifications and market data, providing users with realistic simulations and calculations that directly apply to Kenya's live derivatives markets. The platform's token-based economy and wallet system create a sustainable model where users can access advanced features while maintaining low barriers to entry through daily free token allocations.

---

## System Objectives

- **Democratize sophisticated financial analytics** by providing institutional-grade options pricing models and volatility forecasting tools at accessible price points for Kenyan retail investors and students

- **Bridge the knowledge gap** in Kenya's emerging derivatives market by offering AI-powered education through Flavia, a specialized financial advisor that explains complex concepts in contextually relevant language

- **Enable informed risk assessment** through comprehensive Greeks calculations, multi-leg profit/loss analysis, and interactive visualizations that make abstract mathematical relationships tangible and actionable

- **Integrate with local financial infrastructure** by leveraging M-Pesa for seamless wallet top-ups and token purchases, eliminating barriers associated with international payment systems or bank transfers

- **Support evidence-based decision making** through machine learning volatility predictions with confidence intervals, helping users move beyond guesswork when estimating this critical pricing input

- **Foster market literacy and confidence** by providing a sandbox environment where users can experiment with strategies, analyze outcomes, and develop intuition before committing real capital

- **Maintain professional accuracy** by implementing industry-standard Black-76 pricing models calibrated to actual NSE futures contracts with proper fee structures and market conventions

---

## System Architecture

### Technology Stack

#### Backend Infrastructure
- **Framework**: Flask 3.0 (Python 3.8+) with Flask-RESTX for RESTful API development and automatic Swagger documentation
- **Database**: MongoDB 4.6+ for flexible document storage of user accounts, wallets, and transaction history
- **Authentication**: JWT-based (Flask-JWT-Extended) with bcrypt password hashing and token refresh mechanisms
- **Numerical Computing**: NumPy and SciPy for Black-76 implementation and statistical distributions
- **Machine Learning**: Scikit-learn, TensorFlow, StatsModels (ARIMA/GARCH), and ARCH for volatility forecasting ensemble
- **API Integration**: OpenAI API (GPT-4o-mini) for Flavia AI chatbot, M-Pesa Daraja API for payment processing

#### Frontend Architecture
- **HTML5 Semantic Markup**: Server-side rendered templates with Jinja2
- **Styling**: Tailwind CSS utility-first framework for responsive design
- **JavaScript**: Vanilla ES6+ with modular component architecture
- **Visualization**: Plotly.js for interactive 3D heatmaps and 2D profit/loss diagrams
- **State Management**: LocalStorage for client-side persistence of calculator inputs and chat history

#### Security & Deployment
- **CORS Configuration**: Controlled cross-origin resource sharing for API access
- **Environment Variables**: Sensitive credentials stored in `.env` files (API keys, database URIs, M-Pesa secrets)
- **Session Management**: 24-hour server-side sessions with secure cookie handling
- **Input Validation**: Pydantic models for request/response validation with comprehensive error messages
- **Rate Limiting**: Token-based consumption for AI chat to prevent abuse

#### Data Storage & Caching
- **NSE Contract Data**: CSV-based futures contract specifications loaded at startup
- **ML Model Persistence**: Joblib serialization for trained volatility forecasting models
- **Feature Caching**: Zstandard-compressed cache directory for processed time-series features
- **Transaction History**: MongoDB indexing on user_id, status, and timestamps for efficient querying

---

## System Features

### Feature 1: Black-76 Options Pricing Engine

#### Description

The Black-76 Options Pricing Engine is the mathematical core of the platform, implementing the industry-standard Black-76 model (also known as Black's model) specifically designed for pricing European-style options on futures contracts. The engine accepts user-specified inputs including futures price, strike price, time to expiration, risk-free rate, and volatility, then computes theoretical option values for both call and put contracts using closed-form solutions based on the cumulative normal distribution.

The implementation follows the exact mathematical formulation used by professional derivatives desks globally, ensuring calculation accuracy and consistency with industry standards. The engine calculates option prices in real-time as users adjust input parameters, providing immediate feedback on how market conditions affect option valuations. All calculations account for NSE-specific contract specifications including contract size, tick size, and optional fee structures (NSE clearing fees, member fees, IPF levy, and CMA charges totaling 0.085%).

Beyond simple pricing, the engine computes the complete set of Greek risk measures (Delta, Gamma, Vega, Theta, Rho) that quantify how option values respond to changes in underlying variables. This comprehensive output enables users to understand not just what an option is worth, but how its value will evolve as market conditions change.

#### Objective

This feature exists to eliminate the "black box" problem that plagues options education, where learners see final prices without understanding the underlying calculations. By implementing a transparent, mathematically rigorous pricing engine with full Greek calculations, the platform empowers users to develop genuine quantitative intuition rather than relying on memorized rules of thumb. The feature directly addresses the reality that Kenyan derivatives markets lack accessible pricing tools—professional Bloomberg terminals cost thousands of dollars monthly, putting sophisticated analytics beyond reach for most individual investors and educational institutions.

The Black-76 engine also serves as the foundation for all advanced features on the platform. Heatmaps, profit/loss diagrams, and strategy comparisons all depend on rapid, accurate option pricing across hundreds of scenarios. By centralizing this functionality in a robust, tested engine, the platform ensures consistency and reliability throughout the user experience while maintaining the computational efficiency necessary for real-time interactive visualizations.

#### User Interaction

Users access the pricing calculator from the homepage dashboard, where they encounter a streamlined form interface organized into logical sections. The contract selection dropdown presents all 13 available NSE futures contracts (including equities like SCOM, EQTY, KCBG, and indices like N25I), each with detailed specifications automatically loaded from the system database. Upon selecting a contract, the system pre-fills relevant parameters like contract size and current market price where available.

The core pricing inputs are presented with intelligent defaults and validation constraints. The futures price field accepts decimal values with appropriate bounds checking. The strike price selector can either be manually entered or chosen from a dropdown of standard strikes generated around the current futures price. Time to expiration can be specified in calendar days or by selecting from standard expiration months (March, June, September, December) with automatic day calculation to expiry.

The volatility input is presented as a dual-interface: users can manually enter an expected annualized volatility percentage, or click the "Get ML Prediction" button to trigger the machine learning volatility forecasting service. When ML prediction is requested, the system displays a loading indicator, then populates the volatility field with the predicted value along with confidence intervals and model confidence score, helping users understand prediction uncertainty.

An optional "Include NSE Fees" checkbox allows users to add realistic fee structures to the theoretical prices, showing both the pure Black-76 value and the total cost including all market fees with a detailed breakdown (clearing fees, trading member fees, regulatory levies).

Upon clicking "Calculate," the system instantly displays results in a structured output panel showing call and put option prices prominently, followed by a collapsible Greeks section displaying Delta (price sensitivity), Gamma (Delta acceleration), Vega (volatility sensitivity), Theta (time decay), and Rho (interest rate sensitivity) with both numerical values and plain-language interpretations (e.g., "This option will gain KES 0.45 for every KES 1 increase in the futures price").

Users can generate an interactive 3D heatmap by clicking "Generate Heatmap," which creates a price-volatility surface showing how option values change across a range of futures prices (±20% from current) and volatilities (±50% from input), providing immediate visual insight into sensitivity patterns and risk exposures.

#### Screenshot

**[Screenshot Placeholder: Black-76 Options Pricing Calculator interface showing contract dropdown, input fields for futures price/strike/expiry/volatility, ML prediction button, calculate button, and results panel displaying call/put prices with Greeks values]**

---

### Feature 2: Machine Learning Volatility Forecasting

#### Description

The Volatility Forecasting Service implements a sophisticated ensemble machine learning system that predicts future volatility levels for underlying futures contracts based on historical price patterns. The service combines multiple statistical and machine learning models—including ARIMA (AutoRegressive Integrated Moving Average), GARCH (Generalized Autoregressive Conditional Heteroskedasticity), LSTM neural networks (Long Short-Term Memory), and XGBoost (Gradient Boosting)—into a single ensemble that leverages the strengths of each approach while mitigating individual model weaknesses.

The pre-trained model (`volatility_forecaster_v2_enhanced.joblib`) is loaded at application startup and stored in memory for fast inference. When users request a volatility prediction, the service processes historical OHLCV (Open, High, Low, Close, Volume) data through an automated feature engineering pipeline that extracts relevant statistical properties: rolling standard deviations, returns distributions, volume patterns, and price momentum indicators. These engineered features are normalized using StandardScaler and fed into the ensemble model, which produces a point prediction along with calibrated confidence intervals.

The output provides not just a single volatility number, but a comprehensive forecast package including the predicted annualized volatility percentage, upper and lower bounds for the 95% confidence interval, overall model confidence score (0-100%), contributing model weights showing how much each component model influenced the final prediction, forecast horizon in days (1-365), and a timestamp for prediction traceability. This transparency enables users to assess prediction reliability and understand forecast uncertainty.

The service also supports backtesting functionality where users can upload historical data and validate the model's performance across different time periods, examining prediction accuracy metrics such as mean absolute error, root mean squared error, and directional accuracy. For advanced users, a custom data upload endpoint allows analysis of proprietary datasets beyond the platform's built-in NSE contract data.

#### Objective

Volatility is simultaneously the most critical and most challenging input in options pricing—it directly determines option premiums and risk exposures, yet unlike price or time, volatility cannot be directly observed and must be estimated. This feature addresses the fundamental problem that individual investors typically have no systematic approach to volatility estimation, often relying on subjective guesses or blindly accepting broker estimates without understanding their basis.

By providing a data-driven, transparent volatility forecasting tool with explicit confidence intervals, the platform empowers users to make informed assumptions grounded in statistical evidence rather than intuition. The ensemble approach specifically guards against model overfitting and single-algorithm bias, providing more robust predictions than any individual technique. The confidence intervals explicitly communicate forecast uncertainty, teaching users the critical lesson that volatility predictions are probabilistic ranges, not deterministic values.

This feature directly supports better options pricing decisions by allowing users to explore scenarios using both their own volatility assumptions and ML-generated forecasts, comparing how different volatility inputs affect pricing and strategy outcomes. The transparency around model confidence and contributing algorithms builds trust and understanding, transforming volatility forecasting from a mysterious process into an interpretable analytical tool.

#### User Interaction

Users access volatility forecasting directly within the main calculator interface via the "Get ML Prediction" button adjacent to the volatility input field. Upon clicking, the system displays a loading animation and sends an API request containing the selected contract symbol and desired forecast horizon (typically defaulting to 30 days ahead, matching common option expiration cycles).

Within 1-3 seconds, the system returns the forecast and automatically populates the volatility input field with the predicted value. A small info icon appears next to the field; hovering over or clicking it reveals a detailed forecast breakdown panel showing the predicted volatility percentage (e.g., "18.5%"), the 95% confidence interval range (e.g., "15.2% - 21.8%"), model confidence score (e.g., "78%"), and a visual breakdown of contributing models represented as a horizontal stacked bar chart showing relative weights (e.g., GARCH 35%, XGBoost 30%, LSTM 25%, ARIMA 10%).

For users seeking deeper analysis, a dedicated Volatility Forecasting page (accessible via main navigation) provides an expanded interface. Here, users can select a contract, specify custom forecast horizons from 1 to 365 days, and view historical volatility trends plotted as line charts showing realized volatility over the past 90 days. The page includes a comparison section where users can run multiple forecasts with different horizons and view them side-by-side, helping identify whether volatility is expected to increase or decrease over time.

Advanced users can access the backtesting tool by uploading historical CSV data (containing date, open, high, low, close, volume columns) and specifying an evaluation period. The system runs the model against historical data, generates predictions, compares them to realized volatility, and displays accuracy metrics along with a scatter plot showing predicted vs. actual values, enabling validation of model performance on specific securities or time periods.

Throughout all interfaces, plain-language explanations accompany technical outputs. For example, a 95% confidence interval of "15-22%" is supplemented with text like "The model is 95% confident that volatility will fall between 15% and 22%, meaning there's a 5% chance actual volatility could be outside this range." This educational approach ensures users understand not just the numbers, but their practical meaning for options trading decisions.

#### Screenshot

**[Screenshot Placeholder: Volatility Forecasting interface showing contract selection, forecast horizon slider, predicted volatility display with confidence intervals, contributing models breakdown chart, and historical volatility trend line graph]**

---

### Feature 3: Interactive 3D Heatmap Visualization

#### Description

The Interactive Heatmap Visualization generates three-dimensional surface plots that display how call and put option prices vary simultaneously across ranges of futures prices and implied volatility levels. Using Plotly.js rendering, the system creates two separate heatmaps (one for calls, one for puts) where the x-axis represents futures prices spanning ±20% from the user's input price, the y-axis represents implied volatility ranging from ±50% of the input volatility, and the z-axis (color intensity) represents the resulting option value calculated using the Black-76 model at each coordinate point.

The heatmaps employ intuitive color schemes: blue gradients for call options (lighter blues indicating lower values, darker blues for higher values) and red gradients for put options (following the same intensity logic). A yellow star marker indicates the user's current input position on the surface, providing immediate visual reference for "where you are" relative to the broader price-volatility landscape.

The visualization is fully interactive—users can hover over any point on the surface to see exact futures price, volatility percentage, and option value at that coordinate. The 3D plots can be rotated by clicking and dragging, allowing examination from different angles to better understand the surface topology. Zoom controls enable focus on specific regions of interest, and a reset button returns to the default view. A toggle between 3D surface and 2D contour projections accommodates different visualization preferences and screen sizes.

Each heatmap calculation involves computing Black-76 prices for a 20x20 grid (400 calculations per heatmap, 800 total for calls and puts), performed server-side for computational efficiency and returned as JSON arrays that Plotly.js renders client-side. The generation typically completes in under 2 seconds, providing responsive feedback even for computationally intensive visualizations.

#### Objective

Options pricing involves multiple interacting variables whose relationships are highly nonlinear—small changes in some regions produce dramatic price effects, while other regions show minimal sensitivity. Traditional tabular presentations or single-variable sensitivity charts fail to capture these complex multidimensional relationships, leaving users with fragmented understanding that hinders intuitive risk assessment.

This feature transforms abstract mathematical relationships into concrete visual patterns that align with human spatial reasoning capabilities. By seeing the "shape" of option value surfaces, users develop intuitive understanding of key concepts like volatility skew, price-volatility correlation, and non-linear risk exposures. The visualization makes immediately apparent insights that would require extensive calculation to discover analytically, such as how volatility impacts become progressively stronger as options move toward at-the-money strike prices.

The interactive nature specifically supports exploratory learning—users can form hypotheses ("what happens if volatility increases?"), manipulate the visualization, and immediately observe outcomes, creating an active learning loop superior to passive reading of explanations. The visual comparison between call and put heatmaps reinforces understanding of put-call parity and symmetries in options pricing, while differences in surface topology highlight where the two contract types respond differently to market conditions.

#### User Interaction

After entering pricing inputs and clicking "Calculate" in the main calculator interface, users see a "Generate Heatmap" button below the pricing results. Clicking this button triggers a loading animation (as the system computes 800 price points) followed by the appearance of two side-by-side heatmap panels labeled "Call Option Price Heatmap" and "Put Option Price Heatmap."

Each heatmap occupies approximately half the screen width (responsive to browser size) and displays a 3D surface plot with clearly labeled axes: "Futures Price (KES)" on the x-axis, "Implied Volatility (%)" on the y-axis, and a color scale legend on the right indicating option values in KES. The user's current inputs are marked with a prominent yellow star on each surface, making it easy to locate the calculated price within the broader landscape.

Users can interact with the visualizations in multiple ways:
- **Hover**: Moving the cursor over any point displays a tooltip showing exact values: "Futures Price: 102.5, Volatility: 22%, Call Value: 4.32"
- **Rotate**: Click-dragging rotates the 3D surface to view from different angles, helping understand surface topology
- **Zoom**: Scroll wheel or pinch gestures zoom in/out, enabling detailed examination of specific regions
- **Pan**: Shift-drag moves the plot without rotating, useful for repositioning after zoom
- **2D Mode**: A toggle button switches between 3D surface and 2D contour projection for users preferring flat contour lines over 3D rendering

Below each heatmap, interpretive text provides context: "This surface shows how call option values change as futures prices and volatility vary. Notice how values increase sharply when moving up-right (higher price and volatility), demonstrating the compound effect of both factors. The steepest part of the surface occurs near your current strike price (marked with a star), indicating maximum sensitivity to price changes in this region."

A "Compare Calls vs Puts" button overlays both surfaces on a single plot with semi-transparent rendering and distinct color schemes, enabling direct visual comparison of how the two contract types respond differently to the same market conditions. This comparison view particularly highlights how calls benefit more from price increases while puts gain from price decreases, and how volatility increases benefit both contract types (though by different amounts depending on moneyness).

For educational purposes, the interface includes an "Explain This Chart" expandable section that provides plain-language interpretation of what the visualization reveals, including concepts like: "The blue intensity shows call option value—darker blue means more expensive. Notice how the surface gets steeper as volatility increases (moving up), showing that high-volatility options are more sensitive to price changes. The relatively flat region at low prices and low volatility indicates that deep out-of-the-money options with low volatility have minimal value."

#### Screenshot

**[Screenshot Placeholder: Side-by-side 3D heatmaps showing Call and Put option prices across futures price and volatility ranges, with color-coded surfaces (blue for calls, red for puts), yellow star marking current position, axis labels, and color scale legends]**

---

### Feature 4: Comprehensive Greeks Calculator and Dashboard

#### Description

The Greeks Dashboard calculates and presents all five primary option Greeks—Delta (Δ), Gamma (Γ), Vega (ν), Theta (Θ), and Rho (ρ)—that quantify how option values respond to changes in underlying market variables. Each Greek is computed analytically from the Black-76 model using closed-form partial derivative formulas, ensuring mathematical precision and consistency with the primary pricing calculations.

The dashboard presents each Greek in a dedicated card that includes four components: the numerical value with appropriate units (e.g., Delta: +0.65), a visual indicator showing magnitude and direction (positive/negative via color coding and gauge charts), a plain-language interpretation explaining what the number means in practical terms, and a contextual assessment of whether the value is considered low, moderate, or high for that particular Greek.

**Delta** measures the rate of change in option value relative to changes in the underlying futures price, displayed as a decimal (e.g., +0.65 means the option gains KES 0.65 for every KES 1 increase in futures price). The dashboard visualizes Delta using a horizontal bar chart ranging from -1 to +1, with call options typically showing positive Delta and puts showing negative Delta.

**Gamma** quantifies how Delta itself changes as the underlying price moves, serving as an "acceleration" measure for option sensitivity. Displayed as a small decimal (e.g., 0.015), Gamma is highest for at-the-money options and decreases as options move in- or out-of-the-money. The dashboard includes a gauge chart showing whether Gamma is low/moderate/high relative to typical values.

**Vega** measures sensitivity to changes in implied volatility, displayed in KES terms (e.g., Vega: 2.35 means the option gains KES 2.35 for every 1% increase in volatility). A bar chart shows Vega magnitude with explanatory text highlighting that all options have positive Vega (benefit from volatility increases) but at-the-money options have higher Vega than deep in- or out-of-the-money options.

**Theta** quantifies time decay, showing how much value the option loses per day as expiration approaches, displayed as a negative number (e.g., Theta: -0.08 means the option loses KES 0.08 per day). A declining line chart visualizes the accelerating time decay as expiration nears, with explanatory notes about how time decay accelerates for at-the-money options.

**Rho** measures sensitivity to risk-free interest rate changes, displayed in KES terms per 1% rate change (e.g., Rho: 0.52). While typically the least impactful Greek in stable rate environments, the dashboard includes it for completeness and provides context about when rate sensitivity becomes important (longer-dated options, high-interest-rate environments).

Each Greek calculation accounts for the specific NSE contract parameters including contract size and market conventions. The dashboard automatically updates all Greeks whenever the user modifies any pricing input, demonstrating the dynamic nature of these risk measures and how they evolve as market conditions change.

#### Objective

The Greeks represent the mathematical language of options risk management—professional traders use these measures constantly to monitor exposures, hedge positions, and understand how portfolios will respond to market movements. However, most educational resources present Greeks as abstract mathematical concepts divorced from practical application, leaving learners unable to translate Greek values into actionable insights.

This feature bridges the theory-practice gap by presenting Greeks not as obscure derivatives but as practical risk indicators with clear interpretations and visual representations that aid comprehension. By showing how Greeks change dynamically as users adjust inputs, the dashboard reinforces understanding of the relationships between market conditions and risk exposures. The plain-language interpretations specifically address the common problem where users see a number like "Delta: 0.65" but don't know whether that's high, low, good, or bad for their situation.

The comprehensive presentation of all five Greeks together enables users to develop a holistic view of option risk rather than focusing myopically on price alone. For example, an option might appear attractively priced but have severely negative Theta (rapid time decay), or might show attractive Delta but concerning Gamma (unstable sensitivity). By surfacing all risk dimensions simultaneously, the dashboard promotes more sophisticated risk assessment aligned with professional trading practices.

The feature also serves an educational objective of demystifying Greek calculations—by showing that these measures update automatically from the same inputs used for pricing, users learn that Greeks aren't separate, mysterious quantities but simply different aspects of how the pricing model behaves, making them less intimidating and more approachable.

#### User Interaction

The Greeks Dashboard appears automatically below the option pricing results after users click "Calculate" in the main calculator interface. The dashboard organizes the five Greeks into a grid layout with clear visual hierarchy—each Greek occupies a distinct card with consistent structure but unique styling to aid differentiation.

Users can interact with the dashboard in several ways:

**Hover Exploration**: Hovering over any Greek's card reveals an expanded tooltip with additional detail, including the mathematical definition (e.g., "Delta = ∂V/∂S, the partial derivative of option value with respect to futures price"), typical value ranges for that Greek, and examples of how traders use that particular measure in practice.

**What-If Mode**: A "What-If Analysis" toggle button activates an interactive mode where users can use mini sliders directly within each Greek's card to simulate changes. For example, within the Delta card, a futures price slider allows users to see how Delta would change if the underlying moved ±10%, with the calculation updating in real-time without requiring full form resubmission. Similarly, within the Vega card, a volatility slider demonstrates how Vega changes with different volatility levels.

**Greeks Comparison**: For users analyzing multiple options simultaneously, a "Compare" button saves the current Greek values and allows adding additional options (different strikes, expirations, or option types) to build a comparison table showing Greeks side-by-side. This is particularly valuable for spread strategies where understanding the net Greeks of the combined position is essential.

**Educational Annotations**: Each Greek's card includes a small "?" icon that, when clicked, opens a modal dialog with a comprehensive explanation including: definition, formula, interpretation guidelines, typical values and what they mean, real-world examples of how the Greek impacts trading decisions, and common strategies that target specific Greek exposures (e.g., "Calendar spreads profit from Theta decay differences between expirations").

**Visual Indicators**: Beyond numerical values, each Greek includes contextual visual cues:
- Delta: Green for positive (calls), red for negative (puts), with saturation indicating proximity to ±1
- Gamma: Color intensity shows whether Gamma is near its maximum (at-the-money) or minimal (deep in/out)
- Vega: Bar length visually represents magnitude, with annotations showing peak Vega occurs near at-the-money
- Theta: Red highlighting emphasizes that this is a cost/decay factor, with darker red for rapidly decaying options
- Rho: Subtle blue coloring with magnitude indicator, noting this is typically less critical than other Greeks

**Time Evolution Display**: A timeline toggle shows how Greeks will evolve over the remaining life of the option, plotting projected Greek values against time-to-expiration. This is particularly valuable for understanding how Theta accelerates and Gamma peaks as expiration approaches, and how Delta approaches either 0 or 1 (depending on in/out-of-the-money status).

The entire Greeks Dashboard is responsive to the main calculator inputs—any change to futures price, strike, volatility, or time-to-expiration immediately triggers Greek recalculation and visual update, providing real-time feedback on how risk exposures shift with market conditions. This responsiveness reinforces the critical lesson that Greeks are dynamic measures that change constantly, not static properties of an option.

#### Screenshot

**[Screenshot Placeholder: Greeks Dashboard showing five cards for Delta/Gamma/Vega/Theta/Rho, each displaying numerical value, visual gauge/chart, plain-language interpretation, and magnitude indicator (low/moderate/high). Dashboard shows both call and put Greeks side-by-side with color-coded differentiation.]**

---

### Feature 5: Multi-Leg Profit/Loss Strategy Analyzer

#### Description

The Multi-Leg Profit/Loss (P&L) Analyzer is a comprehensive strategy modeling tool that enables users to construct and analyze complex options positions involving multiple simultaneous contracts. Users can build positions containing up to 10 separate "legs," where each leg represents either buying or selling a call or put option at a specified strike price, expiration date, and quantity. The system calculates the combined profit/loss profile for the entire position across a range of possible underlying prices at expiration, accounting for all premium payments and receipts, and generates an interactive visualization showing the complete payoff diagram.

The analyzer supports both custom strategy construction (where users manually define each leg) and pre-defined strategy templates including common approaches such as:
- **Vertical Spreads**: Bull call spreads, bear put spreads, bull put spreads, bear call spreads
- **Straddles and Strangles**: Long/short straddles (same strike), long/short strangles (different strikes)
- **Calendar Spreads**: Buying and selling options at different expirations
- **Iron Condors**: Four-leg limited-risk strategies combining put and call spreads
- **Butterfly Spreads**: Three-leg strategies targeting specific price ranges
- **Collars**: Protective combinations of stock (simulated as futures) with puts and calls
- **Ratio Spreads**: Unequal quantities of options at different strikes

For each strategy configuration, the system calculates:
- **Net Debit/Credit**: Total upfront cost or income from entering the position
- **Maximum Profit**: Highest possible gain if the underlying moves favorably
- **Maximum Loss**: Worst-case scenario loss
- **Breakeven Point(s)**: Underlying price(s) at which the position neither profits nor loses
- **Probability of Profit**: Statistical likelihood of expiring with any profit (based on assumed volatility)
- **Risk/Reward Ratio**: Maximum loss divided by maximum profit

The P&L visualization plots profit (positive y-axis values) and loss (negative y-axis values) against underlying prices (x-axis), creating a payoff curve that shows exactly how the position performs at every possible price level. Breakeven points are marked with vertical dashed lines, maximum profit/loss levels are indicated with horizontal reference lines, and the current underlying price is highlighted with a contrasting color to show where the market currently stands relative to the strategy's optimal zone.

#### Objective

Real-world options trading rarely involves single isolated options—professional strategies typically combine multiple positions to target specific market views while managing risk exposures. However, understanding how multiple options interact to create a combined payoff profile requires complex calculations that are error-prone and time-consuming when performed manually. This creates a significant barrier for retail investors who may understand individual options but struggle to design and analyze multi-leg strategies.

This feature democratizes sophisticated strategy analysis by automating the complex mathematics of position combining, enabling users to focus on strategy design and market assessment rather than calculation mechanics. By providing instant visual feedback on how strategy parameters affect payoffs, the analyzer supports iterative refinement—users can adjust strikes, quantities, or expirations and immediately see how the changes impact maximum profit, maximum loss, and breakeven points.

The pre-defined strategy templates specifically address the problem of "not knowing what you don't know"—many retail investors are unaware of common strategy archetypes that might suit their market views. By providing accessible templates with explanatory descriptions, the feature introduces users to proven approaches they can then customize and adapt. The strategy comparison capability enables objective evaluation of trade-offs between aggressive and conservative approaches, helping users align strategy selection with their risk tolerance.

From an educational perspective, the P&L analyzer makes abstract strategy concepts concrete and interactive. Seeing how a bull call spread's payoff diagram differs from a long call, or how an iron condor creates a "sweet spot" profit zone with limited losses outside that range, builds intuitive understanding far more effectively than textbook descriptions. The feature transforms strategy learning from passive memorization to active experimentation.

#### User Interaction

Users access the P&L Analyzer through a dedicated page in the main navigation menu. The interface is organized into three primary sections: Strategy Builder (left panel), Analysis Results (center panel), and Visualization (right panel).

**Strategy Builder Panel**:
Users begin by choosing between "Custom Strategy" and "Template Strategy" tabs. In Custom mode, users click "Add Leg" to create each position component. For each leg, a form appears with:
- **Action**: Dropdown selecting "Buy" or "Sell"
- **Type**: Dropdown selecting "Call" or "Put"
- **Strike Price**: Numerical input or dropdown of standard strikes
- **Expiration**: Date picker or dropdown of standard expiration cycles
- **Quantity**: Integer input for number of contracts
- **Premium**: Automatically calculated via Black-76 based on other parameters, or manually override if analyzing existing positions

As legs are added, a summary list displays all components with quick edit/delete buttons. A visual indicator shows whether the position results in a net debit (user pays to enter) or net credit (user receives premium upfront).

In Template mode, users select from a gallery of pre-defined strategies displayed as cards with representative payoff diagram thumbnails and brief descriptions. Upon selecting a template (e.g., "Iron Condor"), the system pre-populates default strikes and quantities optimized for the current underlying price, which users can then customize if desired.

**Analysis Results Panel**:
Once at least one leg is defined, the system automatically calculates and displays:
- **Position Summary**: Number of legs, net debit/credit, total contracts
- **Risk Metrics**: Maximum profit (with underlying price at which it occurs), maximum loss (with price), risk/reward ratio
- **Breakeven Analysis**: All breakeven prices listed with explanatory text (e.g., "Break even at 105.50 and 118.20")
- **Probability Estimate**: Based on current volatility, estimated likelihood of expiring profitable (with methodology explanation)
- **Greeks Summary**: Net portfolio Delta, Gamma, Vega, Theta showing overall directional bias and risk exposures

Each metric includes a hover tooltip with interpretation guidance (e.g., "Risk/Reward Ratio of 1:3 means you risk KES 1 to potentially make KES 3, favorable for this type of position").

**Visualization Panel**:
The interactive P&L diagram plots the combined payoff curve with:
- **X-axis**: Underlying price range from approximately -30% to +30% of current price
- **Y-axis**: Profit/loss in KES
- **Payoff Curve**: Solid line showing P&L at each price point, color-coded (green above breakeven, red below)
- **Breakeven Lines**: Vertical dashed lines at breakeven price(s)
- **Max Profit/Loss Lines**: Horizontal dashed lines showing profit/loss limits
- **Current Price Marker**: Vertical solid line showing where the market currently stands

Users can interact with the visualization by:
- **Hover**: Moving the cursor along the payoff curve displays a tooltip showing exact underlying price and P&L at that point
- **Zoom**: Click-drag to select a region for zoomed-in detail
- **Toggle Components**: Checkboxes allow showing/hiding individual leg payoffs (as faint lines) overlaid on the combined position, helping understand how each component contributes
- **Comparison Mode**: Users can save multiple strategies and overlay their payoff curves on the same chart with different colors, enabling side-by-side evaluation

**Strategy Comparison Feature**:
Below the main visualization, a "Compare Strategies" button opens an expanded view where users can load two or more strategies simultaneously (either from saved templates or custom-built positions). The system displays a comparison table showing all key metrics side-by-side:

| Metric | Strategy A | Strategy B | Strategy C |
|--------|-----------|-----------|-----------|
| Net Cost | -KES 500 | -KES 350 | +KES 100 |
| Max Profit | KES 1200 | KES 800 | KES 600 |
| Max Loss | -KES 500 | -KES 350 | -KES 400 |
| Breakeven | 108.5 | 106.0, 112.0 | 104.5, 114.5 |
| Risk/Reward | 1:2.4 | 1:2.3 | 1:1.5 |

Below the table, overlaid P&L curves show the strategies' payoff profiles on a single chart, with a legend identifying each curve. This comparison view makes it immediately obvious which strategy offers the best profit potential, which has the lowest risk, and which provides the most favorable breakeven conditions, enabling informed strategy selection based on user priorities.

**Educational Guidance**:
Throughout the analyzer, contextual help is embedded:
- Each template includes a "Strategy Explanation" expandable section describing when to use that strategy, what market view it reflects, and key risks/benefits
- An "Analyze This Strategy" button generates AI-powered commentary (via Flavia) explaining the strategy's characteristics and whether it's appropriate given current market conditions
- A "Strategy Library" link opens documentation showing payoff diagrams and characteristics of 20+ common strategies with usage guidelines

The analyzer saves strategies to the user's account, allowing them to build a personal library of positions to revisit, modify, or reference when planning actual trades.

#### Screenshot

**[Screenshot Placeholder: Multi-Leg P&L Analyzer showing three-column layout with Strategy Builder (left) displaying leg inputs for an iron condor, Analysis Results (center) showing max profit/loss/breakeven metrics, and Visualization (right) displaying interactive P&L diagram with breakeven lines and current price marker]**

---

### Feature 6: Flavia AI Financial Assistant

#### Description

Flavia is an AI-powered financial assistant specifically trained and contextualized for NSE options and futures trading. Built on OpenAI's GPT-4o-mini model with custom system prompts and context injection, Flavia provides conversational support for understanding options concepts, interpreting platform calculations, analyzing strategies, and answering questions about Kenyan derivatives markets.

The chatbot maintains conversation history (up to the last 20 messages) to provide contextually relevant responses that reference earlier parts of the discussion. When users ask questions, Flavia can incorporate real-time data from the platform—such as current pricing calculations, volatility forecasts, or market status—into responses, creating a seamless integration between the analytical tools and the conversational interface.

Flavia's knowledge base covers:
- **Options Theory**: Black-76 and Black-Scholes models, Greeks definitions and applications, volatility concepts (historical vs implied), time decay mechanics, intrinsic vs extrinsic value
- **Strategy Guidance**: When to use different strategies, how to construct spreads/straddles/condors, risk management approaches, position sizing principles
- **NSE-Specific Information**: NSE trading hours and market conventions, NSE futures contract specifications, Kenyan risk-free rates and how they're determined, regulatory considerations (CMA oversight)
- **Technical Analysis**: Support/resistance concepts, volatility analysis techniques, trend identification
- **Platform Usage**: How to use calculator features, interpreting heatmaps, understanding Greeks dashboard output, using the P&L analyzer

The chatbot interface includes a "Suggested Questions" feature that displays common queries users can click to immediately ask, including topics like "What are the Greeks?", "How does volatility affect option prices?", "What's the difference between a call and put?", and "Explain bull call spreads."

Flavia operates on a token-based consumption model where each message sent costs 1 chat token from the user's wallet. Users receive 4 free tokens daily automatically, and can purchase additional tokens in packages ranging from 100 tokens (KES 50) to 10,000 tokens (KES 2,500) with volume discounts. This model ensures sustainability while maintaining accessibility through free daily allocations.

#### Objective

Financial education faces a fundamental challenge: textbooks and static documentation can't answer the specific questions learners have at their moment of confusion, and human tutors are expensive and not available 24/7. This creates frustration where users encounter a concept they don't understand, search through documentation unsuccessfully, and ultimately give up or make decisions based on incomplete understanding.

Flavia addresses this by providing instant, personalized explanations available whenever confusion arises. The AI can adapt explanations to the user's apparent sophistication level, provide examples relevant to their current task, and iteratively clarify concepts through back-and-forth dialogue until understanding is achieved. This on-demand learning support dramatically reduces friction in the educational journey.

The platform-specific context awareness is particularly valuable—Flavia can say "Looking at your current heatmap, notice how the call option values (the blue surface) increase more steeply as you move toward the upper-right corner..." rather than providing generic explanations divorced from the user's immediate experience. This contextualization makes abstract concepts concrete and immediately applicable.

The token-based model serves multiple objectives: it creates a sustainable revenue stream to support ongoing platform development while keeping costs extremely low for typical usage (4 free daily tokens support substantive daily learning), it gently discourages low-quality queries that would degrade the experience, and it teaches users to formulate thoughtful questions rather than treating AI as a chat toy, ultimately improving learning outcomes.

From a market development perspective, Flavia helps overcome the knowledge barriers that prevent broader derivatives market participation in Kenya. By making sophisticated financial education accessible at minimal cost, the platform supports the CMA's objectives of developing informed investor bases capable of participating responsibly in complex financial markets.

#### User Interaction

Users access Flavia through a dedicated Chatbot page in the main navigation, or via quick-access floating chat button visible on all platform pages. The interface presents a clean messaging layout similar to modern chat applications, with user messages right-aligned in blue bubbles and Flavia's responses left-aligned in gray bubbles.

**Starting a Conversation**:
Upon entering the chat page, users see a welcome message from Flavia: "Hello! I'm Flavia, your NSE options trading assistant. I can help you understand options pricing, strategies, Greeks, and how to use this platform. What would you like to know?" Below this, a grid of "Suggested Questions" appears as clickable chips covering common topics. Users can click any suggestion to immediately send that question, or type their own question in the input field at the bottom.

**Sending Messages**:
The message input is an auto-expanding textarea that grows as users type longer questions. A character counter shows remaining space (up to 1000 characters per message). The "Send" button displays the token cost ("Send - 1 token") and is disabled if the user has zero tokens, instead showing "Get More Tokens" linking to the wallet page.

When users send a message, it immediately appears in the conversation thread with a "Sending..." indicator. Within 2-5 seconds (depending on query complexity), Flavia's response appears with a typing animation, making the interaction feel conversational rather than transactional.

**Response Quality**:
Flavia's responses are structured and comprehensive:
- **Direct Answer**: Clearly addresses the specific question asked
- **Context**: Provides relevant background or related concepts
- **Examples**: Includes concrete numerical examples when explaining calculations or strategies
- **Next Steps**: Often suggests related questions or platform features to explore
- **Platform Integration**: When relevant, includes statements like "You can see this in action by going to the P&L Analyzer and selecting the 'Bull Call Spread' template"

For complex questions, Flavia breaks responses into logical sections with bold headers, bullet points, and step-by-step explanations. For conceptual questions, responses include analogies and plain-language descriptions before introducing technical terminology.

**Conversation Continuity**:
Flavia maintains context across messages, enabling natural follow-up questions. For example:
- User: "What is Delta?"
- Flavia: [Explains Delta in detail]
- User: "How does it change as the option moves in-the-money?"
- Flavia: [Responds understanding "it" refers to Delta from previous message, explains Delta behavior across moneyness levels]

This context awareness extends up to 20 messages back, creating coherent multi-turn discussions rather than isolated Q&A pairs.

**Token Management**:
At the top of the chat interface, a status bar displays "Available Tokens: 15 | Daily Free: 2/4 used". When token balance runs low (below 5), a gentle notification appears: "You're running low on tokens. You'll receive 4 more free tokens tomorrow, or you can purchase more anytime." A "Buy Tokens" button links directly to the wallet page.

When users exhaust their tokens mid-conversation, the send button becomes disabled and displays "No tokens remaining. Get more to continue chatting." However, the conversation history remains accessible, allowing users to review past exchanges without consuming tokens.

**Additional Features**:
- **Copy Response**: A small copy icon appears on each Flavia response, allowing users to copy text for notes or sharing
- **Rate Response**: Thumbs up/down icons let users provide feedback on response quality (data used to improve system prompts)
- **Clear Conversation**: A "New Conversation" button clears history, useful when switching topics entirely
- **Export Chat**: Users can download conversation history as a text file for offline reference
- **Search History**: A search bar lets users find past exchanges containing specific keywords across all saved conversations

**Educational Nudges**:
If Flavia detects misunderstandings in user questions (e.g., confusing calls and puts, or asking about features that don't exist), responses gently correct the misconception: "I notice you mentioned selling a call to benefit from price increases—actually, selling a call benefits from price decreases or stability. Buying a call benefits from price increases. Would you like me to explain the difference?"

Similarly, if users ask very basic questions repeatedly, Flavia may suggest: "It seems you're learning the fundamentals of options. Would you like me to provide a structured learning path covering key concepts in order? I can guide you through pricing basics, Greeks, then strategies."

#### Screenshot

**[Screenshot Placeholder: Flavia AI chat interface showing conversation history with message bubbles (user in blue, Flavia in gray), suggested question chips at top, message input field with character counter and token cost indicator at bottom, and token balance status bar displaying "Available Tokens: 15 | Daily Free: 2/4 used"]**

---

### Feature 7: M-Pesa Integrated Wallet System

#### Description

The Wallet System provides comprehensive financial management capabilities integrated directly with Kenya's M-Pesa mobile money platform. Users maintain a digital wallet within the platform storing two types of value: cash balance (in Kenyan Shillings) used for potential future features like trade execution or premium services, and chat tokens used to access Flavia AI assistance.

The wallet implementation uses Safaricom's Daraja API 2.0 for M-Pesa integration, specifically leveraging the STK Push (Lipa Na M-Pesa Online) capability that initiates payment prompts directly on users' phones without requiring manual till number entry or USSD codes. This creates a seamless, native mobile money experience aligned with how Kenyans already interact with financial services.

**Core Wallet Features**:
- **Balance Tracking**: Real-time display of cash balance (KES) and available chat tokens
- **Transaction History**: Paginated, searchable history of all wallet activities including deposits, purchases, and token consumption
- **M-Pesa Deposits**: Instant wallet top-ups via STK Push with amounts from KES 1 to KES 150,000
- **Token Purchases**: Conversion of wallet cash balance into chat tokens using tiered pricing with volume discounts
- **Daily Token Grants**: Automatic allocation of 4 free tokens every 24 hours per user
- **Transaction Status Tracking**: Real-time monitoring of pending M-Pesa transactions with automatic status updates

**M-Pesa Integration Architecture**:
The system implements a complete Daraja API flow:
1. **Authentication**: OAuth token management with 50-minute refresh cycle, automatic renewal before expiration
2. **STK Push Initiation**: User provides phone number and amount → system generates transaction → Safaricom sends payment prompt to phone
3. **User Confirmation**: User enters M-Pesa PIN on their phone to authorize payment
4. **Callback Processing**: Safaricom sends transaction result to platform webhook → system updates wallet balance and transaction status
5. **Confirmation**: User sees updated balance and transaction marked as "Completed"

The implementation handles all M-Pesa-specific requirements including phone number format normalization (supporting 07XXXXXXXX, 254XXXXXXXX, and +254XXXXXXXX formats), amount validation (within Safaricom limits), duplicate transaction prevention, and timeout handling (30-second countdown for user to complete payment on phone).

**Token Pricing Structure**:
The platform offers five token packages with progressively larger volume discounts:
- **100 tokens**: KES 50 (KES 0.50 per token) - baseline price
- **500 tokens**: KES 200 (KES 0.40 per token, 20% discount) - most popular tier
- **1,000 tokens**: KES 350 (KES 0.35 per token, 30% discount)
- **5,000 tokens**: KES 1,500 (KES 0.30 per token, 40% discount) - bulk user tier
- **10,000 tokens**: KES 2,500 (KES 0.25 per token, 50% discount) - maximum discount for power users

A custom amount calculator allows users to input any token quantity and see the dynamically calculated price with applicable discount, enabling flexible purchasing beyond preset packages.

**Transaction Management**:
All wallet activities are logged in a MongoDB collection with comprehensive metadata:
- **Transaction Types**: Deposit (M-Pesa top-up), payment (token purchase), refund (if M-Pesa fails), grant (daily free tokens)
- **Status Tracking**: Pending (initiated but not confirmed), completed (successful), failed (M-Pesa rejection), cancelled (user abandoned)
- **M-Pesa Details**: Receipt number, checkout request ID, merchant request ID, phone number used
- **Timestamps**: Creation time, update time, completion time
- **Amounts**: Transaction value in KES, tokens involved (for purchases/grants)

Users can filter transaction history by type, status, or date range, and export statements as CSV files for personal record-keeping.

#### Objective

Financial accessibility is a critical barrier to participation in sophisticated financial services—requiring credit cards, international payment systems, or bank transfers excludes the majority of Kenyan retail investors who conduct most financial transactions via M-Pesa. By integrating natively with M-Pesa, the platform meets users where they already are, eliminating payment friction that would otherwise prevent platform adoption.

The token-based economy achieves multiple strategic objectives simultaneously. First, it creates a sustainable revenue model that allows the platform to offer core pricing and analytical features for free while monetizing the high-marginal-cost AI assistance feature. Second, the daily free token allocation ensures accessibility—even users with zero cash can engage with Flavia daily for basic learning needs, preventing complete exclusion based on ability to pay. Third, volume discounts incentivize larger purchases that improve user lifetime value while still offering fair pricing at every tier.

The comprehensive transaction history serves both operational and educational purposes. Operationally, it provides full transparency and record-keeping for financial compliance and user trust. Educationally, seeing a history of token consumption helps users understand their learning investment and creates positive reinforcement ("I've asked 50 questions and learned so much") that encourages continued engagement.

The seamless STK Push experience specifically addresses a common friction point in Kenyan digital services—requiring users to manually navigate USSD menus or remember till numbers creates abandonment. By initiating the payment prompt automatically, the platform reduces friction to a single M-Pesa PIN entry, maximizing conversion rates and user satisfaction.

From a market development perspective, demonstrating that sophisticated financial platforms can integrate seamlessly with local payment infrastructure sets a precedent for other fintech services, showing that international technical standards (RESTful APIs, JWT authentication) and local mobile money systems can coexist productively.

#### User Interaction

Users access the Wallet page through the main navigation menu or via quick-access wallet icon in the page header (displaying current token count). The wallet interface is organized into three tabs: Overview, Deposit, and Transactions.

**Overview Tab**:
The landing view displays a dashboard with two prominent balance cards:
- **Cash Balance Card**: Shows current KES balance in large, bold text with a green background. Below the balance, a "Deposit via M-Pesa" button initiates top-ups. A small info icon explains "This balance can be used to purchase chat tokens or for future platform features."
- **Token Balance Card**: Shows available chat tokens with a blue background. Below, text states "Daily Free: 3/4 used" showing today's free token consumption. A "Buy Tokens" button opens the purchase interface. A countdown timer shows "Next free tokens in: 8h 23m"

Below the balance cards, a quick-stats section displays:
- Total tokens used (lifetime): 847 tokens
- Total spent: KES 1,250
- Member since: May 2025
- Current tier: Active user (based on monthly token usage)

**Deposit Tab**:
This tab provides M-Pesa top-up functionality with a clean, step-by-step flow:

1. **Amount Entry**: Large input field labeled "Amount to Deposit (KES)" with validation showing acceptable range (KES 1 - 150,000). Below, example amounts appear as quick-select chips: "+50", "+100", "+500", "+1000", "+5000"

2. **Phone Number**: Input field for M-Pesa-registered phone number with automatic format detection and normalization. A small info text states "Your phone must be registered for M-Pesa. You'll receive a payment prompt on this number."

3. **Confirmation**: Display shows "You will pay: KES 500 to phone 0712345678" with an edit button if details need correction.

4. **Initiate STK Push**: Large green "Send M-Pesa Prompt" button triggers the transaction. Upon clicking, a loading modal appears: "Sending payment prompt to your phone... Please check your phone and enter your M-Pesa PIN to complete the payment."

5. **Status Monitoring**: A 30-second countdown timer displays with status updates:
   - "Waiting for phone confirmation..." (0-10 seconds)
   - "Processing payment..." (after user enters PIN)
   - Success: "Payment successful! Your wallet has been topped up with KES 500" with green checkmark
   - Failure: "Payment was not completed. Please try again or contact support if you were charged" with red X

Throughout the process, users can cancel by clicking "Cancel Transaction" which abandons the request and updates the backend status to "cancelled."

**Token Purchase Interface**:
Clicking "Buy Tokens" from the Overview tab or Token Balance card opens a modal overlay with token package selection:

The interface displays five package cards in a horizontal scrollable row, each showing:
- Token quantity (large, bold)
- Price in KES
- Price per token
- Discount percentage (highlighted in green for better tiers, e.g., "Save 20%!")
- "Best Value" badge on the 1,000-token tier (most common purchase)

Below the packages, a "Custom Amount" expandable section allows entering any token quantity:
- Input: "Number of tokens" (1-999,999)
- Dynamic calculation showing: "Price: KES 475 (KES 0.38 per token, 24% discount)"
- Discount tier automatically applied based on quantity brackets

After selecting a package or custom amount, a "Purchase Tokens" button deducts the amount from the cash balance and credits tokens instantly. A confirmation message displays: "Successfully purchased 500 tokens for KES 200. New token balance: 523 tokens."

If the cash balance is insufficient, the button is disabled and replaced with "Insufficient balance. Deposit KES 150 more to complete this purchase" with a "Deposit Now" link.

**Transactions Tab**:
This tab presents a comprehensive, filterable transaction history in a clean table format:

| Date | Type | Description | Amount | Status |
|------|------|-------------|--------|--------|
| 2025-05-15 14:32 | Deposit | M-Pesa deposit (Receipt: QR2X...) | +KES 500 | Completed |
| 2025-05-15 14:35 | Payment | Purchased 500 chat tokens | -KES 200 | Completed |
| 2025-05-16 09:00 | Grant | Daily free tokens | +4 tokens | Completed |
| 2025-05-16 10:15 | Payment | Chat message to Flavia AI | -1 token | Completed |

**Filters** above the table allow narrowing by:
- Transaction type (All / Deposits / Payments / Grants / Refunds)
- Status (All / Completed / Pending / Failed)
- Date range (Last 7 days / Last 30 days / Last 90 days / Custom range)

Each transaction row can be clicked to expand and show full details including M-Pesa receipt number, phone number used, timestamps, and any error messages (for failed transactions).

A "Download Statement" button exports the filtered transactions as a CSV file for offline record-keeping.

**Pagination** controls appear at the bottom when transaction history exceeds 10 entries per page: "Showing 1-10 of 47 transactions" with Previous/Next buttons and page number selector.

**Real-Time Updates**:
The wallet interface uses polling (every 5 seconds) to check for transaction status updates when pending transactions exist. This ensures that after completing an M-Pesa payment on their phone, users see their balance update within seconds without manually refreshing the page. A subtle animation (brief green glow) highlights the updated balance when a change is detected.

**Mobile Optimization**:
Given M-Pesa's mobile-native nature, the wallet interface is specifically optimized for small screens:
- Large, touch-friendly buttons (minimum 44px height)
- Single-column layout on phones
- Bottom-sheet modals for token purchase on mobile (easier thumb reach)
- Auto-focus on phone number input after amount selection
- Success/failure messages display as full-screen overlays with clear next-action buttons

#### Screenshot

**[Screenshot Placeholder: Wallet dashboard showing two prominent balance cards (Cash Balance in green, Token Balance in blue), quick-stats section below, and three tabs (Overview/Deposit/Transactions). STK Push flow modal visible showing "Payment prompt sent to 0712 345 678 - Please check your phone" with 30-second countdown timer.]**

---

### Feature 8: User Account Management and Authentication System

#### Description

The Account Management System provides comprehensive user identity and preference management capabilities built on secure authentication protocols. The system handles the complete user lifecycle from registration through profile management to account deletion, using industry-standard security practices to protect user data and ensure proper access control across all platform features.

**Registration Process**:
New users create accounts by providing an email address, password (minimum 8 characters with at least one letter and one number), and display name. The system validates email format and uniqueness, hashes passwords using bcrypt with salt rounds for cryptographic security, and creates a MongoDB user document with default preferences. Upon successful registration, users receive a JWT (JSON Web Token) authentication token and are automatically logged in.

**Authentication Mechanism**:
The platform implements JWT-based authentication with access and refresh token architecture:
- **Access Tokens**: Short-lived (1 hour) tokens included in Authorization headers for API requests, contain user identity claims (user_id, email)
- **Refresh Tokens**: Long-lived (30 days) tokens stored securely, used to obtain new access tokens without re-authentication
- **Token Security**: HTTP-only cookies for web, localStorage with XSS protection for SPA, automatic token expiration and renewal

All protected API endpoints (wallet, profile, chat, etc.) require valid access tokens in the Authorization header (`Bearer <token>`). The system automatically validates tokens, checks expiration, and returns 401 Unauthorized errors for invalid/expired tokens, triggering client-side token refresh flows.

**Profile Management**:
Users can view and update profile information including:
- **Display Name**: Customizable name shown throughout the platform UI
- **Email Address**: Account identifier (changes require email verification)
- **Password**: Secure change requiring current password confirmation
- **Preferences**: Theme selection (light/dark), default futures contract, notification settings

Profile updates trigger validation (email uniqueness, password strength) and update MongoDB documents with new timestamps. The profile page displays account creation date, last login timestamp, and usage statistics (total tokens used, strategies analyzed, heatmaps generated).

**User Preferences System**:
The preferences subsystem allows customization of platform behavior:
- **Theme**: Light or dark color scheme, persisted across sessions and applied platform-wide
- **Default Contract**: Pre-selected futures contract that auto-populates in calculator on page load
- **Notifications**: Enable/disable email notifications for wallet activity, new features, educational content
- **Calculation Defaults**: Saved default values for risk-free rate, typical volatility ranges, preferred expiration horizons

Preferences are stored in the user document's `preferences` subdocument and synchronized across devices via cloud storage, ensuring consistent experience regardless of access device.

**Session Management**:
The platform maintains user sessions with 24-hour server-side lifetime. Sessions track:
- Last activity timestamp (for auto-logout after 30 minutes inactivity)
- Device/browser fingerprint (for security monitoring)
- Feature usage flags (which features accessed this session)

Sessions automatically expire after 24 hours or 30 minutes of inactivity, triggering client-side redirects to login page. Users can manually logout, which invalidates the session and clears stored tokens.

**Account Security**:
Security features include:
- **Password Hashing**: Bcrypt with 12 salt rounds, passwords never stored in plaintext
- **Email Validation**: Regex pattern matching and domain validation
- **Brute Force Protection**: Rate limiting on login attempts (5 failed attempts trigger 15-minute lockout)
- **Token Expiration**: Short-lived access tokens minimize exposure window if compromised
- **Secure Transmission**: All authentication requests over HTTPS with TLS 1.2+

**Account Deletion**:
Users can permanently delete accounts via profile settings. The deletion flow:
1. User clicks "Delete Account" and enters password confirmation
2. System validates password and displays warning about data loss
3. User confirms via secondary "Yes, Permanently Delete" button
4. System marks account as deleted, purges personal data, anonymizes transaction records (for regulatory compliance), and invalidates all tokens
5. Confirmation screen displays with automatic redirect to homepage

Deleted accounts are soft-deleted initially (30-day recovery window) before hard deletion, allowing recovery if user contacts support within the grace period.

#### Objective

Secure identity management is foundational to any platform handling financial data or personalized services—without reliable authentication, the platform cannot safely store user preferences, transaction history, or wallet balances. This feature ensures users can trust that their account data remains private and accessible only to them, building confidence necessary for financial platform adoption.

The preference system specifically addresses the reality that users interact with the platform repeatedly over time—having to re-enter default parameters on every visit creates friction that degrades user experience and discourages regular engagement. By persisting preferences, the platform creates a personalized environment that adapts to each user's typical use cases, making the platform feel responsive and attentive to individual needs.

The JWT-based authentication architecture provides security without sacrificing user experience. Unlike session-only authentication requiring server-side session storage and creating scalability challenges, JWTs are stateless and enable horizontal scaling while maintaining security through cryptographic signatures. The access/refresh token pattern specifically balances security (short-lived access tokens) with convenience (users don't need to log in hourly).

From an educational platform perspective, account management enables progress tracking and personalized learning paths—the system can remember which concepts a user has explored, which strategies they've analyzed, and which Flavia conversations they've had, enabling adaptive educational experiences that build on previous learning rather than starting fresh each session.

The transparent account deletion capability specifically builds trust by demonstrating respect for user autonomy and data privacy—users who know they can leave easily are paradoxically more likely to commit, as they don't feel "trapped" by the platform.

#### User Interaction

**Registration Flow**:
Users access registration via "Sign Up" links in the navigation header or from the login page. The registration form presents three input fields with clear labels and inline validation:

1. **Email**: Input with format validation (@ symbol, valid domain). Real-time feedback shows green checkmark for valid format, red X for invalid. On blur, system checks email uniqueness and displays "This email is already registered" error if duplicate found.

2. **Password**: Password input with strength meter showing weak/moderate/strong based on length, character variety, and common password checking. Requirements listed below field: "Minimum 8 characters, at least one letter and one number." A toggle icon allows showing/hiding password text.

3. **Display Name**: Text input for the name shown throughout the platform. Defaults to email username but fully customizable.

A "Create Account" button remains disabled until all validation passes, then enables with prominent green styling. Upon clicking, a loading spinner replaces the button text while the request processes. Success triggers automatic login and redirect to the calculator homepage with a welcome message: "Welcome, [Name]! Your account has been created. You've received 4 free chat tokens to get started."

Registration errors display as red alert boxes above the form: "An account with this email already exists. Please log in instead." with a link directly to the login page.

**Login Flow**:
The login page presents a minimal form with email and password inputs, a "Remember Me" checkbox (keeps refresh token for 30 days rather than session-only), and a "Log In" button.

After submission:
- **Success**: Redirect to previous page or homepage, with user menu in navigation header updating to show display name and profile picture (if set)
- **Invalid Credentials**: Error message "Email or password is incorrect. Please try again." (intentionally vague for security, doesn't indicate whether email exists)
- **Account Locked**: Error message "Too many failed login attempts. Please try again in 15 minutes or reset your password."

A "Forgot Password?" link initiates password reset flow (email verification with time-limited reset link).

**Profile Page**:
Users access their profile via the account menu dropdown in the navigation header. The profile page is organized into collapsible sections:

**Account Information Section**:
Displays read-only information with "Edit" buttons:
- Email: user@example.com [Edit]
- Display Name: John Trader [Edit]
- Member Since: May 15, 2025
- Last Login: June 10, 2025 at 2:34 PM

Clicking "Edit" toggles to edit mode with input fields and "Save" / "Cancel" buttons. Email changes trigger verification flow (email sent to new address with confirmation link that must be clicked before change takes effect).

**Security Section**:
Contains password change form:
- Current Password: [input]
- New Password: [input with strength meter]
- Confirm New Password: [input]
- [Change Password] button

Submission requires all fields, validates current password, checks new password meets requirements, and confirms both new password fields match. Success message: "Password updated successfully. You'll need to log in again on other devices."

**Preferences Section**:
Customization options displayed as form controls:

- **Theme**: Radio buttons for Light / Dark with live preview toggle
- **Default Contract**: Dropdown showing all 13 NSE futures contracts (e.g., "SCOM - Safaricom Futures")
- **Risk-Free Rate Default**: Numerical input (e.g., "9.5%") for auto-filling calculator
- **Notifications**: Checkboxes for different notification types:
  - [ ] Email me about wallet activity
  - [x] Email me about new platform features
  - [x] Email me educational content and tips
  - [ ] Email me weekly usage summaries

A "Save Preferences" button at section bottom triggers save with success confirmation: "Preferences saved. Your changes will apply immediately."

**Usage Statistics Section**:
Read-only dashboard showing activity metrics:
- Total Chat Messages: 87
- Total Tokens Used: 1,203
- Strategies Analyzed: 24
- Heatmaps Generated: 15
- Most Used Contract: SCOM (38%)
- Account Tier: Active User (based on monthly usage)

**Account Actions Section**:
Dangerous actions with warning styling:
- **Export My Data**: Button downloads JSON file containing all user data (profile, preferences, transaction history, chat logs) for portability
- **Delete Account**: Red button with warning icon opens confirmation modal: "Are you sure you want to delete your account? This will permanently erase all your data including wallet balance, transaction history, and chat conversations. This action cannot be undone." with [Cancel] and [Yes, Delete My Account] buttons. Upon confirmation, prompts for password entry as final verification before executing deletion.

**Navigation Integration**:
Once logged in, the navigation header displays:
- **User Menu Dropdown**: Display name with small down arrow, clicking reveals:
  - Profile
  - Wallet (with token count badge)
  - Settings
  - [Divider]
  - Log Out

When not logged in, header shows:
- **Log In** button (ghost style)
- **Sign Up** button (primary style, green)

**Session Timeout Handling**:
When access token expires during active use, the system automatically attempts refresh using the stored refresh token. If successful, the request retries transparently without user intervention. If refresh fails (refresh token also expired), a modal appears: "Your session has expired for security. Please log in again to continue." with a login form embedded directly in the modal, allowing re-authentication without losing page context.

#### Screenshot

**[Screenshot Placeholder: User profile page showing Account Information section with email/display name/member since details, Security section with password change form, Preferences section with theme toggle and default contract dropdown, Usage Statistics showing activity metrics, and Account Actions section with Export Data and Delete Account buttons]**

---

### Feature 9: NSE Market Data Integration and Contract Management

#### Description

The Market Data Integration system provides real-time access to Nairobi Securities Exchange (NSE) futures contract specifications and market status information. The system loads contract data from CSV files containing official NSE derivatives price lists, parses and validates the data, and exposes it via API endpoints for use throughout the platform. Additionally, the system tracks NSE trading hours and provides real-time market status indicating whether the derivatives market is currently open for trading.

**NSE Futures Contracts Database**:
The platform maintains a comprehensive database of 13 NSE futures contracts spanning equity futures and index futures:

**Equity Futures** (10 contracts):
- **SCOM** (Safaricom): Tick size KES 0.01, contract size 1,000 shares
- **EQTY** (Equity Group): Tick size KES 0.01, contract size 1,000 shares
- **KCBG** (KCB Group): Tick size KES 0.01, contract size 1,000 shares
- **EABL** (East African Breweries): Tick size KES 0.01, contract size 1,000 shares
- **BATK** (British American Tobacco Kenya): Tick size KES 0.01, contract size 100 shares
- **ABSA** (Absa Bank Kenya): Tick size KES 0.01, contract size 1,000 shares
- **NCBA** (NCBA Group): Tick size KES 0.01, contract size 1,000 shares
- **COOP** (Co-operative Bank): Tick size KES 0.01, contract size 1,000 shares
- **SCBK** (Standard Chartered Bank Kenya): Tick size KES 0.01, contract size 1,000 shares
- **IMHP** (IMH Properties): Tick size KES 0.01, contract size 1,000 shares

**Index Futures** (3 contracts):
- **N25I** (NSE 25 Index Future): Tick size 0.05 index points, contract size 100 x index value
- **25MN** (NSE 25 Mini Future): Tick size 0.05 index points, contract size 10 x index value (mini contract)

For each contract, the system stores:
- **Symbol**: Official NSE ticker
- **Name**: Full descriptive name
- **Contract Size**: Number of units per contract
- **Tick Size**: Minimum price movement
- **Expiration Months**: Standard expiry cycle (MAR/JUN/SEP/DEC quarterly)
- **Mark-to-Market Price**: Last settlement price (updated daily from CSV feed)
- **Contract Type**: Equity or Index
- **Underlying**: What the futures contract tracks

**Market Status Tracking**:
The system implements NSE derivatives market hours logic:
- **Trading Days**: Monday through Friday
- **Trading Hours**: 9:00 AM to 3:00 PM East Africa Time (EAT, UTC+3)
- **Market Status**: OPEN during trading hours on trading days, CLOSED outside hours or on weekends/holidays
- **Countdown Timer**: Displays time until next market open when closed, time until close when open

The market status API endpoint returns JSON containing current status, current server time in EAT, next market event (open/close), and countdown in human-readable format (e.g., "Market opens in 14 hours 32 minutes").

**Data Loading and Updates**:
The system loads contract data from CSV files at application startup. The CSV parser:
1. Reads the price list file (path configured in `config.py`)
2. Extracts rows containing futures contracts (filtering out options, bonds, etc.)
3. Parses relevant columns: Symbol, Name, Previous Close, MTM Price, Contract Specifications
4. Validates data types and ranges (prices must be positive, symbols must match expected patterns)
5. Stores parsed data in-memory for fast API access
6. Logs any parsing errors or missing fields for administrator review

For production deployment, the system supports automated CSV updates via scheduled tasks or webhook endpoints that reload data when NSE publishes updated price lists, ensuring contract specifications and settlement prices remain current.

**Fee Structure Integration**:
The system includes NSE-mandated fee structures applied to all derivatives transactions:
- **NSE Clearing Fee**: 0.0125% of contract value
- **Clearing Member Fee**: 0.0125% of contract value
- **Trading Member Fee**: 0.05% of contract value
- **IPF (Investor Protection Fund) Levy**: 0.005% of contract value
- **CMA (Capital Markets Authority) Fee**: 0.005% of contract value
- **Total Fees**: 0.085% of contract value

Users can optionally include these fees in pricing calculations to see realistic all-in costs rather than purely theoretical Black-76 values. The system displays itemized fee breakdowns showing each component's contribution to total cost.

#### Objective

Accurate, up-to-date market data is fundamental to any financial platform's credibility—using outdated contract specifications, incorrect tick sizes, or wrong trading hours would produce incorrect calculations and potentially mislead users about real trading conditions. This feature ensures the platform reflects actual NSE market conventions and contract structures, building user trust that the education received here translates directly to real-world application.

The comprehensive contract database specifically enables users to explore the full range of NSE derivatives offerings rather than limiting practice to a single "demo" contract. By supporting all 13 actual contracts, the platform allows users to understand how different underlying assets (banking stocks vs. telecom vs. consumer goods vs. indices) exhibit different price behaviors, volatilities, and option characteristics—critical knowledge for real-world trading where strategy selection depends heavily on underlying asset characteristics.

The market status tracking serves both practical and educational objectives. Practically, it prevents confusion about when trading occurs, helping users align their learning and analysis with actual market hours. Educationally, it reinforces that derivatives markets have specific trading windows (unlike 24/7 cryptocurrency markets), teaching users to consider liquidity and market access when planning strategies.

The fee integration specifically addresses a common pitfall where novice traders focus solely on theoretical option values without considering transaction costs, only to discover later that fees significantly erode profitability on small positions or high-frequency strategies. By making fees transparent and easy to include in calculations, the platform instills realistic cost awareness from the beginning of the learning journey.

From a market development perspective, providing a centralized, accurate database of NSE derivatives specifications reduces information fragmentation and democratizes access to market structure knowledge that might otherwise require expensive data terminals or direct broker relationships to obtain.

#### User Interaction

**Contract Selection in Calculator**:
Throughout the platform (pricing calculator, P&L analyzer, volatility forecasting), users encounter contract selection via a searchable dropdown menu. The dropdown displays contracts in grouped format:

**Equity Futures:**
- SCOM - Safaricom Futures
- EQTY - Equity Group Futures
- KCBG - KCB Group Futures
- [... 7 more equity contracts]

**Index Futures:**
- N25I - NSE 25 Index Future
- 25MN - NSE 25 Mini Future

As users type in the search field, the list filters by both symbol and name (typing "saf" matches "SCOM - Safaricom Futures"). Selecting a contract immediately:
1. Populates a "Contract Details" info panel showing specifications (contract size, tick size, last settlement price)
2. Auto-fills the futures price input with the last mark-to-market price
3. Adjusts validation ranges for strike prices based on the underlying's typical price range
4. Updates any existing calculations to reflect the new contract parameters

**Contract Information Panel**:
Adjacent to the contract dropdown, an expandable information panel displays detailed specifications:
- **Full Name**: Safaricom Futures Contract
- **Symbol**: SCOM
- **Contract Size**: 1,000 shares
- **Tick Size**: KES 0.01
- **Expiration Months**: March, June, September, December
- **Last Settlement**: KES 25.40 (as of June 10, 2025)
- **Underlying**: Safaricom PLC ordinary shares
- **Description**: This futures contract tracks the price of Safaricom shares, Kenya's largest telecom company. Highly liquid with active trading during market hours.

A "View All Contracts" link opens a full contracts reference page showing all 13 contracts in a sortable, filterable table with specifications and current prices.

**Market Status Indicator**:
The navigation header includes a market status badge that updates every 60 seconds:
- **When OPEN**: Green badge displaying "NSE OPEN | Closes in 4h 23m" with animated pulse effect
- **When CLOSED**: Gray badge displaying "NSE CLOSED | Opens in 15h 12m"

Clicking the badge opens a detailed market hours modal:
- **Current Time**: 10:45 AM EAT (June 10, 2025)
- **Today's Status**: Market is OPEN
- **Trading Hours**: 9:00 AM - 3:00 PM EAT, Monday-Friday
- **Time Until Close**: 4 hours 15 minutes
- **Next Trading Day**: Today (if before 3 PM) or Tomorrow [Date] at 9:00 AM

For users in different timezones, the modal includes a timezone converter: "In your timezone ([Auto-detected timezone]), the market opens at [Local time] and closes at [Local time]."

**Fee Inclusion Toggle**:
Within the pricing calculator, a checkbox labeled "Include NSE Fees (0.085%)" allows users to add realistic fees to theoretical pricing. When checked:
1. Calculated option prices increase by 0.085%
2. A fee breakdown expands below showing itemized components
3. Results display both "Theoretical Price" and "Total Cost with Fees"

The fee breakdown shows:
```
NSE Fee Breakdown for 1 contract:
- Theoretical Option Value: KES 4.50
- NSE Clearing Fee (0.0125%): KES 0.06
- Clearing Member Fee (0.0125%): KES 0.06
- Trading Member Fee (0.05%): KES 0.23
- IPF Levy (0.005%): KES 0.02
- CMA Fee (0.005%): KES 0.02
- Total Fees: KES 0.38
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Cost: KES 4.88
```

For multi-contract positions, fees scale proportionally with a note: "For 10 contracts, total fees would be KES 3.80 (10 x KES 0.38 per contract)."

**Contract Data Freshness**:
At the bottom of pages displaying market data, a timestamp indicates data currency: "Contract data last updated: June 10, 2025 at 3:15 PM EAT (end of trading day)." If data is older than 24 hours, a yellow warning appears: "Market data may be outdated. Last update was [time] ago."

**Educational Context**:
First-time users encountering contract selection see a one-time tooltip: "These are real NSE futures contracts. While this is an educational platform, all calculations use actual contract specifications so you're learning with realistic parameters." This can be dismissed and won't show again for that user.

#### Screenshot

**[Screenshot Placeholder: Contract selection dropdown showing grouped equity and index futures, with expanded contract details panel displaying SCOM specifications (contract size, tick size, last settlement price, expiration months). Market status badge in header showing "NSE OPEN | Closes in 4h 23m" in green with pulse animation.]**

---

### Feature 10: Enhanced Educational Content and Contextual Help System

#### Description

The Educational Content System provides comprehensive learning resources integrated throughout the platform via contextual help, interactive tutorials, strategy guides, and a searchable financial glossary. Rather than isolating education in a separate documentation section, the system embeds learning opportunities at every point where users might need clarification, creating a seamless integration between doing and learning.

**Contextual Help Tooltips**:
Throughout the platform interface, small "?" icons appear adjacent to technical terms, input fields, and complex visualizations. Hovering over or clicking these icons reveals contextual tooltips that explain the concept in plain language with relevant examples. For instance:
- Next to "Implied Volatility" input: "Expected future volatility. Higher volatility increases option prices because there's more uncertainty about where the underlying price will end up. Historical average for this contract is 18-22%."
- Next to "Delta" in Greeks dashboard: "How much the option price changes when the underlying moves KES 1. A Delta of 0.65 means this call gains KES 0.65 if the stock rises KES 1."

**Interactive Tutorials**:
First-time users encounter optional guided tours when accessing major features:
- **Calculator Tutorial**: 6-step walkthrough highlighting contract selection, input fields, calculation button, and results interpretation
- **Heatmap Tutorial**: 4-step guide explaining axes, color meanings, and how to interpret surface topology
- **P&L Analyzer Tutorial**: 8-step walkthrough covering leg addition, strategy templates, and payoff diagram interpretation
- **Flavia AI Introduction**: 3-step guide showing how to ask questions, use suggested queries, and manage tokens

Tours can be skipped ("Don't show this again") or paused/resumed. Progress is saved so users can complete tutorials across multiple sessions.

**Strategy Library**:
A dedicated "Strategies" section in the main navigation provides comprehensive guides for 20+ common options strategies, organized by category:

**Bullish Strategies** (expecting price increases):
- Long Call
- Bull Call Spread
- Bull Put Spread
- Covered Call (with futures position)

**Bearish Strategies** (expecting price decreases):
- Long Put
- Bear Put Spread
- Bear Call Spread

**Neutral Strategies** (expecting low volatility / range-bound prices):
- Short Straddle
- Short Strangle
- Iron Condor
- Butterfly Spread

**Volatile Strategies** (expecting large price movements):
- Long Straddle
- Long Strangle
- Calendar Spread (Volatility Play)

Each strategy guide includes:
- **Payoff Diagram**: Visual representation of profit/loss profile
- **Description**: What the strategy involves (which options to buy/sell)
- **Market Outlook**: When to use this strategy (bullish/bearish/neutral/volatile)
- **Maximum Profit**: How much you can gain and under what conditions
- **Maximum Loss**: How much you can lose and under what conditions
- **Breakeven Point(s)**: Underlying price(s) where strategy neither profits nor loses
- **Greeks Profile**: Typical Delta, Gamma, Vega, Theta characteristics
- **Example Trade**: Concrete numerical example with NSE contracts (e.g., "Buy 1 SCOM JUN 25 call, Sell 1 SCOM JUN 27 call...")
- **Pros and Cons**: Advantages and disadvantages of this strategy
- **Try It Now**: Button that loads the strategy into the P&L Analyzer with pre-filled parameters

**Financial Glossary**:
A searchable glossary accessible via main navigation and quick-search bar provides definitions for 100+ terms:
- Options terminology (call, put, strike, expiration, premium, intrinsic value, extrinsic value, American vs European)
- Greeks (Delta, Gamma, Vega, Theta, Rho) with formulas and interpretations
- Pricing concepts (Black-76 model, Black-Scholes, implied volatility, historical volatility, volatility smile)
- NSE-specific terms (futures contract, index future, settlement, MTM price, clearing fees)
- Market mechanics (bid-ask spread, liquidity, open interest, volume)
- Risk management (position sizing, stop loss, hedging, diversification)
- Statistical concepts (standard deviation, probability distribution, confidence interval)

Each glossary entry includes:
- **Definition**: Clear, jargon-free explanation
- **Example**: Contextual example using NSE contracts
- **Related Terms**: Links to related glossary entries
- **Learn More**: Links to relevant strategy guides or Flavia AI suggested questions

The glossary supports full-text search and alphabetical browsing. Frequently accessed terms are highlighted as "Popular" to guide beginners toward foundational concepts.

**Video Tutorials** (if implemented):
For visual learners, embedded video content demonstrates:
- Platform navigation and feature overview
- How to use the pricing calculator step-by-step
- Reading and interpreting heatmaps
- Building multi-leg strategies in the P&L analyzer
- Understanding Greeks through examples
- Using Flavia AI effectively

Videos are short (2-5 minutes), professionally produced with clear audio, and include timestamps and transcripts for accessibility.

**Learning Paths** (advanced feature):
Structured curriculum guiding users from beginner to advanced understanding:
- **Path 1: Options Basics** (5 modules): What are options → Call vs Put → Intrinsic/Extrinsic value → How pricing works → Time decay
- **Path 2: Understanding Greeks** (4 modules): Introduction to Greeks → Delta and Gamma → Vega and Volatility → Theta and Time
- **Path 3: Basic Strategies** (6 modules): Covered calls → Protective puts → Vertical spreads → Straddles/Strangles → Calendar spreads → Risk management
- **Path 4: Advanced Strategies** (5 modules): Iron condors → Butterflies → Ratio spreads → Volatility trading → Portfolio hedging

Each module includes reading material, interactive examples in the calculator, quizzes to check understanding, and practical exercises ("Build a bull call spread with SCOM contracts and analyze the payoff").

Progress tracking shows completion percentage and suggests next steps: "You've completed 3 of 5 modules in Options Basics. Continue with Time Decay to finish this path."

#### Objective

Financial education suffers from a fundamental challenge: learners don't know what they don't know, and traditional linear education (textbooks, courses) forces learners to consume content in predetermined sequences that may not align with their questions or needs at specific moments. This feature addresses that by meeting learners at their point of need—when they encounter a confusing term or concept while using the platform, immediate help is available without disrupting workflow.

The contextual approach specifically reduces cognitive load and friction. Rather than forcing users to alt-tab to external documentation or search through lengthy PDFs, tooltips and inline explanations provide just-in-time learning that keeps users in flow state. This dramatically increases the likelihood that users will actually seek and absorb information rather than guessing or skipping features they don't understand.

The strategy library addresses a specific gap in options education: while many resources explain individual options and basic concepts, far fewer provide practical guidance on combining options into strategies that match real market views. By providing pre-built strategy templates with clear explanations of when and why to use them, the platform accelerates the learning curve from "I understand calls and puts" to "I can design a strategy matching my market outlook."

The glossary specifically supports self-directed learning—users with some existing knowledge may not need tutorials but want quick reference for specific terms or formulas. The comprehensive, searchable glossary enables that mode of learning while maintaining consistency in definitions across all platform features.

From a market development perspective, embedding education directly in the trading platform follows the model of successful fintech companies that have democratized investing (Robinhood's accessible interface, Coinbase's learn-and-earn). By reducing educational barriers, the platform supports Kenya's CMA objectives of developing sophisticated investor populations capable of participating safely in derivatives markets.

#### User Interaction

**Discovering Educational Content**:

**Via Contextual Help Icons**:
While using any feature, users notice small "?" icons (blue or gray, 16px diameter) positioned near technical terms or complex elements. For example, in the calculator:
- Next to "Strike Price" field: [?] icon
- Next to "Implied Volatility" field: [?] icon
- Next to each Greek in the dashboard: [?] icon

Hovering over a "?" icon (on desktop) or tapping it (on mobile) reveals a small tooltip popup with white background and dark text, containing a 1-3 sentence explanation and optionally a "Learn More" link. For example:

> **Strike Price**: The price at which the option allows you to buy (call) or sell (put) the underlying futures contract. Options with strikes close to the current price are most valuable. [Learn More →]

Clicking "Learn More" opens a side drawer (desktop) or full-screen modal (mobile) with expanded explanation including examples, related concepts, and links to relevant strategy guides.

**Via Main Navigation**:
The header navigation includes a "Learn" dropdown menu with organized sections:
- **Getting Started**
  - Platform Overview
  - How to Use the Calculator
  - Understanding Option Prices
  - Reading Heatmaps
- **Core Concepts**
  - Calls vs Puts
  - The Greeks Explained
  - Volatility and Its Impact
  - Time Decay
- **Strategy Guides**
  - Bullish Strategies (7 strategies)
  - Bearish Strategies (4 strategies)
  - Neutral Strategies (5 strategies)
  - Volatile Strategies (4 strategies)
- **Glossary**
  - Browse A-Z
  - Search Terms
- **Learning Paths**
  - Options Basics (5 modules)
  - Understanding Greeks (4 modules)
  - Basic Strategies (6 modules)
  - Advanced Strategies (5 modules)

Selecting any item navigates to a dedicated page with structured content, code examples, interactive calculators embedded inline, and "Try It Now" buttons that load examples into the actual calculator.

**Strategy Guide Pages**:
Clicking a strategy from the dropdown (e.g., "Bull Call Spread") loads a dedicated page with:

**Header Section**:
- Strategy name in large text
- One-line summary: "Limited-risk, limited-profit bullish strategy using two call options"
- Difficulty badge: "Beginner" (green) / "Intermediate" (yellow) / "Advanced" (red)
- Market outlook tags: "Bullish" "Limited Risk" "Moderate Cost"

**Payoff Diagram Section**:
Large interactive diagram showing profit/loss profile with:
- Labeled breakeven point
- Max profit and max loss regions shaded
- Current underlying price marker
- Ability to adjust strikes/parameters and see diagram update in real-time

**How It Works Section**:
Step-by-step construction guide:
1. "Buy 1 call option at lower strike price (e.g., KES 25)"
2. "Sell 1 call option at higher strike price (e.g., KES 27)"
3. "Both options must have the same expiration date"
Includes a visual representation showing the two legs and how they combine.

**When to Use Section**:
- "Use this strategy when you expect moderate price increases"
- "Best in low-to-moderate volatility environments"
- "Appropriate when you want defined risk (unlike naked long calls)"

**Risk/Reward Analysis Section**:
- **Maximum Profit**: "Difference between strikes minus net debit" with formula and example calculation
- **Maximum Loss**: "Net debit paid (limited to upfront cost)" with example
- **Breakeven**: "Lower strike + net debit" with example calculation

**Greeks Profile Section**:
Table showing typical Greek characteristics:
- **Net Delta**: Positive (bullish), around +0.40 typical at-the-money
- **Net Gamma**: Near zero (offsetting long/short Gammas)
- **Net Vega**: Near zero (offsetting Vega exposures)
- **Net Theta**: Slightly negative but less than simple long calls

With interpretation: "This strategy has bullish directional exposure (positive Delta) but is relatively insensitive to volatility changes (near-zero Vega) and time decay (low Theta), making it more stable than simple long calls."

**Example Trade Section**:
Concrete example with NSE contracts:
```
Example Bull Call Spread on SCOM:
- Current SCOM futures price: KES 25.50
- Buy 1 SCOM JUN 25.00 call @ KES 1.20
- Sell 1 SCOM JUN 27.00 call @ KES 0.40
- Net Debit: KES 0.80 per share (KES 800 per contract for 1,000 shares)

Outcomes at Expiration:
- If SCOM below 25.00: Both calls expire worthless, lose KES 800 (max loss)
- If SCOM at 25.80: Breakeven (25.00 strike + 0.80 debit)
- If SCOM at 26.00: Profit KES 200 [(26-25) - 0.80 debit) x 1000]
- If SCOM above 27.00: Max profit KES 1,200 [(27-25) - 0.80] x 1000]
```

**Pros and Cons Section**:
Two-column comparison:
- ✓ **Pros**: Lower cost than long call, defined maximum loss, profit in moderately bullish scenarios, less Theta decay than long calls
- ✗ **Cons**: Limited profit potential (capped at higher strike), still loses money if underlying falls, more complex than single-option positions

**Try It Now Section**:
Large green button: "Build This Strategy in P&L Analyzer" which, when clicked:
1. Opens the P&L Analyzer page
2. Auto-populates a bull call spread with reasonable strikes based on current underlying price
3. Displays the resulting payoff diagram
4. Shows a hint: "This strategy was pre-loaded from the Bull Call Spread guide. Adjust the strikes and expiration to see how parameters affect the payoff."

**Glossary Interaction**:
Accessing the glossary via "Learn > Glossary" opens a dedicated glossary page with:

**Search Bar** at top: "Search terms..." with autocomplete showing matching entries as user types

**Alphabetical Navigation**: A-Z letter tabs for browsing by first letter

**Term List**: Alphabetically sorted terms displayed as cards:

---
**Call Option**
The right, but not obligation, to buy the underlying asset at a specified price (strike) before expiration. Call buyers profit when the underlying price rises above the strike.

*Example*: If you buy a SCOM 25 call and SCOM rises to 28, you can exercise to buy at 25 and sell at 28, profiting KES 3 per share (minus premium paid).

*Related*: Put Option, Strike Price, Premium, Intrinsic Value

[Ask Flavia About This →]

---
**Delta (Δ)**
The rate of change in option value relative to changes in underlying price. Ranges from 0 to 1 for calls (0 to -1 for puts). Higher Delta = more sensitivity.

*Example*: A Delta of 0.65 means the option gains KES 0.65 for every KES 1 increase in the underlying.

*Formula*: δV/δS (partial derivative of option value with respect to underlying price)

*Related*: Gamma, The Greeks, Hedge Ratio

[Ask Flavia About This →] [See in Calculator →]

---

Each term can be clicked to expand into a full-page view with more comprehensive explanation, historical context, mathematical formulas (if applicable), and links to strategies that emphasize that concept.

The "Ask Flavia About This" button pre-fills the chat with an optimized question about that term, opening the chatbot interface ready to send the query.

**Learning Path Interface**:
Selecting "Learning Paths" from the Learn menu displays available curricula as cards showing:
- Path name and difficulty level
- Number of modules and estimated completion time
- Progress bar (if started)
- "Start Path" or "Continue" button

Clicking into a path shows module list:
```
Path: Options Basics (Beginner)
Estimated Time: 2 hours | Your Progress: 60% (3/5 modules complete)

[✓] Module 1: What Are Options? (Completed)
[✓] Module 2: Calls vs Puts (Completed)
[✓] Module 3: Intrinsic and Extrinsic Value (Completed)
[→] Module 4: How Option Pricing Works (Current - 40% complete)
[ ] Module 5: Understanding Time Decay (Locked until Module 4 complete)

[Continue Module 4 →]
```

Each module includes:
- Reading content with embedded examples
- Interactive calculator exercises ("Now calculate the intrinsic value for a SCOM 26 call when SCOM is at 27.50")
- Knowledge check quiz (3-5 questions)
- Module completion badge

Completing all modules in a path awards a certificate (downloadable PDF) and unlocks the next path in the sequence.

#### Screenshot

**[Screenshot Placeholder: Strategy guide page for "Bull Call Spread" showing header with difficulty badge, large payoff diagram with breakeven/max profit/max loss annotations, "How It Works" step-by-step construction guide, risk/reward analysis table, Greeks profile, concrete NSE example trade calculation, pros/cons comparison, and prominent "Build This Strategy in P&L Analyzer" button]**

---

## Technical Implementation Details

### Backend API Architecture

**Flask Application Structure**:
```
backend/
├── __init__.py              # App factory with Flask-RESTX setup
├── routes.py                # Page route handlers (HTML rendering)
├── config.py                # Configuration classes (Dev/Prod/Test)
├── api/
│   ├── __init__.py          # API namespace registration
│   ├── pricing.py           # Black-76 calculation endpoints
│   ├── auth.py              # Registration, login, profile management
│   ├── wallet.py            # Wallet balance, M-Pesa, transactions
│   ├── chat.py              # Flavia AI chatbot endpoints
│   ├── pnl.py               # Multi-leg P&L analysis
│   ├── market.py            # Market status, futures data
│   └── volatility.py        # ML volatility forecasting
├── services/
│   ├── auth_service.py      # User authentication logic
│   ├── wallet_service.py    # Wallet and transaction management
│   ├── mpesa_service.py     # M-Pesa Daraja API integration
│   ├── chatbot_service.py   # OpenAI integration for Flavia
│   ├── volatility_service.py # ML model loading and prediction
│   ├── data_loader.py       # CSV parsing for NSE contract data
│   └── feature_engine.py    # Feature engineering for ML models
├── models/
│   └── user_models.py       # Pydantic models for validation
└── core/
    └── pricing/
        ├── black76.py       # Black-76 pricing implementation
        └── contracts.py     # NSE futures contract specifications
```

**API Documentation**:
Flask-RESTX auto-generates Swagger documentation accessible at `/api/docs`, providing:
- Complete endpoint listing with HTTP methods
- Request/response schemas with examples
- Try-it-out functionality for testing endpoints
- Authentication requirements clearly marked

### Frontend Architecture

**JavaScript Module Organization**:
```
frontend/static/js/
├── app.js                    # Main application initialization
├── api.js                    # Centralized API client with JWT handling
├── auth.js                   # Login, registration, session management
├── components/
│   ├── calculator.js         # Options pricing calculator logic
│   ├── charts.js             # Plotly.js heatmap and P&L visualization
│   ├── pnl.js                # Strategy builder and P&L analyzer
│   ├── wallet.js             # Wallet UI, M-Pesa, token purchases
│   ├── chatbot.js            # Flavia AI chat interface
│   └── volatility_forecast.js # Volatility prediction UI
└── utils/
    └── formatting.js         # Number formatting, date utilities
```

**State Management**:
- LocalStorage for calculator inputs, theme preferences, auth tokens
- SessionStorage for temporary UI state (tab selections, modal states)
- In-memory JavaScript objects for real-time calculations (no server round-trip for instant feedback)

**Responsive Design**:
Tailwind CSS utility classes with mobile-first approach:
- Single-column layouts on mobile (<640px)
- Two-column on tablets (640-1024px)
- Three-column on desktop (>1024px)
- Touch-friendly button sizes (minimum 44x44px)
- Collapsible navigation drawer on mobile

### Database Schema

**MongoDB Collections**:

**users Collection**:
```javascript
{
  _id: ObjectId,
  email: String (unique index),
  password_hash: String,
  name: String,
  preferences: {
    theme: String ('light' | 'dark'),
    default_contract: String,
    notifications_enabled: Boolean
  },
  wallet: {
    balance: Number (KES, 2 decimal precision),
    currency: String ('KES'),
    chat_tokens: Number (integer),
    tokens_used: Number (integer),
    last_daily_token_grant: ISODate,
    last_updated: ISODate
  },
  created_at: ISODate,
  updated_at: ISODate
}
```
**Indexes**: email (unique), created_at

**wallet_transactions Collection**:
```javascript
{
  _id: ObjectId,
  user_id: String (indexed),
  type: String ('deposit' | 'payment' | 'grant' | 'refund'),
  amount: Number (KES or tokens),
  status: String ('pending' | 'completed' | 'failed' | 'cancelled') (indexed),
  description: String,
  mpesa_receipt: String,
  mpesa_checkout_id: String,
  mpesa_merchant_request_id: String,
  phone_number: String,
  created_at: ISODate (indexed),
  updated_at: ISODate
}
```
**Indexes**: user_id, status, created_at, mpesa_checkout_id (unique)

### Security Implementation

**Authentication Flow**:
1. User submits credentials to `/api/auth/login`
2. Backend validates credentials (bcrypt comparison)
3. If valid, generates JWT access token (1hr expiry) and refresh token (30d expiry)
4. Frontend stores tokens in localStorage
5. All subsequent API requests include `Authorization: Bearer <access_token>` header
6. Backend middleware validates token signature and expiration on each protected route
7. When access token expires, frontend automatically calls `/api/auth/refresh` with refresh token
8. Backend issues new access token if refresh token valid
9. If refresh token invalid/expired, user redirected to login

**Password Security**:
- Bcrypt hashing with 12 salt rounds
- Password requirements enforced: minimum 8 characters, at least one letter, one number
- Current password verification required for password changes
- No password storage in plaintext anywhere in system

**CORS Configuration**:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://nse-options.co.ke"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

**Input Validation**:
- Pydantic models validate all API request payloads
- Type checking (string vs number vs boolean)
- Range validation (prices > 0, volatility 0-200%, etc.)
- Format validation (email regex, phone number patterns)
- SQL injection prevention (MongoDB parameterized queries)
- XSS prevention (all user inputs sanitized before rendering)

### M-Pesa Integration Details

**OAuth Flow**:
```python
# Get access token (refreshed every 50 minutes)
def get_access_token():
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json()['access_token']
```

**STK Push Request**:
```python
def initiate_stk_push(phone, amount, account_ref):
    url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f"{SHORTCODE}{PASSKEY}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": f"{BASE_URL}/api/wallet/callback/mpesa",
        "AccountReference": account_ref,
        "TransactionDesc": "Wallet Top-up"
    }

    headers = {"Authorization": f"Bearer {get_access_token()}"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

**Callback Handling**:
```python
@api.route('/callback/mpesa', methods=['POST'])
def mpesa_callback():
    data = request.json
    result = data['Body']['stkCallback']

    if result['ResultCode'] == 0:  # Success
        items = result['CallbackMetadata']['Item']
        mpesa_receipt = next(item['Value'] for item in items if item['Name'] == 'MpesaReceiptNumber')
        amount = next(item['Value'] for item in items if item['Name'] == 'Amount')

        # Update transaction status and wallet balance
        wallet_service.complete_transaction(
            checkout_id=result['CheckoutRequestID'],
            mpesa_receipt=mpesa_receipt,
            amount=amount
        )
    else:  # Failed
        wallet_service.fail_transaction(
            checkout_id=result['CheckoutRequestID'],
            error_message=result['ResultDesc']
        )

    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})
```

### Volatility Forecasting Implementation

**Model Architecture**:
The volatility forecasting service uses a pre-trained ensemble model combining:
- **ARIMA (AutoRegressive Integrated Moving Average)**: Captures linear time-series patterns and trends
- **GARCH (Generalized Autoregressive Conditional Heteroskedasticity)**: Models volatility clustering (periods of high/low volatility persistence)
- **LSTM (Long Short-Term Memory Neural Network)**: Captures complex non-linear temporal dependencies
- **XGBoost (Gradient Boosting)**: Ensemble tree-based model for feature interactions

**Feature Engineering**:
```python
def engineer_features(price_data):
    """Extract features from OHLCV data"""
    features = {}

    # Returns-based features
    features['returns'] = np.log(price_data['close'] / price_data['close'].shift(1))
    features['squared_returns'] = features['returns'] ** 2

    # Volatility measures
    features['realized_vol_5d'] = features['returns'].rolling(5).std() * np.sqrt(252)
    features['realized_vol_21d'] = features['returns'].rolling(21).std() * np.sqrt(252)

    # Price-based features
    features['high_low_range'] = (price_data['high'] - price_data['low']) / price_data['close']
    features['close_open_diff'] = (price_data['close'] - price_data['open']) / price_data['open']

    # Volume features
    features['volume_ma_ratio'] = price_data['volume'] / price_data['volume'].rolling(20).mean()

    # Momentum indicators
    features['rsi_14'] = calculate_rsi(price_data['close'], 14)
    features['macd'] = calculate_macd(price_data['close'])

    return pd.DataFrame(features)
```

**Prediction Process**:
```python
def predict_volatility(symbol, horizon_days):
    # Load historical data
    data = load_historical_data(symbol)

    # Engineer features
    features = engineer_features(data)

    # Normalize
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Load model
    model = joblib.load('volatility_forecaster_v2_enhanced.joblib')

    # Generate prediction
    prediction = model.predict(features_scaled, horizon=horizon_days)

    # Calculate confidence intervals (using quantile regression)
    lower_bound = model.predict_quantile(features_scaled, quantile=0.025)
    upper_bound = model.predict_quantile(features_scaled, quantile=0.975)

    # Compute model confidence (based on prediction variance across ensemble members)
    predictions_by_model = model.predict_all_models(features_scaled)
    confidence = 100 * (1 - np.std(predictions_by_model) / np.mean(predictions_by_model))

    return {
        'predicted_volatility': float(prediction),
        'confidence_interval': [float(lower_bound), float(upper_bound)],
        'model_confidence': float(confidence),
        'contributing_models': model.get_model_weights(),
        'horizon_days': horizon_days,
        'prediction_timestamp': datetime.utcnow().isoformat()
    }
```

---

## System Requirements

### Server Requirements
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **Python**: 3.8 or higher
- **MongoDB**: 4.6 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended for ML model)
- **Storage**: Minimum 10GB (for database, logs, ML models)
- **Network**: Stable internet connection for M-Pesa callbacks and OpenAI API

### Client Requirements
- **Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript**: Must be enabled
- **Screen Resolution**: Minimum 1280x720 (responsive down to 360px mobile)
- **Internet**: Minimum 2 Mbps connection for real-time features

### Development Environment
- **Code Editor**: VS Code, PyCharm, or similar
- **Package Manager**: pip (Python), npm (Node.js for any frontend tooling)
- **Version Control**: Git 2.0+
- **API Testing**: Postman, Insomnia, or Swagger UI (built-in)

---

## Deployment Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<strong-random-secret-key>

# MongoDB
MONGO_URI=mongodb://username:password@host:port/database_name

# JWT Settings
JWT_SECRET_KEY=<different-random-secret-key>
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days

# M-Pesa Daraja API
MPESA_ENVIRONMENT=production  # or 'sandbox' for testing
MPESA_CONSUMER_KEY=<your-consumer-key>
MPESA_CONSUMER_SECRET=<your-consumer-secret>
MPESA_SHORTCODE=<your-business-shortcode>
MPESA_PASSKEY=<your-lipa-na-mpesa-passkey>
MPESA_CALLBACK_URL=https://yourdomain.com/api/wallet/callback/mpesa

# OpenAI API
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MODEL=gpt-4o-mini

# NSE Data
NSE_DATA_FILE=/path/to/derivatives_price_list.csv
VOLATILITY_MODEL_PATH=/path/to/volatility_forecaster_v2_enhanced.joblib

# Application Settings
BASE_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Production Deployment Steps

1. **Server Setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.8 python3-pip python3-venv -y

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-4.6.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.6.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

2. **Application Deployment**:
```bash
# Clone repository
git clone https://github.com/yourusername/nse-options-pricer.git
cd nse-options-pricer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
nano .env  # Edit with production values

# Run database migrations (if applicable)
python manage.py db upgrade
```

3. **WSGI Server (Gunicorn)**:
```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/nse-options.service
```

Service file content:
```ini
[Unit]
Description=NSE Options Pricer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/nse-options-pricer
Environment="PATH=/path/to/nse-options-pricer/venv/bin"
ExecStart=/path/to/nse-options-pricer/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 "backend:create_app()"

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start nse-options
sudo systemctl enable nse-options
```

4. **Nginx Reverse Proxy**:
```bash
# Install Nginx
sudo apt install nginx -y

# Create site configuration
sudo nano /etc/nginx/sites-available/nse-options
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/nse-options-pricer/frontend/static;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/nse-options /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **SSL Certificate (Let's Encrypt)**:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Maintenance and Monitoring

### Log Management
- **Application Logs**: `/var/log/nse-options/app.log` (configured in Flask)
- **Error Logs**: `/var/log/nse-options/error.log`
- **M-Pesa Callback Logs**: Separate log file for debugging payment issues
- **Log Rotation**: Configure logrotate to prevent disk space issues

### Monitoring
- **Health Check Endpoint**: `GET /api/health` returns system status, database connectivity, ML model loaded status
- **Uptime Monitoring**: Use services like UptimeRobot or Pingdom
- **Error Tracking**: Integrate Sentry or similar for exception tracking
- **Performance Monitoring**: Monitor API response times, database query performance

### Backup Strategy
- **Database Backups**: Daily MongoDB dumps to remote storage
- **User Data**: Regular exports of user accounts and transactions
- **ML Models**: Version-controlled model files in cloud storage
- **Configuration**: Environment files backed up securely (encrypted)

---

## Support and Maintenance

### User Support Channels
- **Email**: support@nse-options.co.ke (monitored 9 AM - 5 PM EAT, Mon-Fri)
- **In-App Feedback**: Feedback form accessible from all pages
- **FAQ Section**: Comprehensive FAQ covering common issues and questions
- **Flavia AI**: First line of support for educational questions

### Known Issues and Limitations
- **M-Pesa Transaction Delays**: Callbacks can sometimes be delayed up to 60 seconds during high Safaricom traffic
- **ML Model Accuracy**: Volatility predictions are probabilistic and should not be treated as certainties
- **Browser Compatibility**: Internet Explorer not supported; users should use modern browsers
- **Mobile Data Usage**: Heatmap visualizations can consume significant data (2-5 MB per generation)

### Roadmap and Future Enhancements
- **Phase 2**: Live market data integration (real-time NSE futures prices)
- **Phase 3**: Mobile applications (iOS and Android native apps)
- **Phase 4**: Social features (strategy sharing, community discussions)
- **Phase 5**: Portfolio tracking and management tools
- **Phase 6**: Automated trading strategy backtesting

---

## Conclusion

The NSE Options Pricer Platform represents a comprehensive solution for derivatives education and analysis in the Kenyan market, combining professional-grade quantitative models, AI-powered assistance, and seamless local payment integration. By making sophisticated financial analytics accessible and affordable, the platform supports the growth of informed, confident derivatives market participants essential for Kenya's financial market development.

The system's architecture prioritizes accuracy, security, and user experience, ensuring that educational features maintain professional standards while remaining approachable for learners at all levels. Through continuous enhancement and community feedback, the platform aims to evolve alongside Kenya's derivatives market, providing the tools and knowledge necessary for sustainable, responsible market participation.

---

## Appendix

### Glossary of Technical Terms

**Black-76 Model**: Options pricing model specifically designed for European options on futures contracts, modified from the Black-Scholes model to account for futures as the underlying asset.

**JWT (JSON Web Token)**: Compact, URL-safe means of representing claims to be transferred between two parties, used for authentication and information exchange.

**STK Push**: M-Pesa feature that initiates payment prompts directly on customer phones without requiring manual USSD navigation.

**Daraja API**: Safaricom's developer API platform providing programmatic access to M-Pesa services.

**MongoDB**: NoSQL document database providing flexible schema design and horizontal scalability.

**Flask-RESTX**: Extension for Flask that adds support for quickly building REST APIs with automatic Swagger documentation.

**Plotly.js**: JavaScript graphing library built on D3.js and stack.gl, used for interactive, publication-quality graphs.

**Bcrypt**: Password hashing function designed specifically for secure password storage with built-in salt generation.

### API Reference Summary

Complete API documentation available at `https://yourdomain.com/api/docs` (Swagger UI).

**Authentication**: All protected endpoints require `Authorization: Bearer <token>` header.

**Rate Limiting**: 100 requests per minute per IP for anonymous users, 500 requests per minute for authenticated users.

**Error Format**: All errors return JSON with structure `{"error": "Error message", "code": "ERROR_CODE"}`

### Contact Information

**Development Team**: dev@nse-options.co.ke
**Support**: support@nse-options.co.ke
**Business Inquiries**: info@nse-options.co.ke

**Physical Address**:
[Your Company Name]
[Address Line 1]
[Address Line 2]
Nairobi, Kenya

**Social Media**:
- Twitter: @NSEOptionsPricer
- LinkedIn: NSE Options Pricer
- GitHub: github.com/nse-options-pricer

---

*Document Version*: 1.0
*Last Updated*: June 10, 2025
*Document Owner*: NSE Options Pricer Development Team

---

© 2025 NSE Options Pricer Platform. All rights reserved.
