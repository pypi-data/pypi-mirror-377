# Requisite Processor
The `RequisiteProcessor` class is designed to evaluate whether the prerequisite rules for a course are met given a list of completed courses and test score data.

## Prerequisite Data
This module can make use of any arbitrary prerequisite information given that it is formatted correctly. For more information on the necessary structure as well as the latest prerequsite data for UNM courses, see this repo:

https://lobogit.unm.edu/unm-data-analytics/requisite-data#

## Usage

### Initialization
Initialize the RequisiteProcessor with a dictionary of prerequisite rules.

```python
from requisite_processor.requisite_processor import RequisiteProcessor

prerequisite_rules = {
    "202310": {
        "MATH 1512": {
            "type": "course",
            "course": {"code": "MATH 1234"},
            "minimum_course_grade": "C"
        }
    }
}

processor = RequisiteProcessor(prerequisite_rules)
```

### Processor Methods
The RequisiteProcessor contains the following methods:
*availabile_academic_periods*:
Returns a list of all academic periods in the dataset.
```python
academic_periods = processor.availabile_academic_periods
print(academic_periods)  # Output: ['202310', '202380']
```

*latest_available_academic_period*:
Returns the most recent academic period.
```python
latest_period = processor.latest_available_academic_period
print(latest_period)  # Output: '202380'
```

*check_satisfaction*:
Checks if a student satisfies the prerequisites for a course in a specific academic period.

Parameters:

- course_code (str): Course to check prerequisites for.
- courses_taken (list[dict], optional): List of completed courses and grades. Defaults to [].
- test_scores (dict, optional): Test scores dictionary. Defaults to {}.
- academic_period (str, optional): Academic period. Defaults to the latest available.
- ignore_tests (bool, optional): Ignore test requirements. Defaults to False.
- ignore_grades (bool, optional): Ignore grade requirements. Defaults to False.

Returns:
RequisiteCheckResult object. The result of the prerequisite check.

See below for example usage.

### Example Prerequisite Satisfaction Check

```python
courses_taken = [{"code": "MATH 1250", "grade": "B"}]
test_scores = {"A01": 28}

result = processor.check_satisfaction(
    course_code="MATH 1512",
    courses_taken=courses_taken,
    test_scores=test_scores
)

print(result.satisfied)  # Output: True or False
```

## Future Work
- Write tests
- Allow for more customization in how requisites are processed.
- Write additional helper functions such as string representation of requirements, flattend requirements and more.