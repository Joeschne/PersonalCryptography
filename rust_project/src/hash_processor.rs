use crate::hash_config::HashConfig;
use crate::prime_generator::PrimeGenerator;

pub struct HashProcessor {
    pub hash_config: HashConfig,
}

impl HashProcessor {
    pub fn new(hash_config: HashConfig) -> Self {
        Self {
            hash_config,
        }
    }

    pub fn generate_hash(&self, hash_key: String, input_data: String) -> String {
        String::from("Implementation tbd")
    }
}
