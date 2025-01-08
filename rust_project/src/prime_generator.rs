use malachite::random::EXAMPLE_SEED;
use malachite::Natural;
use malachite::natural::random;
use malachite::num::arithmetic::traits::ModPow;
use malachite::num::basic::traits::{One, Two};
use lazy_static::lazy_static;

lazy_static! {
    pub static ref NATURAL_THREE: Natural = Natural::from(3u8);
}

pub struct PrimeGenerator {

}

impl PrimeGenerator {   
    pub fn next_limited_prime(seed: &Natural, limit: &Natural) -> Natural {
        let mut current = seed.clone();
        loop {
            if current >= *limit {
                break;
            }
            current >>= 1; // divide by two
        }
        loop {
            let prime =Self::next_prime(seed);
            if prime < *limit {
                break prime;
            }
            current >>= 1;
        }
    }
    

    pub fn next_prime(seed: &Natural) -> Natural {
        let mut current = seed.clone();
        if Self::is_even(seed) {
            current += &Natural::ONE;
        }
        loop {
            if Self::is_prime(&current, 10) {
                break current;
            } 
            else {
                current += &Natural::from(2u8);
            }
        }
    }
    

    /// Miller-Rabin Primality Test
    /// `n`: The number to test for primality.
    /// `iterations`: Number of random bases to test with (more increases confidence).
    pub fn is_prime(n: &Natural, iterations: u32) -> bool {
        // Handle trivial cases
        if *n <= Natural::ONE {
            return false;
        }
        if *n <= *NATURAL_THREE {
            return true;
        }
        if Self::is_even(n) {
            return false;
        }

        // Decompose n - 1 into 2^exponent * odd_component
        let mut odd_component = n - Natural::ONE;
        let mut exponent_of_two = 0;
        while Self::is_even(&odd_component) {
            odd_component /= Natural::TWO;
            exponent_of_two += 1;
        }

        let mut random_bases = random::uniform_random_natural_range(EXAMPLE_SEED, Natural::TWO, n - Natural::TWO);

        // Perform the Miller-Rabin test for a number of iterations
        for _ in 0..iterations {
            // Choose a random base between 2 and n - 2
            let random_base = random_bases.next().unwrap();
            
            // Compute random_base^odd_component mod n
            let mut modular_exponentiation = random_base.mod_pow(odd_component.clone(), n);

            // Check if modular_exponentiation is 1 or n - 1
            if modular_exponentiation == Natural::ONE || modular_exponentiation == n - Natural::ONE {
                continue;
            }

            // Square modular_exponentiation up to exponent_of_two - 1 times
            let mut is_composite = true;
            for _ in 0..(exponent_of_two - 1) {
                modular_exponentiation = modular_exponentiation.mod_pow(Natural::TWO, n);
                if modular_exponentiation == n - Natural::ONE {
                    is_composite = false;
                    break;
                }
            }

            // If no condition for primality is met, return false (composite)
            if is_composite {
                return false;
            }
        }
        // If all iterations pass, n is probably prime
        true
    }

    fn is_even(n: &Natural) -> bool {
        if n & Natural::ONE == 0u8 {
            return true;
        }
        false
    }

}
