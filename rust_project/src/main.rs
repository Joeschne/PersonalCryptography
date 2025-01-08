mod hash_processor;
mod hash_config;
mod prime_generator;

use hash_processor::HashProcessor;
use hash_config::HashConfig;
use prime_generator::PrimeGenerator;

use malachite::Natural;

fn main() {
    let mut current = Natural::from(999999999999999999u128);
    loop {
        if PrimeGenerator::is_prime(&current, 10) {
            println!("Prime found: {}", current)
        }
        else {
            println!("Not prime: {}", current)
        }
        current += Natural::from(1u8);
    }
}
