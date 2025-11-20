ABSTRACT
This project presents the design and development of a web-based pricing and learning tool for European-style options on futures, tailored to Kenya’s financial market. The tool applies the Black-76 model to compute theoretical option prices using user-supplied parameters such as futures prices, strike prices, volatility, and interest rates. Additional modules include calculation of option Greeks, profit-and-loss simulations, and interactive strategy visualizers, all aimed at improving understanding of derivatives trading.
Given the limited availability of live market data and educational resources in the Kenyan context, the platform incorporates simulated data and a user-friendly interface built using Streamlit. It integrates visual elements like heatmaps to enhance comprehension and includes support for local conventions such as quarterly expiries and KES currency formatting. The goal is to support learning, experimentation, and awareness among students, traders, and retail investors engaging with NSE’s derivatives market.





CHAPTER 1:  INTRODUCTION
1.1 Background
The global derivatives market plays a vital role in helping investors manage financial risk, improve returns, and allocate capital more efficiently. Options on futures allow traders to lock in prices for future contracts, with cash settlement at maturity. These instruments help investors hedge against fluctuations in stock prices and market indices.
In Kenya, the Nairobi Securities Exchange (NSE) launched its derivatives market, known as NEXT, in July 2019. It introduced futures contracts on key stocks such as Safaricom, KCB, Equity Group, and ABSA, as well as index futures like the NSE 25 and Mini NSE 25. These contracts are traded daily from 9 AM to 3 PM and are settled in cash (Strathmore Business School, 2024).
Despite these advancements, participation in the market remains low. While institutional investors have begun trading, many individual investors lack the tools and resources to price options, understand risk, or test trading strategies in a local context. This gap in access and education continues to limit market growth. A recent student-led study highlighted key barriers to participation, including high transaction costs, low investor awareness, weak risk management, and a fragmented regulatory framework (Strathmore Business School, 2024).
In response to these challenges and to broaden the range of available instruments, the NSE has announced plans to introduce options on futures. This aims to offer investors more advanced risk management tools and encourage deeper market participation (Nairobi Securities Exchange, 2024).
This proposal presents a Python-based platform using the Black 76 model to support derivatives education and trading. The platform will simulate option prices, calculate risk metrics known as Greeks, and display profit and loss charts. By making financial models interactive and practical, the tool will help investors and students engage more confidently with Kenya’s derivatives market.
1.2 Problem Statement
Despite major steps in setting up a derivatives market, the Nairobi Securities Exchange (NSE) still faces low use of options on futures. This is especially true among retail investors and other small market players. The NSE offers European-style options that are settled in cash. These include options on single stocks and index futures. However, trading activity remains low, and many investors do not fully understand how these products work 
One major reason for this is the lack of simple and practical tools to help users price and test options strategies using Kenyan market data. Most tools available today are made for global markets. They often need advanced financial knowledge or technical skills, which many local users do not have (Viva Africa LLP, 2017). Also, there are few local learning resources that link theory, such as the Black 76 pricing model, to real trading on the NSE (Strathmore Business School, 2024).
This lack of tools affects retail investors who cannot easily measure risk or expected returns from trading options. As a result, the NSE's goal of growing the derivatives market is held back due to limited user participation and market knowledge (Kisaka & Meso, 2024; ResearchGate, 2024).
According to the NSE’s August 2024 report, while futures on stocks and indices are gaining some traction, options trading is still mainly handled by a small group of institutional traders. Most retail investors have not entered the market in any meaningful way (Nairobi Securities Exchange, 2024). Unless tools are developed to help users in Kenya simulate, price, and understand options contracts in their own currency and using NSE data and schedules, these products will remain underused. Their full value as risk management or investment tools will not be realized (Cytonn Investments, 2023).

1.3 Objectives
1.3.1 Main Objective
To develop a Python web app to price European‐style futures options, simulates P&L, calculate Greeks, and charts strategies.
1.3.2 Specific Objectives
The system will be able to: 
	•	To implement the Black 76 model for pricing European options on single-stock and index futures using user inputs such as futures price, strike price, time to expiry, volatility, and interest rate.
	•	To calculate and display option Greeks including delta, gamma, vega, and theta to help users understand price and risk changes.
	•	To build a profit and loss simulator that includes transaction costs and shows how option values change with different market prices.
	•	To develop a strategy visualizer that allows users to create and analyze basic multi-leg options strategies using a simple chart-based interface.
	•	To deploy an interactive web platform that uses Kenyan market data and includes a chatbot to explain key terms and concepts for new users.










1.5 Scope and Limitations of the Study
This study focuses on the development of a Python-based web application that models, prices, and visualizes European-style options on futures using the Black 76 model. The tool is designed with Kenyan market conditions in mind, specifically aligning with the instruments and conventions of the Nairobi Securities Exchange. It includes features such as option pricing, calculation of Greeks (delta, gamma, vega, theta), a profit and loss simulator, and a strategy visualizer for basic multi-leg positions like bull spreads and straddles. The system uses local market settings such as Kenyan Shilling pricing, quarterly expiry dates in March, June, September, and December, and NSE trading hours from 9:00 AM to 3:00 PM. The application is deployed through Streamlit to allow easy access for students, educators, and retail investors through any browser. An AI-powered chatbot is also included to explain key financial terms and support self-paced learning.
However, this study has several limitations. It does not cover the pricing of American-style or exotic options. It does not connect to live trading platforms or execute real-time trades. The application does not support advanced portfolio risk analysis or simulations involving multiple asset classes. It also does not include high-frequency data or real-time market feeds. The focus is purely on education, modeling, and strategy testing based on historical or user-input data under simplified conditions.
1.6 Significance of the Study
This study is important because it addresses a key gap in the understanding and use of derivatives in Kenya. Although the Nairobi Securities Exchange has introduced options on futures, many investors, students, and educators still lack the tools to apply this knowledge in a practical way. By creating an easy-to-use web platform based on the Black 76 model, this project makes complex financial concepts more accessible to a wider audience.
The tool supports learning by allowing users to simulate option prices, calculate risk measures, and visualize strategies using real market conditions. This hands-on approach helps retail investors make better decisions, supports lecturers and students in their academic work, and encourages greater participation in the Kenyan derivatives market. The addition of an AI-powered chatbot further enhances the learning experience by providing instant explanations of key terms and concepts.
Overall, the study contributes to financial literacy, market development, and the practical application of financial theory in emerging markets like Kenya.



CHAPTER 2: LITERATURE REVIEW
2.1 Introduction
Pricing derivative instruments is a key part of modern finance. One important type of derivative is the European-style option on futures contracts. These options are widely used for hedging and speculation in both advanced and developing financial markets. Accurate pricing of these contracts helps improve market efficiency, supports risk management, and allows traders to make informed decisions. One well-known model used to price these options is the Black 76 model. It was introduced by Fischer Black in 1976 as an update to the Black-Scholes model to handle futures and forward contracts (Black, 1976).
As financial technology continues to grow, it is not enough to simply develop pricing models. There is also a strong need for tools that are easy to use and help users understand how these models work. Open-source platforms, digital learning tools, and web-based applications now make it possible to create interactive systems where users can simulate outcomes, change inputs, and visualize results. Tools like profit and loss simulators, strategy analyzers, and heatmaps are becoming more common. These tools help learners and investors see how option prices react to changes in the market.
Although many such tools exist globally, there is a gap when it comes to adapting them to the needs of emerging markets like Kenya. The Nairobi Securities Exchange (NSE) started trading in futures in 2019, and options in 2024, offering European-style options that are settled in cash. These include futures options on stocks like Safaricom and Equity Group, as well as on index futures (Strathmore Business School, 2024; Nairobi Securities Exchange, 2024). However, usage of these products remains low. Many investors in Kenya do not have access to platforms that allow them to price or test options using local data. This lack of local tools and resources has slowed the growth of the derivatives market in the country (Cytonn Investments, 2023; Kisaka & Meso, 2024).
This literature review looks at previous research and tools in four main areas. First, it explores how the Black 76 model is used to price options on futures. Second, it examines how interactive tools support learning and trading in derivatives. Third, it reviews advanced models that go beyond Black 76. Lastly, it focuses on Kenya’s current market situation, including gaps in education and technology. By reviewing these areas, the study shows why a web-based tool built in Python, using local NSE settings and focused on ease of use, is necessary. The goal is to provide a tool that is not only technically correct but also useful and easy to understand for Kenyan investors, students, and educators.

2.2 Review of Related Works
Research on derivatives pricing has produced several models aimed at valuing options on futures contracts. One of the most widely used models is the Black 76 model, developed by Fischer Black in 1976. This model adjusts the original Black-Scholes framework by replacing the spot price with the futures price and discounting the payoff at the risk-free rate (Black, 1976). It is designed for European-style options, which can only be exercised at expiry, and assumes constant volatility. Despite its limitations, the Black 76 model remains a preferred choice in many financial markets due to its simplicity and analytical clarity.
Several researchers have worked on improving the Black 76 model to better reflect real market conditions. For instance, Swishchuk, Wu, and McCracken (2020) explored how the model performs in markets where futures prices may turn negative, such as in energy trading. They introduced mean-reverting processes and stochastic volatility to make pricing more realistic. While these advanced models offer more accuracy in volatile markets, they are more complex and less practical for educational use, especially in markets like Kenya where negative pricing is unlikely.
In addition to theoretical models, the rise of digital tools has led to new approaches in teaching and applying derivatives pricing. Singh (2025) developed a Python-based heatmap visualization that shows how option prices change across different strike prices and expiry dates. This method allows users to explore non-linear pricing behavior visually, which supports learning and practical understanding. Although Singh focused on equity options and did not include volatility as a factor, the study highlights the educational value of visual tools.
Web-based applications have also been developed to improve user engagement. Dros (2023) built an interactive platform that allows users to simulate Black-Scholes option pricing, view Greek values, and analyze profit and loss scenarios. The platform uses a browser interface and dynamic widgets to make learning easier. Though the tool was designed for developed markets and equity options, it demonstrates the power of interactivity in financial education. A similar approach could be adapted to support Black 76 pricing and reflect Kenyan market settings.
Locally, the Nairobi Securities Exchange has introduced European-style, cash-settled options on stock and index futures (Nairobi Securities Exchange, 2024). Despite this progress, adoption remains low. According to Strathmore Business School (2024), limited access to pricing tools, low investor awareness, and lack of practical learning platforms are key challenges. Business Daily Africa (2024) also noted that many investors find derivatives complex and intimidating, which further limits participation. These findings suggest that there is a need for tools that combine technical accuracy with local relevance and ease of use.
This review shows that while global tools and models are well developed, Kenya still lacks a localized, interactive system that allows students, retail investors, and educators to engage meaningfully with options on futures. A Python-based web platform using the Black 76 model, combined with visual tools and Kenyan market data, would fill this gap and support broader participation in the derivatives market.

2.3 Gaps Identified in the Literature
This project fills several important gaps in Kenya’s current tools for learning and using options on futures. First, it solves the problem of applying the Black 76 model correctly to futures traded on the Nairobi Securities Exchange. Many tools used today are not built for Kenya’s market and may not work well with local products.
Second, the project fills a gap in how option prices are shown. It includes a heatmap that lets users see how option prices change with both futures prices and market volatility. This makes it easier to understand how different factors affect option values.
Third, there is a lack of learning tools built for the Kenyan market. This project uses Kenyan Shilling pricing, local trading hours, and expiry dates used by the NSE. This helps students, investors, and teachers work with data they know and trust.
Finally, most tools today are made for experts or large financial firms. This project focuses on retail users by making the platform easy to use. It also includes a built-in AI chatbot to explain terms and help users learn at their own pace.

2.3 Summary
This literature review looked at key ideas, tools, and market issues related to building a learning platform for pricing European-style options on futures in Kenya. The Black 76 model, introduced by Black in 1976, is still the main method for pricing these options and works well in stable markets like Kenya. Studies show that tools like heatmaps and profit and loss simulators help people understand options better, but most existing tools are made for equity options in other markets. More advanced models exist, but they are too complex for everyday users. Reports from the Nairobi Securities Exchange and other sources show that very few people in Kenya use options on futures, mainly because there are not enough local tools or learning resources. This project aims to fill that gap.











CHAPTER 3 : METHODOLOGY
3.1 Introduction
This chapter explains how the entire project will be carried out from start to finish. It covers the research approach, system design, data sources, tools, and the way the system will be evaluated. The goal of the project is to build a working web application that prices options on futures using the Black-76 model and makes the results easy to understand for students, investors, and other users.
3.2 Research Design / Development Methodology
The project will follow an agile development method. This means the system will be built step by step, with regular testing and improvements based on feedback. Each part of the system will be created in a short cycle, and after every cycle, any necessary changes will be made before moving on to the next phase. This method is helpful when building interactive systems because it allows for flexibility. It also ensures that the system is tested and improved gradually instead of waiting until the end.
The system will be developed in different phases. First, the system requirements will be gathered. Then, the design phase will begin, where the structure and layout of the system will be planned. After that, the development phase will follow, where coding will be done. Once the system is working, it will go through testing to make sure everything works correctly. The final phase will be deployment, where the system is made available online.
3.3 System Requirements (Functional and Non-functional)
The system will need to perform several functions. It should allow users to input data such as futures price, strike price, interest rate, volatility, and time to expiry. It should then return the price of the option using the Black-76 model. The system should also show the Greeks, which are measures of how the option responds to changes in the market. Users should be able to view charts like payoff diagrams, profit and loss simulations, and heatmaps.
In addition to these functions, the system should be easy to use, fast to load, and visually clear. It should be accessible through a web browser without requiring any software installation. It should also handle different inputs without crashing or giving incorrect results.
3.4 Data Sources
The main source of data will be historical futures prices from the Nairobi Securities Exchange. These can be found in daily reports or summaries. Where real data is not available or is too expensive to access, simulated data will be used. Simulated data is created by making reasonable assumptions about how futures prices behave. For example, a range of futures prices can be created using past trends and known contract rules. This data will be used to calculate option prices and test how the system performs in different situations.
3.5 System Design and Architecture
The system will have a simple architecture made up of different parts that work together. The front end is the part users see. It will be built using Streamlit, which is a Python framework for creating web apps. The front end will include sliders, text boxes, and buttons for entering data and viewing results.
The back end is where calculations take place. This will include the code for the Black-76 model, the formulas for calculating Greeks, and the logic for drawing payoff charts. There will also be a module for handling simulated data. If in the future real-time data becomes available through an API, the system can be updated to connect to it.
The two parts, front end and back end, will communicate with each other. When the user enters a value, the front end sends the data to the back end, which performs the necessary calculations and sends the results back to the front end for display.

Figure 1 : A clean architecture diagram designed using Lucidchart to depict these interactions.
Link to diagram: Lucidchart document


3.6 Tools and Technologies to be Used
The system will be built entirely in Python. Streamlit will be used to create the web interface. The Black-76 model and Greeks calculations will use standard Python libraries such as NumPy and SciPy. Matplotlib or Plotly will be used for visualizations like heatmaps and payoff diagrams. For working with data, pandas will be used.
The artificial intelligence will be in the form of a simple chatbot using an open-source language model, Open-AI’s ChatGPT. This chatbot will explain basic financial terms to users. It will not store personal data and will only answer general questions related to the app.
The development will take place in Jupyter Notebook and VS Code, with testing done locally and then deployed to Streamlit Cloud for public use.
3.7 Evaluation Metrics
The system will be evaluated in different ways. First, the pricing engine will be tested by comparing results to known values from textbooks or other pricing calculators. Second, the interface will be tested for usability. Users will be asked if they can understand the outputs and navigate the system easily. Third, the visualizations will be reviewed to see if they help users understand complex options behavior.
User feedback will be collected from a small group of students or investment challenge participants. Their suggestions will help improve the system.
3.8 Ethical Considerations
This project does not collect or store user data. Users will input values such as strike price or time to expiry, but this information is not personal or sensitive. All data used is either publicly available or simulated. If any future updates involve collecting personal information, proper privacy measures will be added.
The chatbot will use only trusted open-source tools and will be limited to educational topics. Care will be taken to avoid giving financial advice. The purpose of the system is educational, not for actual trading.
5.2 Estimated Budget and Resources
The project will try to keep costs as low as possible. Most tools used are free and open-source. Development will be done using a personal laptop. Hosting will be done through Streamlit Cloud, which is free for small projects. No hardware, transport, or printing costs are expected.
However, access to live data from the Nairobi Securities Exchange would require a fee of 50,000 Kenyan Shillings per month, which is beyond the current budget. Therefore, simulated data and historical summaries will be used instead.
Resources needed include a stable internet connection, a laptop, and basic software such as Python, Streamlit, and Jupyter Notebook. These are all available for free.

If in the future the system is expanded to use real-time data or serve a larger user base, more advanced hosting or API services might be needed.
