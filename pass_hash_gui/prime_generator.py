import math

class PrimeGenerator:
    @staticmethod
    def _is_prime(n: int) -> bool:
        """Check if a number is prime using 6k ± 1 optimization."""
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    @staticmethod
    def generate_prime(seed: int, limit: int = 10**10) -> int:
        """
        Generate a prime number starting from the given seed.
        Uses 6k ± 1 optimization for primality testing.
        """
        seed += 50
        log_of_seed = math.log(seed)
        extra_safety = log_of_seed / 2
        while seed + (log_of_seed * 4.605) + extra_safety > limit:
            seed -= seed // 2

        if seed % 2 == 0:  # Ensure seed is odd
            seed += 1

        for num in range(seed, limit, 2):  # Skip even numbers
            if PrimeGenerator._is_prime(num):
                return num

        raise ValueError(f"No prime found in range starting from {seed} up to {limit}.")