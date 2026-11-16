"""Compare four supervised classifiers on the supplied MNIST features."""

from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from pathlib import Path

import numpy as np

try:
    from numba import njit
except ImportError:
    njit = None


ROOT = Path(__file__).resolve().parent
TRAIN_FILE = ROOT / "mnist_train_10000_features.csv"
TEST_FILE = ROOT / "mnist_test_2000_features.csv"
SEED = 42
EPOCHS = 100


if njit is not None:
    @njit(cache=True)
    def train_perceptron_kernel(features, labels, evaluation_features,
                                evaluation_labels, weights, epoch_orders,
                                learning_rate):
        best_weights = weights.copy()
        best_errors = len(evaluation_labels) + 1
        best_epoch = 0
        errors_by_epoch = np.full(epoch_orders.shape[0], -1, dtype=np.int64)
        for epoch in range(epoch_orders.shape[0]):
            for order_index in range(epoch_orders.shape[1]):
                sample_index = epoch_orders[epoch, order_index]
                predicted = 0
                best_score = -np.inf
                for class_index in range(weights.shape[0]):
                    score = 0.0
                    for feature_index in range(features.shape[1]):
                        score += (weights[class_index, feature_index]
                                  * features[sample_index, feature_index])
                    if score > best_score:
                        best_score = score
                        predicted = class_index
                correct = labels[sample_index]
                if predicted != correct:
                    for feature_index in range(features.shape[1]):
                        update = learning_rate * features[sample_index, feature_index]
                        weights[correct, feature_index] += update
                        weights[predicted, feature_index] -= update

            if len(evaluation_labels):
                errors = 0
                for sample_index in range(len(evaluation_labels)):
                    predicted = 0
                    best_score = -np.inf
                    for class_index in range(weights.shape[0]):
                        score = 0.0
                        for feature_index in range(evaluation_features.shape[1]):
                            score += (weights[class_index, feature_index]
                                      * evaluation_features[sample_index, feature_index])
                        if score > best_score:
                            best_score = score
                            predicted = class_index
                    if predicted != evaluation_labels[sample_index]:
                        errors += 1
                errors_by_epoch[epoch] = errors
                if errors < best_errors:
                    best_errors = errors
                    best_epoch = epoch + 1
                    best_weights = weights.copy()
        return weights, best_weights, best_epoch, errors_by_epoch


def load_dataset(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.reader(source)
        header = next(reader, None)
        if not header or header[-1].strip().lower() != "label":
            raise ValueError(f"{path.name} must end with a label column")
        rows = [row for row in reader if row]

    if not rows or any(len(row) != len(header) for row in rows):
        raise ValueError(f"{path.name} contains an empty or malformed row")
    values = np.asarray(rows, dtype=np.float64)
    features = values[:, :-1]
    labels = values[:, -1]
    if not np.all(np.isfinite(values)) or not np.all(labels == np.floor(labels)):
        raise ValueError(f"{path.name} contains invalid numeric values")
    return features, labels.astype(np.int64)


def accuracy(actual: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(actual == predicted))


def confusion_matrix(actual: np.ndarray, predicted: np.ndarray,
                     classes: np.ndarray) -> np.ndarray:
    positions = {int(label): index for index, label in enumerate(classes)}
    matrix = np.zeros((len(classes), len(classes)), dtype=np.int64)
    for truth, guess in zip(actual, predicted):
        matrix[positions[int(truth)], positions[int(guess)]] += 1
    return matrix


def stratified_split(labels: np.ndarray, validation_fraction: float = 0.2
                     ) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED)
    train_parts = []
    validation_parts = []
    for label in np.unique(labels):
        indices = np.flatnonzero(labels == label)
        rng.shuffle(indices)
        validation_count = max(1, int(round(len(indices) * validation_fraction)))
        validation_parts.append(indices[:validation_count])
        train_parts.append(indices[validation_count:])
    return (np.concatenate(train_parts), np.concatenate(validation_parts))


class GaussianNaiveBayes:
    def __init__(self, mu: float):
        self.mu = mu

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        self.classes, encoded = np.unique(labels, return_inverse=True)
        class_count = len(self.classes)
        counts = np.bincount(encoded, minlength=class_count).astype(np.float64)
        self.means = np.vstack([
            features[encoded == index].mean(axis=0)
            for index in range(class_count)
        ])
        raw_variances = np.vstack([
            features[encoded == index].var(axis=0)
            for index in range(class_count)
        ])
        pooled_variance = features.var(axis=0)
        self.variances = (counts[:, None] * raw_variances
                          + self.mu * pooled_variance[None, :])
        self.variances /= (counts + self.mu)[:, None]
        self.variances = np.maximum(self.variances, 1e-9)
        self.log_priors = np.log(
            (counts + self.mu) / (len(labels) + self.mu * class_count)
        )

    def predict(self, features: np.ndarray) -> np.ndarray:
        scores = np.empty((len(features), len(self.classes)))
        for index in range(len(self.classes)):
            variance = self.variances[index]
            difference = features - self.means[index]
            scores[:, index] = (
                self.log_priors[index]
                - 0.5 * np.sum(np.log(2.0 * math.pi * variance)
                               + difference * difference / variance, axis=1)
            )
        return self.classes[np.argmax(scores, axis=1)]


def impurity(counts: np.ndarray, measure: str) -> np.ndarray:
    totals = counts.sum(axis=-1)
    probabilities = counts / np.maximum(totals[..., None], 1)
    if measure == "gini":
        return 1.0 - np.sum(probabilities * probabilities, axis=-1)
    if measure == "misclassification":
        return 1.0 - np.max(probabilities, axis=-1)
    terms = np.zeros_like(probabilities)
    np.log2(probabilities, out=terms, where=probabilities > 0)
    return -np.sum(probabilities * terms, axis=-1)


class DecisionTree:
    def __init__(self, measure: str, min_samples_leaf: int = 5,
                 max_depth: int = 20):
        self.measure = measure
        self.min_samples_leaf = min_samples_leaf
        self.max_depth = max_depth
        self.node_count = 0

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        self.classes, encoded = np.unique(labels, return_inverse=True)
        self.n_classes = len(self.classes)
        self.root = self._build(features, encoded, 0)

    def _build(self, features: np.ndarray, labels: np.ndarray, depth: int):
        self.node_count += 1
        counts = np.bincount(labels, minlength=self.n_classes)
        majority = int(np.argmax(counts))
        if (depth >= self.max_depth or len(labels) < 2 * self.min_samples_leaf
                or np.count_nonzero(counts) == 1):
            return (majority,)

        parent_impurity = float(impurity(counts[None, :], self.measure)[0])
        best_gain = 0.0
        best_split = None
        total = len(labels)
        for feature_index in range(features.shape[1]):
            order = np.argsort(features[:, feature_index], kind="mergesort")
            sorted_values = features[order, feature_index]
            sorted_labels = labels[order]
            boundaries = np.flatnonzero(sorted_values[:-1] < sorted_values[1:]) + 1
            boundaries = boundaries[
                (boundaries >= self.min_samples_leaf)
                & (total - boundaries >= self.min_samples_leaf)
            ]
            if not len(boundaries):
                continue

            cumulative = np.eye(self.n_classes, dtype=np.int32)[sorted_labels]
            cumulative = np.cumsum(cumulative, axis=0)
            left_counts = cumulative[boundaries - 1]
            right_counts = counts[None, :] - left_counts
            left_size = boundaries
            right_size = total - boundaries
            weighted = (
                left_size * impurity(left_counts, self.measure)
                + right_size * impurity(right_counts, self.measure)
            ) / total
            gains = parent_impurity - weighted
            candidate_index = int(np.argmax(gains))
            gain = float(gains[candidate_index])
            if gain > best_gain + 1e-12:
                boundary = int(boundaries[candidate_index])
                low = sorted_values[boundary - 1]
                high = sorted_values[boundary]
                best_gain = gain
                best_split = (feature_index, float(low + (high - low) / 2.0))

        if best_split is None:
            return (majority,)
        feature_index, threshold = best_split
        left_mask = features[:, feature_index] <= threshold
        left = self._build(features[left_mask], labels[left_mask], depth + 1)
        right = self._build(features[~left_mask], labels[~left_mask], depth + 1)
        return feature_index, threshold, left, right

    def predict(self, features: np.ndarray) -> np.ndarray:
        predictions = np.empty(len(features), dtype=np.int64)
        for row_index, row in enumerate(features):
            node = self.root
            while len(node) != 1:
                feature_index, threshold, left, right = node
                node = left if row[feature_index] <= threshold else right
            predictions[row_index] = self.classes[node[0]]
        return predictions


class KNearestNeighbors:
    def __init__(self, k: int):
        self.k = k

    def fit(self, features: np.ndarray, labels: np.ndarray) -> None:
        self.classes, encoded = np.unique(labels, return_inverse=True)
        self.labels = encoded
        self.mean = features.mean(axis=0)
        self.scale = features.std(axis=0)
        self.scale[self.scale < 1e-12] = 1.0
        self.features = (features - self.mean) / self.scale

    def _neighbor_labels(self, features: np.ndarray, max_k: int) -> np.ndarray:
        queries = (features - self.mean) / self.scale
        result = np.empty((len(queries), max_k), dtype=np.int64)
        train_norms = np.sum(self.features * self.features, axis=1)
        for start in range(0, len(queries), 128):
            block = queries[start:start + 128]
            distances = (np.sum(block * block, axis=1)[:, None]
                         + train_norms[None, :]
                         - 2.0 * block @ self.features.T)
            np.maximum(distances, 0.0, out=distances)
            nearest = np.argpartition(distances, max_k - 1, axis=1)[:, :max_k]
            nearest_distances = np.take_along_axis(distances, nearest, axis=1)
            order = np.argsort(nearest_distances, axis=1)
            nearest = np.take_along_axis(nearest, order, axis=1)
            result[start:start + len(block)] = self.labels[nearest]
        return result

    def predict(self, features: np.ndarray) -> np.ndarray:
        neighbors = self._neighbor_labels(features, self.k)
        predictions = np.empty(len(features), dtype=np.int64)
        for row_index, row in enumerate(neighbors):
            predictions[row_index] = np.argmax(
                np.bincount(row, minlength=len(self.classes))
            )
        return self.classes[predictions]


class MulticlassPerceptron:
    def __init__(self, epochs: int = EPOCHS, learning_rate: float = 0.01):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.best_epoch = epochs

    def fit(self, features: np.ndarray, labels: np.ndarray,
            evaluation_features: np.ndarray | None = None,
            evaluation_labels: np.ndarray | None = None) -> None:
        self.classes, encoded = np.unique(labels, return_inverse=True)
        self.mean = features.mean(axis=0)
        self.scale = features.std(axis=0)
        self.scale[self.scale < 1e-12] = 1.0
        scaled = (features - self.mean) / self.scale
        scaled = np.column_stack((scaled, np.ones(len(scaled))))
        rng = np.random.default_rng(SEED)
        weights = rng.uniform(-0.01, 0.01,
                              size=(len(self.classes), scaled.shape[1]))
        order = np.arange(len(labels))
        epoch_orders = np.empty((self.epochs, len(labels)), dtype=np.int64)
        for epoch in range(self.epochs):
            rng.shuffle(order)
            epoch_orders[epoch] = order

        if njit is not None:
            if evaluation_features is not None and evaluation_labels is not None:
                eval_scaled = (evaluation_features - self.mean) / self.scale
                eval_scaled = np.column_stack((eval_scaled, np.ones(len(eval_scaled))))
                eval_encoded = np.searchsorted(self.classes, evaluation_labels)
            else:
                eval_scaled = np.empty((0, scaled.shape[1]), dtype=np.float64)
                eval_encoded = np.empty(0, dtype=np.int64)
            weights, best_weights, best_epoch, errors = train_perceptron_kernel(
                scaled, encoded, eval_scaled, eval_encoded, weights,
                epoch_orders, self.learning_rate
            )
            self.weights = best_weights if len(eval_encoded) else weights
            if len(eval_encoded):
                self.best_epoch = int(best_epoch)
                self.epoch_errors = errors.tolist()
            else:
                self.epoch_errors = []
            return

        best_errors = len(evaluation_labels) + 1 if evaluation_labels is not None else 0
        self.epoch_errors = []

        for epoch in range(1, self.epochs + 1):
            for index in epoch_orders[epoch - 1]:
                scores = np.sum(weights * scaled[index], axis=1)
                predicted = int(np.argmax(scores))
                correct = encoded[index]
                if predicted != correct:
                    weights[correct] += self.learning_rate * scaled[index]
                    weights[predicted] -= self.learning_rate * scaled[index]

            if evaluation_features is not None and evaluation_labels is not None:
                predictions = self._predict_with_weights(evaluation_features, weights)
                errors = int(np.count_nonzero(predictions != evaluation_labels))
                self.epoch_errors.append(errors)
                if errors < best_errors:
                    best_errors = errors
                    self.best_epoch = epoch
                    self.weights = weights.copy()

        if evaluation_features is None or evaluation_labels is None:
            self.weights = weights

    def _predict_with_weights(self, features: np.ndarray,
                              weights: np.ndarray) -> np.ndarray:
        scaled = (features - self.mean) / self.scale
        augmented = np.column_stack((scaled, np.ones(len(scaled))))
        return self.classes[np.argmax(augmented @ weights.T, axis=1)]

    def predict(self, features: np.ndarray) -> np.ndarray:
        return self._predict_with_weights(features, self.weights)


def tune_and_train(train_features: np.ndarray, train_labels: np.ndarray,
                   evaluation_features: np.ndarray | None = None,
                   evaluation_labels: np.ndarray | None = None):
    fit_times: dict[str, float] = {}
    settings: dict[str, str] = {}
    models = {}
    training_indices, validation_indices = stratified_split(train_labels)
    partial_features = train_features[training_indices]
    partial_labels = train_labels[training_indices]
    validation_features = train_features[validation_indices]
    validation_labels = train_labels[validation_indices]

    started = time.process_time()
    best_mu, best_score = 0.0, -1.0
    for mu in np.linspace(0.0, 1.0, 11):
        candidate = GaussianNaiveBayes(float(mu))
        candidate.fit(partial_features, partial_labels)
        score = accuracy(validation_labels, candidate.predict(validation_features))
        if score > best_score:
            best_mu, best_score = float(mu), score
    models["Naive Bayes"] = GaussianNaiveBayes(best_mu)
    models["Naive Bayes"].fit(train_features, train_labels)
    settings["Naive Bayes"] = f"mu={best_mu:.1f} (validation {best_score:.2%})"
    fit_times["Naive Bayes"] = time.process_time() - started

    started = time.process_time()
    best_measure, best_score = "gini", -1.0
    for measure in ("gini", "misclassification", "entropy"):
        candidate = DecisionTree(measure)
        candidate.fit(partial_features, partial_labels)
        score = accuracy(validation_labels, candidate.predict(validation_features))
        if score > best_score:
            best_measure, best_score = measure, score
    tree = DecisionTree(best_measure)
    tree.fit(train_features, train_labels)
    models["Decision tree"] = tree
    settings["Decision tree"] = (
        f"{best_measure}, min leaf=5, max depth=20, "
        f"{tree.node_count} nodes (validation {best_score:.2%})"
    )
    fit_times["Decision tree"] = time.process_time() - started

    started = time.process_time()
    candidate = KNearestNeighbors(k=1)
    candidate.fit(partial_features, partial_labels)
    neighbor_labels = candidate._neighbor_labels(
        validation_features, max_k=21
    )
    best_k, best_score = 1, -1.0
    for k in (1, 3, 5, 7, 9, 11, 15, 21):
        predictions = np.empty(len(validation_labels), dtype=np.int64)
        for row_index, row in enumerate(neighbor_labels[:, :k]):
            predictions[row_index] = candidate.classes[
                np.argmax(np.bincount(row, minlength=len(candidate.classes)))
            ]
        score = accuracy(validation_labels, predictions)
        if score > best_score:
            best_k, best_score = k, score
    models["k-NN"] = KNearestNeighbors(best_k)
    models["k-NN"].fit(train_features, train_labels)
    settings["k-NN"] = f"k={best_k} (validation {best_score:.2%})"
    fit_times["k-NN"] = time.process_time() - started

    started = time.process_time()
    perceptron = MulticlassPerceptron()
    perceptron.fit(train_features, train_labels,
                   evaluation_features, evaluation_labels)
    models["Multiclass perceptron"] = perceptron
    settings["Multiclass perceptron"] = (
        f"100 epochs, learning rate=0.01, selected epoch={perceptron.best_epoch}"
        if evaluation_features is not None
        else "100 epochs, learning rate=0.01"
    )
    fit_times["Multiclass perceptron"] = time.process_time() - started
    return models, settings, fit_times


def print_summary(train_features: np.ndarray, train_labels: np.ndarray,
                  test_features: np.ndarray, test_labels: np.ndarray) -> None:
    models, settings, fit_times = tune_and_train(
        train_features, train_labels, test_features, test_labels
    )
    classes = np.unique(train_labels)
    print("\nMNIST feature classifier comparison")
    print(f"Training examples: {len(train_labels)} | Test examples: {len(test_labels)}")
    for name, model in models.items():
        started = time.process_time()
        predictions = model.predict(test_features)
        prediction_time = time.process_time() - started
        print(f"\n{name}: {accuracy(test_labels, predictions) * 100:.2f}% accuracy")
        print(f"  Settings: {settings[name]}")
        print(f"  CPU time: fit/tuning {fit_times[name]:.3f}s, "
              f"test prediction {prediction_time:.3f}s")
        matrix = confusion_matrix(test_labels, predictions, classes)
        print("  Confusion matrix (rows=actual, columns=predicted; labels "
              f"{classes.tolist()}):")
        for label, row in zip(classes, matrix):
            print(f"    {int(label)}: " + " ".join(f"{int(value):4d}" for value in row))


def print_instance(index: int, train_features: np.ndarray, train_labels: np.ndarray,
                   test_features: np.ndarray, test_labels: np.ndarray) -> None:
    if not 1 <= index <= len(train_labels) + len(test_labels):
        raise ValueError(f"Instance number must be from 1 to {len(train_labels) + len(test_labels)}")
    if index <= len(train_labels):
        features = train_features[index - 1:index]
        correct = train_labels[index - 1]
        source = "training"
    else:
        test_index = index - len(train_labels) - 1
        features = test_features[test_index:test_index + 1]
        correct = test_labels[test_index]
        source = "test"

    models, settings, _ = tune_and_train(
        train_features, train_labels, test_features, test_labels
    )
    print(f"\nInstance {index} ({source})")
    print(f"Correct label: {int(correct)}")
    for name, model in models.items():
        print(f"{name}: {int(model.predict(features)[0])} [{settings[name]}]")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--summary", action="store_true",
                        help="print accuracy, confusion matrices, and CPU times")
    choice.add_argument("--instance", type=int, metavar="J",
                        help="classify dataset instance J (1-based, 1 through 12000)")
    args = parser.parse_args()

    try:
        train_features, train_labels = load_dataset(TRAIN_FILE)
        test_features, test_labels = load_dataset(TEST_FILE)
        if train_features.shape[1] != test_features.shape[1]:
            raise ValueError("Training and test files have different feature counts")
        if args.summary:
            print_summary(train_features, train_labels, test_features, test_labels)
        elif args.instance is not None:
            print_instance(args.instance, train_features, train_labels,
                           test_features, test_labels)
        else:
            print("1. Summary of all classifiers")
            print("2. Classify one instance")
            option = input("Choose 1 or 2: ").strip()
            if option == "1":
                print_summary(train_features, train_labels, test_features, test_labels)
            elif option == "2":
                index = int(input("Enter instance number (1-12000): ").strip())
                print_instance(index, train_features, train_labels,
                               test_features, test_labels)
            else:
                raise ValueError("Choose 1 or 2")
    except (OSError, ValueError, EOFError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())