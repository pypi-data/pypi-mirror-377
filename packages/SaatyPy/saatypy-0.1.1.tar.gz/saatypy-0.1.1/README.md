# SaatyPy

SaatyPy is a Python package for Analytic Hierarchy Process (AHP) and Analytic Network Process (ANP) decision modeling.  
It provides robust, flexible, and well-tested tools for multi-criteria decision analysis, supporting both academic and business use cases.

The package is named in honor of **Thomas L. Saaty**, the originator of AHP and ANP methodologies.  
His pioneering work laid the foundation for modern multi-criteria decision making.

## Features
- AHP and ANP model builders
- Pairwise comparison matrices
- Consistency checks and error handling
- Matrix limiters and normalization utilities
- Reporting and result export
- Extensible and type-safe API

## Modules Overview
- **saatypy.ahp**: Build and solve AHP models (hierarchies, priorities, reporting)
- **saatypy.anp**: Build and solve ANP models (networks, supermatrices, limiters)
- **saatypy.components**: Core types, pairwise comparisons, error classes, math utilities
- **saatypy.reporting**: Generate reports and export results

## Installation
```bash
pip install saatypy
```
Or clone the repository and install locally:
```bash
git clone https://github.com/ehsanAhmadzadeh/saatypy.git
cd saatypy
pip install .
```

## Quick Start (AHP)
```python
from saatypy.ahp import AHPBuilder

model = (AHPBuilder()
    .add_criteria(["price", "quality", "service"])
    .add_alternatives(["A", "B", "C"])
    .build())

model.set_criteria_weights({"price": 0.5, "quality": 0.3, "service": 0.2})
for crit in ["price", "quality", "service"]:
    model.set_alt_priorities(crit, {
        ("A", "B"): 2.0,
        ("A", "C"): 3.0,
        ("B", "C"): 1.5
    })

priorities, labels = model.alternative_priorities()
print(dict(zip(labels, priorities)))
```

## Quick Start (ANP)
```python
from saatypy.anp import ANPBuilder
from saatypy.components.pairwise import PairwiseComparison

model = (ANPBuilder()
    .add_cluster("criteria", ["C1", "C2"])
    .add_alternatives(["A", "B"])
    .build())

model.set_cluster_weights({"criteria": 0.6, "Alternatives": 0.4})

block_alt_given_crit = {
    "C1": PairwiseComparison.from_judgments(["A", "B"], {("A", "B"): 4.0}),
    "C2": PairwiseComparison.from_judgments(["A", "B"], {("A", "B"): 3.0/7.0}),
}
model.add_block("Alternatives", "criteria", block_alt_given_crit)
model.add_block_uniform("criteria", "criteria")

priorities, labels = model.alternative_priorities()
print(dict(zip(labels, priorities)))
```

## Error Handling
SaatyPy provides detailed error messages for invalid inputs, missing weights, and matrix inconsistencies:
```python
from saatypy.ahp import AHPBuilder
from saatypy.components.errors import NormalizationError

model = AHPBuilder().add_criteria(["A", "B"]).add_alternatives(["X", "Y"]).build()
try:
    model.set_criteria_weights({"invalid": 1.0})
except NormalizationError as e:
    print("Error:", e)
```

## Reporting
Extract results directly from your model:
```python
report = model.to_report_data()
print(report["criteria_weights"])
print(report["global_priorities"])
print(report["ranking_str"])
```

## Saving Reports
You can save a formatted report for any model using the `ReportManager`:

```python
from saatypy.reporting.report import ReportManager

manager = ReportManager()  # Default: Markdown format, saves to 'reports/'
report_path = manager.save(model)  # model can be AHPModel or ANPModel
print(f"Report saved to: {report_path}")

# To use plain text format:
from saatypy.reporting.report import PlainRenderer
manager = ReportManager(renderer=PlainRenderer())
report_path = manager.save(model, path="my_report.txt")
```

- By default, reports are saved in Markdown format to the `reports/` directory.
- You can specify a custom path, file name, or renderer.
- The filename will include a timestamp unless you set `add_timestamp=False`.

## Advanced Usage
- Hierarchical criteria (AHP)
- Custom limiters (ANP)
- Extend with new adapters or reporting formats
- Use math utilities for normalization and consistency checks

## Documentation
- [AHP Guide](docs/ahp.md)
- [ANP Guide](docs/anp.md)
- [Usage Guide](docs/USAGE.md)

## References

- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.  
- Saaty, T. L. (1996). *Decision Making with Dependence and Feedback: The Analytic Network Process*. RWS Publications.  
- Saaty, T. L. (2008). *Decision making with the analytic hierarchy process*. International Journal of Services Sciences, 1(1), 83–98.  
- Saaty, T. L. (2005). *Theory and Applications of the Analytic Network Process*. RWS Publications.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
See [LICENSE](LICENSE).

## Changelog
See [CHANGELOG.md](CHANGELOG.md).

---
For more details, see the documentation in the `docs/` folder.
