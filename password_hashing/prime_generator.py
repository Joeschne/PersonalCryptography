import random

class PrimeGenerator:
    @staticmethod
    def generate_prime(seed: int, limit: int = 10**16) -> int:
        """
        Generate a prime number starting from the given seed.
        """
        seed += 50
        # approximate numbers as int to make use of pythons arbitrary int precision in case of really high limits
        approx_log_of_seed = PrimeGenerator.approximate_ln(seed)
        extra_safety = approx_log_of_seed // 2
        while seed + (approx_log_of_seed * 4605 // 1000) + extra_safety > limit:
            seed //= 2

        if seed % 2 == 0:  # Ensure seed is odd
            seed += 1

        return PrimeGenerator._miller_rabin_test(seed, limit)

    @staticmethod
    def _miller_rabin_test(seed: int, limit: int) -> int:
        """
        Find the next highest prime number greater than a given floor
        and less than or equal to a specified ceiling using the Miller-Rabin test.

        Args:
            floor (int): The starting number for the search.
            ceiling (int): The upper limit for the search.

        Returns:
            int: The next prime number greater than floor and ≤ ceiling.
        Raises:
            ValueError: If no prime is found within the range.
        """
        def miller_rabin(n, k=10):  # Number of tests
            if n < 2:
                return False
            if n in (2, 3):
                return True
            if n % 2 == 0:
                return False

            # Decompose (n - 1) to d * 2^r
            r, d = 0, n - 1
            while d % 2 == 0:
                r += 1
                d //= 2

            # Witness loop
            for _ in range(k):
                a = random.randint(2, n - 2)
                x = pow(a, d, n)  # Compute a^d % n
                if x in (1, n - 1):
                    continue
                for _ in range(r - 1):
                    x = pow(x, 2, n)
                    if x == n - 1:
                        break
                else:
                    return False
            return True

        # Search for the next prime within the range
        candidate = seed
        while candidate <= limit:
            if miller_rabin(candidate):
                return candidate
            candidate += 2  # Skip even numbers

        raise ValueError(f"No prime found in the range [{seed}, {limit}]")

    @staticmethod
    def approximate_ln(n):
        ln2 = 693  # Approximation of 1000 * ln(2)
        log2 = PrimeGenerator.integer_log2(n)
        return (log2 * ln2) // 1000  # Scale back to approximate ln(n)

    @staticmethod
    def integer_log2(n):
        log = 0
        while n > 1:
            n >>= 1
            log += 1
        return log

