use crate::arrays::{predictions_to_numpy, scores_to_numpy, SequenceArray};
use crate::errors::PyAnomalyGridError;
use anomaly_grid::AnomalyDetector as RustAnomalyDetector;
use numpy::PyArray1;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::Py;
use std::collections::HashMap;

#[pyclass(name = "AnomalyDetector")]
pub struct PyAnomalyDetector {
    detector: Option<RustAnomalyDetector>,
    max_order: usize,
    // Add statistical modeling for proper sequence-level anomaly detection
    transition_counts: HashMap<Vec<String>, HashMap<String, f64>>,
    sequence_stats: SequenceStatistics,
    scoring_config: ScoringConfig,
    trained: bool,
}

#[derive(Default)]
struct SequenceStatistics {
    total_sequences: usize,
    avg_sequence_length: f64,
    vocab_size: usize,
    transition_entropy: f64,
}

/// Configuration for scoring weights and algorithm parameters
#[derive(Clone)]
struct ScoringConfig {
    likelihood_weight: f64,
    point_anomaly_weight: f64,
    pattern_deviation_weight: f64,
    smoothing_factor: f64,
    expected_diversity: f64,
}

impl Default for ScoringConfig {
    fn default() -> Self {
        Self {
            likelihood_weight: 0.85,        // FIXED: Much higher weight for likelihood
            point_anomaly_weight: 0.10,     // FIXED: Reduced weight
            pattern_deviation_weight: 0.05, // FIXED: Minimal weight
            smoothing_factor: 1.0,
            expected_diversity: 0.7,
        }
    }
}

#[pymethods]
impl PyAnomalyDetector {
    #[new]
    fn new(max_order: Option<usize>) -> PyResult<Self> {
        let max_order = max_order.unwrap_or(4); // Safe: unwrap_or provides default

        Ok(Self {
            detector: None,
            max_order,
            transition_counts: HashMap::new(),
            sequence_stats: SequenceStatistics::default(),
            scoring_config: ScoringConfig::default(),
            trained: false,
        })
    }

    /// FIXED: Proper unsupervised training for sequence-level anomaly detection
    fn fit(&mut self, sequences: &PyAny) -> PyResult<()> {
        let seq_array = SequenceArray::from_python(sequences)?;
        seq_array.validate()?;

        // Initialize detector
        let mut detector =
            RustAnomalyDetector::new(self.max_order).map_err(PyAnomalyGridError::from)?;

        // FIXED: Build proper statistical model for sequence-level detection
        self.build_sequence_model(&seq_array)?;

        // Train the underlying detector on normal patterns
        for sequence in seq_array.as_slice() {
            detector.train(sequence).map_err(PyAnomalyGridError::from)?;
        }

        self.detector = Some(detector);
        self.trained = true;
        Ok(())
    }

    /// FIXED: Proper sequence-level probability scoring with normalization
    fn predict_proba(&self, sequences: &PyAny) -> PyResult<Py<PyArray1<f64>>> {
        if !self.trained {
            return Err(PyAnomalyGridError::not_fitted());
        }

        let detector = self
            .detector
            .as_ref()
            .ok_or_else(|| PyAnomalyGridError::not_fitted())?;
        let seq_array = SequenceArray::from_python(sequences)?;
        seq_array.validate()?;

        let mut scores = Vec::with_capacity(seq_array.len());

        for sequence in seq_array.as_slice() {
            // FIXED: Calculate proper sequence-level anomaly probability
            let score = self.calculate_sequence_anomaly_probability(sequence, detector)?;
            scores.push(score);
        }

        // FIXED: Add min-max normalization like the baseline
        if scores.len() > 1 {
            let min_score = scores.iter().cloned().fold(f64::INFINITY, f64::min);
            let max_score = scores.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

            if (max_score - min_score).abs() > 1e-10 {
                for score in &mut scores {
                    *score = (*score - min_score) / (max_score - min_score);
                }
            }
        }

        Python::with_gil(|py| Ok(scores_to_numpy(py, scores)))
    }

    fn predict(&self, sequences: &PyAny, threshold: Option<f64>) -> PyResult<Py<PyArray1<bool>>> {
        let threshold = threshold.unwrap_or(0.1);
        let scores = self.predict_proba(sequences)?;

        Python::with_gil(|py| {
            let scores_array = scores.as_ref(py);
            let predictions: Vec<bool> = scores_array
                .readonly()
                .as_array()
                .iter()
                .map(|&score| score >= threshold)
                .collect();

            Ok(predictions_to_numpy(py, predictions))
        })
    }

    fn get_metrics(&self) -> PyResult<Py<PyDict>> {
        if !self.trained {
            return Err(PyAnomalyGridError::not_fitted());
        }

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("training_time_ms", 0.0)?;
            dict.set_item("context_count", self.transition_counts.len())?;
            dict.set_item("memory_bytes", self.estimate_memory_usage())?;
            dict.set_item("vocab_size", self.sequence_stats.vocab_size)?;
            dict.set_item(
                "avg_sequence_length",
                self.sequence_stats.avg_sequence_length,
            )?;
            dict.set_item("transition_entropy", self.sequence_stats.transition_entropy)?;
            Ok(dict.into())
        })
    }
}

impl PyAnomalyDetector {
    /// FIXED: Build proper statistical model for sequence-level anomaly detection
    fn build_sequence_model(&mut self, seq_array: &SequenceArray) -> PyResult<()> {
        let sequences = seq_array.as_slice();

        // Build transition probability model
        let mut vocab = std::collections::HashSet::new();
        let mut total_length = 0;

        for sequence in sequences {
            total_length += sequence.len();

            // Add to vocabulary
            for token in sequence {
                vocab.insert(token.clone());
            }

            // Build n-gram transition counts with smoothing
            for order in 1..=self.max_order {
                if sequence.len() >= order + 1 {
                    for i in 0..=(sequence.len() - order - 1) {
                        let context: Vec<String> = sequence[i..i + order].to_vec();
                        let next_token = sequence[i + order].clone();

                        *self
                            .transition_counts
                            .entry(context)
                            .or_insert_with(HashMap::new)
                            .entry(next_token)
                            .or_insert(0.0) += 1.0;
                    }
                }
            }
        }

        // Calculate statistics
        self.sequence_stats.total_sequences = sequences.len();
        self.sequence_stats.avg_sequence_length = total_length as f64 / sequences.len() as f64;
        self.sequence_stats.vocab_size = vocab.len();

        // Apply Laplace smoothing and normalize probabilities
        self.apply_smoothing_and_normalize();

        // Calculate transition entropy
        self.sequence_stats.transition_entropy = self.calculate_transition_entropy();

        Ok(())
    }

    /// Apply Laplace smoothing and normalize transition probabilities
    fn apply_smoothing_and_normalize(&mut self) {
        let smoothing_factor = self.scoring_config.smoothing_factor;
        let vocab_size = self.sequence_stats.vocab_size as f64;

        for (_, next_tokens) in self.transition_counts.iter_mut() {
            let total_count: f64 =
                next_tokens.values().sum::<f64>() + vocab_size * smoothing_factor;

            for count in next_tokens.values_mut() {
                *count = (*count + smoothing_factor) / total_count;
            }
        }
    }

    /// Calculate transition entropy for model complexity assessment
    fn calculate_transition_entropy(&self) -> f64 {
        let mut total_entropy = 0.0;
        let mut total_contexts = 0;

        for (_, next_tokens) in &self.transition_counts {
            let mut context_entropy = 0.0;
            for &prob in next_tokens.values() {
                if prob > 0.0 {
                    context_entropy -= prob * prob.log2();
                }
            }
            total_entropy += context_entropy;
            total_contexts += 1;
        }

        if total_contexts > 0 {
            total_entropy / total_contexts as f64
        } else {
            0.0
        }
    }

    /// FIXED: Calculate proper sequence-level anomaly probability
    fn calculate_sequence_anomaly_probability(
        &self,
        sequence: &[String],
        detector: &RustAnomalyDetector,
    ) -> PyResult<f64> {
        // Method 1: Statistical likelihood approach
        let likelihood_score = self.calculate_sequence_likelihood(sequence);

        // Method 2: Point anomaly aggregation (improved)
        let point_anomaly_score = self.calculate_point_anomaly_score(sequence, detector)?;

        // Method 3: Sequence pattern deviation
        let pattern_deviation_score = self.calculate_pattern_deviation(sequence);

        // Combine scores with configurable weights
        let combined_score = self.scoring_config.likelihood_weight * likelihood_score
            + self.scoring_config.point_anomaly_weight * point_anomaly_score
            + self.scoring_config.pattern_deviation_weight * pattern_deviation_score;

        // Apply adaptive calibration based on training statistics
        Ok(self.adaptive_calibration(combined_score))
    }

    /// FIXED: Simplified likelihood calculation closer to baseline approach
    fn calculate_sequence_likelihood(&self, sequence: &[String]) -> f64 {
        if sequence.len() <= self.max_order {
            return 0.5; // Same as baseline for short sequences
        }

        let mut log_prob = 0.0;
        let mut count = 0;

        // FIXED: Use single order (max_order) like baseline, not variable order
        for i in 0..=(sequence.len() - self.max_order - 1) {
            let context: Vec<String> = sequence[i..i + self.max_order].to_vec();
            let next_token = &sequence[i + self.max_order];

            // FIXED: Simplified probability calculation like baseline
            let prob = if let Some(next_tokens) = self.transition_counts.get(&context) {
                if let Some(&prob) = next_tokens.get(next_token) {
                    prob
                } else {
                    // FIXED: Simple fallback like baseline
                    1.0 / self.sequence_stats.vocab_size as f64
                }
            } else {
                // FIXED: Simple fallback like baseline
                1.0 / self.sequence_stats.vocab_size as f64
            };

            log_prob += (prob + 1e-10).ln();
            count += 1;
        }

        // FIXED: Convert to anomaly score like baseline
        let avg_log_prob = if count > 0 {
            log_prob / count as f64
        } else {
            -10.0
        };
        -avg_log_prob // Negative log-likelihood as anomaly score
    }



    /// IMPROVED: Better point anomaly aggregation
    fn calculate_point_anomaly_score(
        &self,
        sequence: &[String],
        detector: &RustAnomalyDetector,
    ) -> PyResult<f64> {
        // Use multiple thresholds for better sensitivity
        let thresholds = [0.1, 0.3, 0.5];
        let mut weighted_score = 0.0;

        for (i, &threshold) in thresholds.iter().enumerate() {
            let anomalies = detector
                .detect_anomalies(sequence, threshold)
                .map_err(PyAnomalyGridError::from)?;

            if !anomalies.is_empty() {
                // Calculate coverage and intensity
                let coverage = anomalies.len() as f64 / sequence.len() as f64;
                let avg_strength = anomalies.iter().map(|a| a.anomaly_strength).sum::<f64>()
                    / anomalies.len() as f64;

                let threshold_score = coverage * avg_strength;
                let weight = 1.0 / (i + 1) as f64; // Higher weight for lower thresholds
                weighted_score += weight * threshold_score;
            }
        }

        Ok(weighted_score.min(1.0))
    }

    /// Calculate pattern deviation score
    fn calculate_pattern_deviation(&self, sequence: &[String]) -> f64 {
        // Check for repetitive patterns (common in anomalies)
        let repetition_score = self.calculate_repetition_score(sequence);

        // Check for length deviation
        let length_deviation = (sequence.len() as f64 - self.sequence_stats.avg_sequence_length)
            .abs()
            / self.sequence_stats.avg_sequence_length;

        // Check for vocabulary deviation
        let vocab_deviation = self.calculate_vocab_deviation(sequence);

        // Combine pattern deviations
        (repetition_score + length_deviation.min(1.0) + vocab_deviation) / 3.0
    }

    /// Calculate repetition score (high repetition = anomalous)
    fn calculate_repetition_score(&self, sequence: &[String]) -> f64 {
        if sequence.len() < 3 {
            return 0.0;
        }

        let mut repetitions = 0;
        for i in 1..sequence.len() {
            if sequence[i] == sequence[i - 1] {
                repetitions += 1;
            }
        }

        (repetitions as f64 / (sequence.len() - 1) as f64).min(1.0)
    }

    /// Calculate vocabulary deviation
    fn calculate_vocab_deviation(&self, sequence: &[String]) -> f64 {
        let unique_tokens: std::collections::HashSet<_> = sequence.iter().collect();
        let diversity = unique_tokens.len() as f64 / sequence.len() as f64;

        // Very low diversity (repetitive) or very high diversity (random) is anomalous
        let expected_diversity = self.scoring_config.expected_diversity;
        (diversity - expected_diversity).abs().min(1.0)
    }

    /// FIXED: Much gentler adaptive calibration that preserves score relationships
    fn adaptive_calibration(&self, raw_score: f64) -> f64 {
        // FIXED: Much gentler calibration that doesn't distort the natural likelihood ordering

        // Simple sigmoid with gentle parameters
        let steepness = 1.0; // FIXED: Much gentler than 3.0-7.0
        let midpoint = 0.5; // FIXED: Neutral midpoint instead of adaptive

        // Apply gentle sigmoid that preserves relative ordering
        let calibrated_score = 1.0 / (1.0 + (-steepness * (raw_score - midpoint)).exp());

        // FIXED: Minimal adjustment to preserve natural score distribution
        calibrated_score.min(0.999).max(0.001)
    }

    /// Estimate memory usage
    fn estimate_memory_usage(&self) -> usize {
        let mut size = std::mem::size_of::<Self>();

        for (context, next_tokens) in &self.transition_counts {
            size += context.iter().map(|s| s.len()).sum::<usize>();
            size +=
                next_tokens.len() * (std::mem::size_of::<String>() + std::mem::size_of::<f64>());
        }

        size
    }
}
