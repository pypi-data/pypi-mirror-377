# AgGarage

An open-source python package with multiple python tools.

## Installation

```bash
pip install aggarage
```

## Usage

```python
from aggarage import *

@blitz # Example of a decorator from the package, it optimizes heavy calculations
def heavy_calc(x):
    total = 0
    for i in range(x):
        total += i ** 2
    return total

print(heavy_calc(10_000_000))

```

## Timed Variables

AgGarage allows you to store variables over time and retrieve past values.

```python
from aggarage import create_timed_variable, get_value_of_timed_variable, clear_all_timed_variables

create_timed_variable("score", 100)
create_timed_variable("score", 200)

print(get_value_of_timed_variable("score"))       # latest value
print(get_value_of_timed_variable("score", "-1m")) # value 1 minute ago

clear_all_timed_variables()  # removes all timed variable data

```

## Utilities

AgGarage also provides common utility functions:

`fib(n)` – Fibonacci number
`factorial(n)` / `factorial_recursive(n)` – Factorial
`is_prime(num)` – Prime check
`gcd(a, b)` / `lcm(a, b)` – Greatest/common divisors
`reverse_string(s)` / `is_palindrome(s)` – String utilities
`sum_of_squares(n)` – Sum of squares
`printf(text, color="red")` – Colored terminal output

## Notes

Timed variables are stored with second-level precision and automatically prune entries older than 30 minutes.
The `@blitz` decorator uses JIT compilation if available or threads as a fallback to speed up computations.

