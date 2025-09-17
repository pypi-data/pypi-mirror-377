from . import *

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

    