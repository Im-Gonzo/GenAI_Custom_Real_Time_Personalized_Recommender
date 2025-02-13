# Utilities

This directory contains utility functions used across the recommender system project.

## Files

- `data_utils.py`: General data manipulation utilities
- `split_utils.py`: Functions for splitting datasets (train/validation/test)
- `validation.py`: Data validation utilities

## Usage

Import utilities as needed:

```python
from recsys.utils.data_utils import check_required_columns
from recsys.utils.split_utils import train_validation_test_split
from recsys.utils.validation import validate_no_nulls
```