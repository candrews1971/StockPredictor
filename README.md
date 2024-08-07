# StockPredictor

This project was created to simply demonstrate an exploration of various machine learning models, and utilization of general MLOPs techniques (to the extent that makes sense for a small project)



## Why a stock predictor?

It is well understood that stocks are generally considered a random walk, i.e. not very predictable very far out in the future.  However, a stock prediction problem does have several benefits for the purposes of exploring the ML and Deep Learning space:
- The problem can be approached in many different ways, lending itself to different types of machine learning models, including regression, classification, and clustering
- It is inherently time-series data, so we can approach it with Recurrent Neural Networks such as LSTM, Autoregressive models like ARIMA,  1-D convolutional Neural Netwoks, or LLMs.
- The decision making process for traders tends to follow a decision-tree method, where different indicators are weighed and compared to make a buy/sell decision.  I suspect this lends itself well to Random Forests, AdaBoost, XGBoost, and the like.
- By backtesting, we can compare to results achieved with my current strategy (not provided)
- 

Further, stocks do have a trend, which has causes that may be discernable with machine learning.

> todays price = yesterdays price + noise + drift(trend)

While this drift component may be small compared to the noise, over time it has an effect.  So it is not really reasonable to try to predict and actual price at any time in the future, but it may be possible to predict the probability of the stock being higher or lower after some time period, based upon the drift.  

Potential pitfalls:
- it is pretty much guaranteed that we will not achieve very good results.
- it is not clear what a good result would be to compare against
    - I will compare it against my strategy, which I beleive identifies reversals about 70% of the time, two days before they happen.
- in timeseries data, care must be taken not to introduce future-knowledge contamination. This is harder than it might seem.  I've seen many YouTube videos where they very happy with their results, but they are horribly contaminated.
- Manually providing Target labels to the data may cause inconsistencies and cause confusion for the model.
    - labeling a "BUY" point at the very apex of a trend reversal may not allow identification based on data for that to even be possible.  We may need another point, or more points in order to identify it.  
    - I've used several different labeling methods to see which might even be able to work reasonably