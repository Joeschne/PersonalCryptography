use malachite::Natural;

fn main() {
    . . .
}

lazy_static::lazy_static! {
    static ref NATURAL_TWO: Natural = Natural::from(2u8);
    static ref TESTING_HASH_BASES: HashBases = HashBases::new(Natural::from(3333u32), Natural::from(2222u32));
    static ref TESTING_LIMIT: Natural = Natural::from(1115u16);
    static ref TESTING_CHARSET: String = String::from("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@%-.$=");
}

struct HashConfig {
    charset: String,
    use_additional_security: bool,
    hash_bases: HashBases,
    limit: Natural,
}

impl HashConfig {
    pub fn new(
        charset: String,
        use_additional_security: bool,
        hash_bases: HashBases,
        limit: Natural,
    ) -> Self {
        Self {
            charset,
            use_additional_security,
            hash_bases,
            limit
        }
    }

    pub fn preset_fast() -> Self {
        Self::new(TESTING_CHARSET.clone(), false, TESTING_HASH_BASES.clone(), TESTING_LIMIT.clone())
    }

    pub fn preset_secure() -> Self {
        Self::new(TESTING_CHARSET.clone(), false, TESTING_HASH_BASES.clone(), TESTING_LIMIT.clone())
    }

    pub fn preset_balanced() -> Self {
        Self::new(TESTING_CHARSET.clone(), false, TESTING_HASH_BASES.clone(), TESTING_LIMIT.clone())
    }
}

#[derive(Clone)]
pub struct HashBases {
    initial_base: Natural,
    base_cascade: Natural,
}

impl HashBases {
    fn new(
        initial_base: Natural,
        base_cascade: Natural
    ) -> Self {
        Self {
            initial_base,
            base_cascade
        }
    }
}

struct HashProcessor {
    hash_key: String,
    input_data: String,
    charset: String,
    use_additional_security: bool,
    hash_bases: HashBases,
    prime_generator: PrimeGenerator,
    cascade: Natural,
}

impl HashProcessor {
    pub fn new(
        hash_key: String,
        input_data: String,
        charset: String,
        use_additional_security: bool,
        hash_bases: HashBases,
        limit: Natural,
    ) -> Self {
        let prime_generator = PrimeGenerator::new(limit);
        let mut cascade = hash_bases.base_cascade.clone();
        Self {
            hash_key,
            input_data,
            charset,
            use_additional_security,
            hash_bases,
            prime_generator,
            cascade,
        }
    }
}


struct PrimeGenerator {
    limit: Natural,
}

impl PrimeGenerator {
    pub fn new(limit: Natural) -> Self {
        Self { limit }
    }

    pub fn next_prime(&self, seed: Natural, limit: Natural) -> Natural {
        let mut current = seed;
        loop {
            if current >= limit {
                current /= &*NATURAL_TWO;
            }
            let prime = Natural::from(5u8);
            if prime < limit {
                break prime;
            }
            current /= &*NATURAL_TWO;
        }
    }
}
