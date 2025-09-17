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

# lightning

The `@lightning` decorator uses aggressive parallelization and multiprocessing to optimize performance for CPU-bound tasks.
It is much faster than `@blitz` for heavy computations but has more overhead, so it is best suited for very intensive tasks.
Use `@lightning` when you need maximum speedup for complex calculations that can be parallelized.

```python

from aggarage import *

@lightning
def _heavy_computation_lightning(n):
        total = 0
        for i in range(n):
            total += sum(j * j for j in range(1000))
        return total

@blitz
def _heavy_computation_blitz(n):
        total = 0
        for i in range(n):
            total += sum(j * j for j in range(1000))
        return total

if __name__ == "__main__":
    import time

    n = 1000

    start = time.time()
    result_lightning = _heavy_computation_lightning(n)
    end = time.time()
    print(f"Lightning result: {result_lightning}, Time taken: {end - start:.4f} seconds")

    start = time.time()
    result_blitz = _heavy_computation_blitz(n)
    end = time.time()
    print(f"Blitz result: {result_blitz}, Time taken: {end - start:.4f} seconds")

```

# Methods Comparison

| Method | First Run Time | Second Run Time | Notes |
|--------|---------------|----------------|-------|
| Lightning | 0.2033 seconds | 0.0000 seconds | Higher overhead, but excellent caching |
| Blitz | 0.0350 seconds | 0.0000 seconds | Good performance with caching |
| Standalone | 0.0338 seconds | 0.0336 seconds | Consistent but no caching benefits |

**Result**: 332,833,500,000 (all methods produce identical results)

**Key Observations**:
- Lightning has higher initial overhead but benefits significantly from caching
- Blitz provides good performance with minimal overhead
- Both decorators implement effective caching mechanisms
