mod hash_processor;
mod hash_config;
mod prime_generator;

use hash_processor::HashProcessor;
use hash_config::HashConfig;
use prime_generator::PrimeGenerator;

use malachite::{strings::ToDebugString, Natural};

fn is_fibonacci(n: u64) -> bool {
    // Helper function to check if a number is a perfect square
    fn is_perfect_square(x: u64) -> bool {
        let sqrt = (x as f64).sqrt() as u64;
        sqrt * sqrt == x
    }

    let test1 = 5 * n * n + 4;
    let test2 = 5 * n * n - 4;

    is_perfect_square(test1) || is_perfect_square(test2)
}

fn main() {
    let mut next = 0;
    let mut nth_prime = 0;
    loop {
        next += 1;
        // Check for overflow
        if PrimeGenerator::is_prime(&Natural::from(next), 10) && !is_fibonacci(next.clone()) {
            println!("{}, number {}", next, nth_prime);
            nth_prime += 1;
        }
    }
}
