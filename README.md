# Prediction Accuracy and Error Monitoring 
---
The program analyzes the accuracy of the predictions against actual values for series of operations. It generates metrics that helps user analyze and better understand the performance, identify potential errors, and monitor how well their prediction model performs.

## Parameters Generated
---
The program generates the following key outputs:
1. Individual Errors (MAE Per Row)
	1. For each prediction, the program calculates how far it deviates from the actual value, by getting the absolute value of pred - actuals.
2. Error Flags
	1. When an individual prediction deviates too far from set threshold (you can change this in settings), it gets marked as an error (1).
3. Operation-level Accuracy
	1. Predictions grouped by operation, each gets an average error and an up-time accuracy, for measuring percentage of predictions that stayed within acceptable error limits. Eg. 90% up-time means 90% of its prediction stayed under that threshold.
4. Histogram of Accuracy
	1. Organizes operations into ranges of up-time accuracy (80+%, 90%+ etc.)
5. Visual Plots
	1. Scatter plot for visualizing each operation accuracy, and color coded by performance ranges.