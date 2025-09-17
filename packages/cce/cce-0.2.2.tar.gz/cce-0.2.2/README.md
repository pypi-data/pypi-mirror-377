# CCE & RankEval: Confidence-Consistency Evaluation for Time Series Anomaly Detection

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
  <a href="https://pypi.org/project/cce/"><img src="https://img.shields.io/badge/PyPI-CCE-red.svg" alt="PyPI"></a>
  <a href="http://arxiv.org/abs/2509.01098"><img src="https://img.shields.io/badge/arXiv-2509.01098-b31b1b.svg" alt="arXiv"></a>
</p>

A comprehensive evaluation framework for time series anomaly detection metrics, focusing on confidence-consistency evaluation, robustness assessment, and discriminative power analysis. This implementation provides novel evaluation metrics and benchmarking tools to improve the reliability and comparability of anomaly detection models.

📄 **Paper**: [arXiv:2509.01098](http://arxiv.org/abs/2509.01098)  
🌐 **Website**: [CCE & RankEval](https://EmorZz1G.github.io/CCE/)

## 🚀 Features

- **Multi-metric Evaluation**: Support for various anomaly detection metrics (F1, AUC-ROC, VUS-PR, etc.)
- **Performance Benchmarking**: Latency analysis and theoretical ranking validation
- **Robustness Assessment**: Noise-resistant evaluation with variance consideration
- **Discriminative Power Analysis**: Both ranking-based and value-change-ratio-based approaches
- **Automated Testing**: Streamlined evaluation pipeline for new metrics
- **Real-world Dataset Support**: Comprehensive testing on multiple datasets

## 📦 Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install cce
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/EmorZz1G/CCE.git
cd CCE

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

**Note**: Build-related files are located in the `docs` directory. For detailed build instructions, please refer to `docs/*.md`.

## 🔧 Requirements

- Python 3.8+
- PyTorch
- NumPy
- Other dependencies (see `requirements.txt`)

## ⚙️ Configuration

After installation, you may need to configure the datasets path:

```bash
# Create a configuration file
cce config create

# Set your datasets directory
cce config set-datasets-path /path/to/your/datasets

# View current configuration
cce config show
```

For detailed configuration options, see [Configuration Guide](docs/CONFIGURATION_GUIDE.md).

## 📚 Quick Start

### Confidence-Consistency Evaluation (CCE)

```python
from cce import metrics
metricor = metrics.basic_metricor()
CCE_score = metricor.metric_CCE(labels, scores)
```

## RankEval

### Basic Usage

```bash
# Run baseline evaluation
. scripts/run_baseline.sh

# Run real-world dataset evaluation
. scripts/run_real_world.sh
```

### Adding New Metrics

1. **Implement the metric function** in `src/metrics/basic_metrics.py`:
   ```python
   def metric_NewMetric(labels, scores, **kwargs):
       # Your metric implementation
       return metric_value
   ```

2. **Add evaluation logic** in `src/evaluation/eval_metrics/eval_latency_baselines.py`:
   ```python
   elif baseline == 'NewMetric':
       with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='NewMetric') as data_item:
           result = metricor.metric_NewMetric(labels, scores)
           data_item['val'] = result
   ```

3. **Run the evaluation**:
   ```bash
   python src/evaluation/eval_metrics/eval_latency_baselines.py --baseline NewMetric
   ```

4. **View results** in `logs/NewMetric/`

## 🏗️ Project Structure

```
CCE/
├── src/                    # Source code
│   ├── metrics/           # Metric implementations
│   ├── evaluation/        # Evaluation framework
│   ├── models/            # Model implementations
│   ├── data_utils/        # Data processing utilities
│   ├── utils/             # Helper functions
│   └── scripts/           # Execution scripts
├──                   # Build and installation files
│   ├── setup.py           # Package setup configuration
│   ├── pyproject.toml     # Modern Python package config
│   ├── MANIFEST.in        # Package file inclusion
│   ├── BUILD.md           # Detailed build instructions
│   └── INSTALL.md         # Quick install guide
├── datasets/              # Dataset storage
├── logs/                  # Evaluation results
├── tests/                 # Test files
├── docs/                  # Documentation
├── requirements.txt       # Dependencies
├── setup.py               # Simple setup entry point
└── pyproject.toml         # Basic build configuration
```

## 📊 Supported Evaluations

- **Latency Analysis**: Metric computation time measurement
- **Theoretical Ranking**: Validation against theoretical expectations
- **Robustness Assessment**: Noise resistance evaluation
- **Discriminative Power**: Ranking-based and value-change-ratio analysis

## 🔄 Updates
- **2025-08-26**: Core evaluation framework implementation
- **2025-08-26**: Multi-metric support and benchmarking

## 📋 TODO List

- [ ] Automated standard evaluation pipeline
- [ ] Enhanced robustness assessment
- [ ] Advanced discriminative power analysis
- [ ] CI/CD integration for metric testing

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FTSAD**: For providing the time series anomaly detection evaluation framework
- **SimAD**: For dataset load.
- **TSB-AD**: For model implementation code
- **Community**: For feedback and contributions

## 📞 Contact

For questions and support, please open an issue on GitHub or contact the maintainers.

## 📖 Citation

If you find our work useful, please cite our paper and consider giving us a star ⭐.

```bibtex
@article{zhong2025cce,
  title={CCE: Confidence-Consistency Evaluation for Time Series Anomaly Detection},
  author={Zhong, Zhijie and Yu, Zhiwen and Cheung, Yiu-ming and Yang, Kaixiang},
  journal={arXiv preprint arXiv:2509.01098},
  year={2025}
}
```

---

**CCE** - Making time series anomaly detection evaluation more reliable and comprehensive.
