from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import os
import json
from datetime import datetime, timedelta

try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

def blitz(func):
    """Decorator that accelerates a function using JIT compilation if available,
    or threads the execution as a fallback for CPU-only machines."""
    if HAS_NUMBA:
        compiled = jit(nopython=True, fastmath=True)(func)
    else:
        compiled = func

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return compiled(*args, **kwargs)
        except Exception:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(func, *args, **kwargs)
                return future.result()
    return wrapper

def fib(n):
    """Compute the nth Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

def factorial(n):
    """Compute the factorial of n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def is_prime(num):
    """Check if a number is prime."""
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def gcd(a, b):
    """Compute the greatest common divisor of a and b."""
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    """Compute the least common multiple of a and b."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)

def reverse_string(s):
    """Reverse a given string."""
    return s[::-1]

def is_palindrome(s):
    """Check if a string is a palindrome."""
    s = s.lower().replace(" ", "")
    return s == s[::-1]

def factorial_recursive(n):
    """Compute the factorial of n using recursion."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0 or n == 1:
        return 1
    return n * factorial_recursive(n - 1)

def sum_of_squares(n):
    """Compute the sum of squares of the first n natural numbers."""
    return sum(i * i for i in range(1, n + 1))

def printf(text, color="default"):
    """Print text in the terminal with the specified color."""
    colors = {
        "default": "\033[0m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }
    color_code = colors.get(color, colors["default"])
    reset_code = colors["default"]
    print(f"{color_code}{text}{reset_code}")

_temp_folder = ".timed_vars"
os.makedirs(_temp_folder, exist_ok=True)

def create_timed_variable(variable_name, variable_value):
    """Stores a variable with timestamp precision to a .tmp file for historical access."""
    file_path = os.path.join(_temp_folder, f"{variable_name}.tmp")
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    # Clear entries older than 30 minutes
    cutoff_time = now - timedelta(minutes=30)
    data = {timestamp: value for timestamp, value in data.items() 
            if datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") >= cutoff_time}
    
    data[now_str] = variable_value
    with open(file_path, "w") as f:
        json.dump(data, f)

def get_value_of_timed_variable(variable_name, time="default"):
    """Retrieves the value of a timed variable. 'time' can be 'default' (current) or a string like '-5s', '-5m'."""
    file_path = os.path.join(_temp_folder, f"{variable_name}.tmp")
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    if not data:
        return None
    
    if time == "default":
        latest_time = max(data.keys())
        return data[latest_time]
    else:
        try:
            # Parse time offset (e.g., "-5s", "-10m")
            if time.endswith("s"):
                offset_seconds = int(time[:-1])
                target_time = datetime.now() + timedelta(seconds=offset_seconds)
            elif time.endswith("m"):
                offset_minutes = int(time[:-1])
                target_time = datetime.now() + timedelta(minutes=offset_minutes)
            else:
                raise ValueError("Time format must be '-Xs' or '-Xm', e.g., '-5s' or '-10m'")
        except ValueError:
            raise ValueError("Time format must be '-Xs' or '-Xm', e.g., '-5s' or '-10m'")
        
        target_str = target_time.strftime("%Y-%m-%d %H:%M:%S")
        times = sorted(data.keys())
        previous_times = [t for t in times if t <= target_str]
        
        if not previous_times:
            # no recorded value before target time, return earliest value
            return data[times[0]]
        
        closest_time = max(previous_times)
        return data[closest_time]

def clear_all_timed_variables():
    """Deletes all .tmp files created by the timed variable system."""
    for f in os.listdir(_temp_folder):
        if f.endswith(".tmp"):
            os.remove(os.path.join(_temp_folder, f))
    os.rmdir(_temp_folder)


if __name__ == "__main__":
    # Example usages
    print("Fibonacci of 10:", fib(10))
    print("Factorial of 5:", factorial(5))
    print("Is 29 prime?", is_prime(29))
    print("GCD of 48 and 18:", gcd(48, 18))
    print("LCM of 4 and 5:", lcm(4, 5))
    print("Reverse of 'hello':", reverse_string("hello"))
    print("Is 'racecar' a palindrome?", is_palindrome("racecar"))
    print("Factorial of 6 (recursive):", factorial_recursive(6))
    print("Sum of squares of first 5 natural numbers:", sum_of_squares(5))
    printf("This is a red text", color="red")
    printf("This is a green text", color="green")
    printf("This is a default text")
    
    # Timed variables example
    create_timed_variable("test_var", 42)
    print("Current value of 'test_var':", get_value_of_timed_variable("test_var"))
    
    # Simulate creating values at different times
    import time
    time.sleep(2)  # Wait 2 seconds
    create_timed_variable("test_var", 84)
    print("Current value of 'test_var':", get_value_of_timed_variable("test_var"))
    print("Value of 'test_var' 2 seconds ago:", get_value_of_timed_variable("test_var", "-2s"))
    print("Value of 'test_var' 1 minute ago:", get_value_of_timed_variable("test_var", "-1m"))
    
    clear_all_timed_variables()

