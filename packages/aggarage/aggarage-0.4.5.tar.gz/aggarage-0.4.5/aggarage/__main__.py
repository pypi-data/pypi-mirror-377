# __main__.py for aggarage package
# This file allows running `python -m aggarage`

from . import *

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
    
    clear_all_timed_variables()

    print("AGGPT-6M response to 'Hello, how are you?':", ask_aggpt6m("Hello, how are you?"))
    print("Clovis response to 'Good morning!':", ask_clovis("Good morning!"))
