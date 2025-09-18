# RooR: AI Behavior Analysis in Post-Quantum Cybersecurity

## Overview

RooR is a Python R\&D package designed to analyze the behavior of AI models in the context of post-quantum cybersecurity.
It provides tools to:

* Simulate post-quantum cryptographic attacks.
* Analyze system logs for anomalies.
* Evaluate the resilience of AI models against emerging threats.

This package is intended for research and development purposes in cybersecurity and AI resilience.

---

## Key Features

* **AI Behavioral Analysis**: Detect anomalies in logs using advanced machine learning techniques.
* **Post-Quantum Attack Simulation**: Simulate lattice-based and code-based cryptographic attacks.
* **Resilience Evaluation**: Assess AI model performance under post-quantum threat scenarios.
* **Report Generation**: Export results in JSON and CSV formats for easy integration and analysis.

---

## Installation

Install RooR using `pip`:

```bash
# Clone the repository
git clone https://github.com/eurocybersecurite/RooR.git
cd RooR

# Install the package
pip install .
```

> Note: For development purposes, you can also install in editable mode:
>
> ```bash
> pip install -e .
> ```

---

## Running Tests

To run the automated tests for this project, activate the virtual environment and use the `unittest` module:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run tests
python3 -m unittest discover tests
```

---

## Usage Examples

Here’s a quick example demonstrating the main functionalities:

```python
from RooR import behavioral_analysis, attack_simulation, report_generation
import pandas as pd

# --- 1. Simulate a post-quantum attack ---
target_model = "Quantum-Resistant AI Model"
attack_result = attack_simulation.simulate_lattice_based_attack(target_model)
report_generation.generate_json_report(attack_result, "attack_report.json")

# --- 2. Analyze logs for anomalies ---
log_data = {
    'timestamp': ['2023-10-27 10:00:00', '2023-10-27 10:05:00', '2023-10-27 10:10:00'],
    'event_type': ['login', 'logout', 'login']
}
pd.DataFrame(log_data).to_csv('dummy_logs.csv', index=False)

anomalies = behavioral_analysis.analyze_logs('dummy_logs.csv')
report_generation.generate_csv_report(anomalies, "anomalies_report.csv")

# --- 3. Evaluate model resilience ---
predictions = [1, 0, 1, 1, 0]
ground_truth = [1, 0, 1, 0, 1]

resilience = behavioral_analysis.evaluate_post_quantum_resilience(predictions, ground_truth)
report_generation.generate_json_report(resilience, "resilience_report.json")
```

---

## Contributing

Contributions are welcome!

* Open an issue to report bugs or request features.
* Submit a pull request for improvements.

Please follow standard Python packaging and testing practices.

---

## License

This project is licensed under the MIT License.

---

## Developer Information

* **Name**: ABDESSEMED Mohamed
* **Email**: [mohamed.abdessemed@eurocybersecurite.fr](mailto:mohamed.abdessemed@eurocybersecurite.fr)
