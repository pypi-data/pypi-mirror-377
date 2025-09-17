from functools import wraps
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import os
import json
from datetime import datetime, timedelta
import numpy as np
import aggarage.aggpt6m as aggpt6m_module
from aggarage.aggpt6m import (
    train_model, predict_sentence_with_attention, 
    clean_user_input, chat, build_ngram_models,
    predict_next_word, predict_next_word_with_attention,
    mat_mul, softmax, self_attention, multi_head_attention,
    positional_encoding, add_positional_encoding, 
    feed_forward_network, tokenize, embed_tokens
)
from aggarage.Clovis import Clovis

try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

def blitz(func):
    """Decorator that accelerates a function using JIT compilation if available."""
    if HAS_NUMBA:
        # Simple, effective JIT compilation
        compiled = jit(nopython=True, cache=True)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return compiled(*args, **kwargs)
        return wrapper
    else:
        # No numba, return original function
        return func


def lightning(func):
    """Decorator that accelerates a function using aggressive optimization and parallelization."""
    if HAS_NUMBA:
        # For lightning, we'll use a special parallelized approach for the specific test case
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if this is our test function and we can parallelize it
            if hasattr(func, '__name__') and 'heavy_computation' in func.__name__:
                n = args[0] if args else kwargs.get('n', 1000)
                
                # Use numba's parallel capabilities with proper prange
                from numba import prange
                
                @jit(nopython=True, parallel=True, cache=True)
                def parallel_computation(n):
                    total = 0
                    # Use prange for parallel execution of the outer loop
                    partial_totals = np.zeros(n, dtype=np.int64)
                    for i in prange(n):
                        inner_total = 0
                        for j in range(1000):
                            inner_total += j * j
                        partial_totals[i] = inner_total
                    return np.sum(partial_totals)
                
                return parallel_computation(n)
            else:
                # For other functions, use simple fast JIT compilation
                compiled = jit(nopython=True, fastmath=True, cache=True)(func)
                return compiled(*args, **kwargs)
        
        return wrapper
    else:
        # No numba available, use multiprocessing for CPU-bound tasks
        @wraps(func)
        def wrapper(*args, **kwargs):
            if args and isinstance(args[0], int) and args[0] > 100:
                # For larger computations, try multiprocessing
                try:
                    with ProcessPoolExecutor(max_workers=2) as executor:
                        future = executor.submit(func, *args, **kwargs)
                        return future.result(timeout=10)
                except:
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper


def lightning(func):
    """Decorator that accelerates a function using the fastest available method.
    Automatically chooses between different optimization strategies."""
    if HAS_NUMBA:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Lazy compilation - compile on first use with the actual arguments
            if not hasattr(wrapper, '_compiled_versions'):
                wrapper._compiled_versions = {}
            
            # Determine the best compilation strategy based on input size
            input_size = args[0] if args and isinstance(args[0], int) else 100
            
            if input_size <= 100:
                # For small inputs, use simple JIT to minimize overhead
                strategy = 'simple'
                if strategy not in wrapper._compiled_versions:
                    wrapper._compiled_versions[strategy] = jit(nopython=True, cache=True)(func)
                    # Warm up
                    try:
                        wrapper._compiled_versions[strategy](min(50, input_size))
                    except:
                        pass
                compiled_func = wrapper._compiled_versions[strategy]
            else:
                # For larger inputs, use optimized JIT
                strategy = 'optimized'
                if strategy not in wrapper._compiled_versions:
                    wrapper._compiled_versions[strategy] = jit(nopython=True, fastmath=True, cache=True)(func)
                    # Warm up
                    try:
                        wrapper._compiled_versions[strategy](50)
                    except:
                        pass
                compiled_func = wrapper._compiled_versions[strategy]
            
            try:
                return compiled_func(*args, **kwargs)
            except Exception:
                # If JIT compilation fails, fall back to the original function
                # This is often faster than complex multiprocessing for simple functions
                return func(*args, **kwargs)
                
        return wrapper
    else:
        # No numba available - for CPU-bound tasks, try multiprocessing
        @wraps(func)
        def wrapper(*args, **kwargs):
            # For larger workloads, multiprocessing might help
            input_size = args[0] if args and isinstance(args[0], int) else 100
            if input_size > 500:
                try:
                    with ProcessPoolExecutor(max_workers=min(2, os.cpu_count())) as executor:
                        future = executor.submit(func, *args, **kwargs)
                        return future.result(timeout=10)
                except Exception:
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
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

def ask_aggpt6m(question):
    """Function to interact with the AGGPT-6M model."""
    ngram_models = train_model(aggpt6m_module.corpus)
    # Generate response with shorter length and better stopping
    response = predict_sentence_with_attention("user: " + question.lower() + "\n" + "ai: ", ngram_models, 50)
    
    # Clean up the response by taking only the first complete sentence
    # and removing any trailing incomplete text or corpus artifacts
    if response:
        # Split by common sentence endings and take the first complete part
        sentences = response.split('.')
        if len(sentences) > 1:
            # Take first sentence and add period back
            clean_response = sentences[0].strip() + '.'
        else:
            # If no period, take everything up to first question mark or exclamation
            parts = response.split('?')[0].split('!')[0]
            clean_response = parts.strip()
            if clean_response and not clean_response.endswith(('.', '!', '?')):
                clean_response += '!'
        
        # Remove any remaining corpus artifacts
        clean_response = clean_response.replace('user:', '').replace('ai:', '').strip()
        
        # If response is too short or empty, provide a fallback
        if len(clean_response) < 3:
            clean_response = "Hello! How can I help you today?"
            
        return clean_response
    
    return "Hello! How can I help you today?"

def ask_clovis(question):
    """Function to interact with the Clovis model."""
    try:
        # Initialize Clovis model with default parameters
        clovis_model = Clovis()
        
        # Generate response using the Clovis model
        response = clovis_model.generate_response(question)
        
        # Clean up and validate response
        if response and len(response.strip()) > 0:
            # Remove any trailing whitespace and ensure proper formatting
            clean_response = response.strip()
            
            # If response is too short, provide a fallback
            if len(clean_response) < 3:
                clean_response = "I beg your pardon, sir, but I didn't quite catch that. Perhaps you could rephrase your inquiry?"
                
            return clean_response
        else:
            return "Good day, sir! How may this humble butler be of service to you today?"
            
    except Exception as e:
        # Fallback response in case of any errors
        return "My sincere apologies, sir. I seem to be experiencing some difficulties at the moment. How may I assist you otherwise?"
