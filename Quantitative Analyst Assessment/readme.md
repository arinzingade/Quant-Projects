
### Thought Process

My approach involved developing a system that allows for simultaneous analysis of price and volume to evaluate and rank the significance of various price levels. To achieve this, I employed a combination of market profiling and volume profiling techniques. This dual approach enables the identification of important price levels, ultimately facilitating the determination of support and resistance levels within a defined look-back period. By integrating these methodologies, I aimed to enhance the decision-making process for trading strategies and improve the accuracy of price assessments.

So essentially, you can stop at any time in the simulation and see the important prices - volume profile - market profile for that point in time, rather than making it static for the whole week, I wanted to make it more dynamic and flexible, as if real time trades were to be taken in the week.

![simulation](https://github.com/user-attachments/assets/2502ddb9-350a-4246-88d2-090a569db351)

### Definition of Important Price

In this analysis, an "important price" is determined by identifying peaks within the market profile distribution, which are further validated by corresponding volume levels. This approach relies on the concept that significant price levels are characterized by heightened trading activity, indicating areas of strong buyer or seller interest.

The simulation GIF demonstrates these important levels, marked by dashed lines. It illustrates how the market consistently tests these levels, reinforcing their significance as reliable support and resistance zones.

To quantify these important prices programmatically, I utilized the following functions in my code:

1. **`find_levels` Function:** This function applies a Gaussian kernel density estimation (KDE) to the given price data, calculating the probability density function (PDF). It identifies peaks in the PDF that represent significant price levels, taking into account the average true range (ATR) for dynamic weighting. The prominence threshold ensures that only the most relevant peaks are considered as important price levels.

    ```python
    def find_levels(price: np.array, atr: float, first_w: float = 0.1, atr_mult: float = 3.0, prom_thresh: float = 0.1):
        # Implementation code...
    ```

2. **`support_resistance_levels` Function:** This function computes the support and resistance levels over a specified look-back period. It leverages the log of the closing prices and incorporates the ATR to adjust the importance of each price level dynamically. By aggregating the identified levels for each time step, it provides a comprehensive view of the market's critical price zones.

    ```python
    def support_resistance_levels(data: pd.DataFrame, lookback: int, first_w: float = 0.01, atr_mult: float = 3.0, prom_thresh: float = 0.25):
        # Implementation code...
    ```

Through these methods, I established a robust framework for identifying and analyzing important price levels in the context of market dynamics.


### News flow for the given week

Despite the low-impact economic news for the week of May 27, 2024, markets continued to slide downward, reflecting broader concerns beyond the immediate data releases. Even with most indicators and central bank speeches aligning with expectations, investor sentiment remained weak. 

Key economic indicators, like Germany’s Ifo Business Climate, U.S. consumer confidence, and the U.S. GDP growth revision, largely painted a picture of modest growth and controlled inflation without major surprises. However, the steady declines in both consumer and business sentiment, coupled with persistently cautious Fed rhetoric, seemed to weigh on the markets. The underwhelming PMI figures from China, signaling slower manufacturing activity, further fueled fears of a global economic slowdown.

Without any positive economic catalysts, traders seemed to lean toward a risk-off sentiment, resulting in a steady decline across various asset classes. This ongoing sell-off highlighted the market’s sensitivity to any hint of global slowdown, amplified by concerns about sticky inflation, high interest rates, and geopolitical uncertainties. The continuous downward trend suggested that, even with no major disruptions, underlying worries about future growth prospects and tighter financial conditions dominated investor sentiment, pushing markets lower through the week.



