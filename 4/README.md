# CS 480 Project 4

This program compares Gaussian Naive Bayes, a numeric decision tree, k-nearest
neighbors, and a multiclass perceptron using the supplied MNIST feature CSVs.
It requires Python 3, NumPy, and Numba. Install dependencies with
`python -m pip install -r requirements.txt`. Keep both CSV files next to
`project4.py`.

Run the interactive menu:

```bash
python project4.py
```

Or run either mode directly:

```bash
python project4.py --summary
python project4.py --instance 10001
```

Instance numbers are 1-based: 1 through 10,000 refer to training rows, and
10,001 through 12,000 refer to test rows. The summary reports test accuracy,
confusion matrices, and process CPU time for tuning/fitting and prediction.

Hyperparameters are selected using a deterministic, stratified 80/20 split of
the training data. Naive Bayes tests `mu` from 0.0 through 1.0 in increments
of 0.1. Here `mu` is a pseudo-count: it smooths class priors toward a uniform
prior and shrinks class feature variances toward the pooled variance. The tree
compares Gini, misclassification error, and entropy, using numeric midpoint
splits with a minimum leaf size of 5 and maximum depth of 20. k-NN tests
`k = 1, 3, 5, 7, 9, 11, 15, 21` after standardizing features. The perceptron
uses standardized features, a bias feature, learning rate 0.01, and 100 epochs.
In summary mode it reports the epoch with the fewest test errors, as specified
in the assignment. Numba compiles the online update loop; if it is unavailable,
the program falls back to the equivalent NumPy implementation.