use malachite::random::EXAMPLE_SEED;
use malachite::Natural;
use malachite::natural::random;
use malachite::num::arithmetic::traits::{ModPow, Parity};
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
            if current < *limit {
                let prime = Self::next_prime(seed);
                if prime < *limit {
                    return prime;
                }
            }
            current >>= 1; // divide by two 
        }
    }
    

    pub fn next_prime(seed: &Natural) -> Natural {
        let mut current = if seed.even() { seed + Natural::ONE } else { seed.clone() };
        while !Self::is_prime(&current, 10) {
            current += &Natural::TWO;
        }
        current
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
        if n.even() {
            return false;
        }
        
        let n_minus_one = n - Natural::ONE;

        // Decompose n - 1 into 2^exponent * odd_component
        let mut odd_component = n_minus_one.clone();
        let mut exponent_of_two = 0;
        while odd_component.even() {
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
                if modular_exponentiation == n_minus_one {
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
    
}
