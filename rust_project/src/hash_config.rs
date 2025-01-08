use malachite::Natural;
use lazy_static::lazy_static;

lazy_static! {
    pub static ref TESTING_HASH_BASES: HashBases = HashBases::new(Natural::from(3333u32), Natural::from(2222u32));
    pub static ref TESTING_LIMIT: Natural = Natural::from(1115u16);
    pub static ref TESTING_CHARSET: String = String::from("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@%-.$=");
}

pub struct HashConfig {
    pub charset: String,
    pub use_additional_security: bool,
    pub hash_bases: HashBases,
    pub limit: Natural,
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
            limit,
        }
    }

    pub fn preset_fast() -> Self {
        Self::new(TESTING_CHARSET.clone(), false, TESTING_HASH_BASES.clone(), TESTING_LIMIT.clone())
    }

    pub fn preset_secure() -> Self {
        Self::new(TESTING_CHARSET.clone(), true, TESTING_HASH_BASES.clone(), TESTING_LIMIT.clone())
    }

    pub fn preset_balanced() -> Self {
        Self::new(TESTING_CHARSET.clone(), false, TESTING_HASH_BASES.clone(), TESTING_LIMIT.clone())
    }
}

#[derive(Clone)]
pub struct HashBases {
    pub initial_base: Natural,
    pub base_cascade: Natural,
}

impl HashBases {
    pub fn new(initial_base: Natural, base_cascade: Natural) -> Self {
        Self {
            initial_base,
            base_cascade,
        }
    }
}
