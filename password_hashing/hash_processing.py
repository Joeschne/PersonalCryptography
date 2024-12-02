import itertools
from concurrent.futures import ProcessPoolExecutor
from prime_generator import PrimeGenerator

class HashProcessor:

    @staticmethod
    # Helper function to perform multiplication in galois field(2^8)
    def _galois_field_mul(a: int, b: int) -> int:
        # The irreducible polynomial for GF(2^8) is x^8 + x^4 + x^3 + x + 1, represented as 0x11b in hexadecimal, 283 in decimal
        mod = 0x11b

        # Initialize the result to 0. This will accumulate the product of a and b.
        result = 0

        # Iterate while there are bits remaining in b (b > 0).
        while b:
            # If the least significant bit of b is 1, add the current value of a to the result.
            # In GF(2), addition is performed as XOR.
            if b & 1:
                result ^= a  # Add (XOR) the current value of 'a' to 'result'

            # Left shift 'a' to effectively multiply it by x (i.e., move to the next higher degree term).
            a <<= 1

            # If the left shift causes 'a' to exceed 8 bits (a & 0x100 is true),
            if a & 0x100:  # Overflow occurs when the 9th bit of 'a' is set. 0x100 == 1'0000'0000 == 256
                a ^= mod  # Reduce 'a' modulo the Rijndael polynomial

            # Right shift 'b' to process the next bit. This simulates traditional binary multiplication,
            # where we move to the next bit of the multiplier (b).
            b >>= 1

        # Return the final result, which is the product of 'a' and 'b' reduced modulo the Rijndael polynomial.
        return result

    @staticmethod
    def _string_to_number_dynamic(input_string: str, base: int, min_length: int = 991) -> int:
        # Initialize an empty dictionary to store character mappings
        char_to_num = {}

        # Generate the dictionary dynamically
        for i, char in enumerate(input_string):
            # Simple custom hash function for mapping
            mapped_value = (ord(char) * base + i ** 2) % 997  # Modulo to limit size
            char_to_num[char] = mapped_value

        # Use the dictionary to encode the string into  concatenated number
        raw_number = "".join(str(char_to_num[char]) for char in input_string)

        # Step 1: Scramble the raw number with  cascade modifier
        cascade = base
        scrambled = []
        for i, digit in enumerate(raw_number):
            # Cascade influences the scrambling to prevent repetition
            cascade = ((cascade ^ (ord(char) * (ord(input_string[i % len(input_string)]) + 1))) + int(digit) ** 2 + (cascade << 3)) % 10007
            scrambled_digit = (int(digit) + cascade + (i * base)) % 10
            scrambled.append(str(scrambled_digit))
        scrambled_number = "".join(scrambled)

        # Step 2: Pad to ensure minimum length with cascade influence
        while len(scrambled_number) < min_length:
            pad_digit = (len(scrambled_number) * base + cascade) % 10
            scrambled_number += str(pad_digit)
            cascade = (cascade * 13 + pad_digit) % 1003  # Continue modifying the cascade

        # Step 3: Scale the number to spread out digits with cascade influence
        scaled_number = []
        for i, d in enumerate(scrambled_number):
            cascade = (HashProcessor._galois_field_mul(cascade, int(d) + i) * cascade * 7 + int(d) + i) % 971  # Update cascade during scaling
            scaled_digit = (int(d) + cascade + base * i) % 10
            scaled_number.append(str(scaled_digit))

        # Ensure the result is still deterministic and of the desired length
        return int("".join(scaled_number))


    @staticmethod
    def _number_to_string(num: int, ascii_min: int =32, ascii_max: int = 126) -> str:
        result = []
        ascii_range = ascii_max - ascii_min + 1

        # Initialize  dynamic scramble factor based on the input number
        scramble_factor = (num % ascii_range) + ascii_min
        cascade = 0  #  cascading variable to mix in previous iterations

        while num > 0:
            # Map a chunk of the number into the ASCII range
            ascii_val = (num % ascii_range) + ascii_min

            # Apply enhanced dynamic scrambling
            scrambled_val = (
                ((ascii_val + scramble_factor + cascade) ^ (num % 251))
                % ascii_range
            ) + ascii_min
            result.append(chr(scrambled_val))

            # Update the number for the next iteration
            num //= ascii_range

            # Dynamically adjust the scramble factor based on the remaining number and current state
            scramble_factor = (((scramble_factor * 7 + num % 17 + ascii_val) ^ cascade) % ascii_range)
            # Cascade evolves based on the scramble factor, current value, and previous state
            cascade = (cascade * scramble_factor + scrambled_val * 17 + num % 23) % ascii_range

        # Reverse the result to restore the proper order
        return ''.join(reversed(result))

    @staticmethod
    def _calculate_three_primary_keys(hash_input: str, hash_input_number: int, base: int) -> tuple[int, int, int]:
        # **Key 1 Calculation**
        # Step 1: Compute `key1mod` using both `card_info` and `card_number`
        key1mod = sum(
            ((ord(c) + i) * (base ** ((i + 1) % 7))) +
            (int(str(hash_input_number)[i % len(str(hash_input_number))]) if hash_input_number else 0)
            for i, c in enumerate(hash_input)
        ) % (base * 103)  # Scale to avoid clustering in  small range

        # Step 2: Generate  large prime for `key1mod`
        key1mod = PrimeGenerator.generate_prime(key1mod + len(hash_input) + hash_input_number % 107)

        # Step 3: Calculate `key1` with scaling and enhanced mixing
        key1 = 1
        for i, c in enumerate(hash_input):
            card_digit = int(str(hash_input_number)[i % len(str(hash_input_number))])
            key1 *= (ord(c) ^ card_digit) + (key1mod % (i + 3)) + (base ** ((i + 1) % 5))  # XOR + modular + scaling
        key1 = abs(key1) % (key1mod * 10) + base * 3  # Scale and offset the final result

        print(f"Key 1: {key1}")


        # **Key 2 Calculation**
        # Step 1: Compute `key2mod` using an aggressive mixing strategy
        key2mod = 1
        for i, c in enumerate(hash_input):
            card_digit = int(str(hash_input_number)[i % len(str(hash_input_number))])
            # Mix ASCII value, digit, and position with cascading XOR and shifts
            key2mod ^= (((key2mod << 5) ^ ord(c)) + ((key2mod >> 3) ^ card_digit) + (base * (i + 1)))

        # Generate  large prime for `key2mod` to introduce unpredictability
        key2mod = PrimeGenerator.generate_prime(abs(key2mod) + len(hash_input) + sum(int(d) for d in str(hash_input_number)))

        # Step 2: Calculate `key2` with cascading and position-based variability
        key2 = 0
        cascade = key2mod  # Start cascading from `key2mod`
        for i, digit in enumerate(str(hash_input_number)):
            # Incorporate cascading value with shifts, base, and modular influences
            cascade = (cascade ^ (int(digit) * base ** (i % 4))) + ((cascade << 3) | (cascade >> 2))
            key2 += cascade

        # Normalize `key2` to  large, dynamic range
        key2 = abs(key2) % (key2mod * 97) + base * 7  # Scale and offset for larger variability

        print(f"Key 2: {key2}")

        # **Key 3 Calculation**
        # Step 1: Compute `key3mod`
        # - Uses  multiplicative hash to compute  base value
        # - Combines the ASCII value of each character with the previous result, modded to 32 bits
        key3mod = 1
        for c in hash_input:
            key3mod = (key3mod * key2mod + ord(c)) & 0xFFFFFFFF  # Limit to 32-bit integer

        # - Generate  dynamic prime number for `key3mod`
        key3mod = PrimeGenerator.generate_prime(key3mod % (10**5) + 1)

        # Step 2: Calculate `key3`
        # - Initialize `key3` to 0
        # - Use cyclic bit shifts for mixing: left-shift the ASCII value by `i % 16` bits
        # - Incorporate  right-shift for additional variability
        key3 = 0
        for i, c in enumerate(hash_input):
            key3 ^= ((ord(c) << (i % 16)) | (ord(c) >> (16 - (i % 16)))) + key3mod % (i + 1)  # Cyclic shift + prime influence

        # - Take the modulus of the result with `key3mod` and offset by `base` for non-zero outputs
        key3 = (key3 % key3mod) + base

        # Debug output for Key 3
        print(f"Key 3: {key3}")

        # Return all three keys as the result
        return key1, key2, key3

    @staticmethod
    def _combine_keys_secure(key1: int, key2: int, key3: int) -> int:
        # Step 1: Dynamically adjust the base and modulus based on key lengths
        key1_len = len(str(key1))
        key2_len = len(str(key2))
        key3_len = len(str(key3))
        total_length = key1_len + key2_len + key3_len

        # Base depends on total length, ensuring variability
        base = 31 + (total_length % 19)  # Add  dynamic component to base

        # Step 2: Initial cascading hash
        combined = (key1 * base + key2) ^ key3  # Combine keys with multiplication and XOR
        cascade = combined

        # Step 3: Mixing through cascading and bitwise shifts
        for i in range(key2 % 617):  
            shift_amount = (total_length + i) % 29 + 1  # Vary shift amount dynamically
            cascade = ((cascade << shift_amount) | (cascade >> (64 - shift_amount))) ^ (
                key1 + key2 * key3
            )  # Left shift + XOR
            cascade = ((cascade * base) + key3) ^ (key2 << 3)  # Modular influence

        # Step 4: Normalize and fold into  large number
        # Generate  dynamic modulus with  controlled lower bound
        prime_mod = PrimeGenerator.generate_prime(abs(key1 + key2 * key3 + cascade % (10 ** (total_length % 4 + 3))))
        result = (cascade ^ (key1 * key2 + key3)) % prime_mod

        # Step 5: Final entropy spreading with bit interleaving
        interleaved = 0
        for i in range(total_length):  # Interleave bits for the length of all keys combined
            bit = (
                (result >> i & 1)
                ^ (key1 >> i & 1)
                ^ (key2 >> i & 1)
                ^ (key3 >> i & 1)
            )
            interleaved |= (bit << i)

        # Step 6: Final scaling and dynamic modulus with  larger range
        final_result = abs(interleaved + result) % max(prime_mod * base, 10 ** 6)
        print(f"Ultra key: {final_result}")
        return final_result

    @staticmethod
    def _split_number_by_key(card_number: int, key1: int, key2: int, key3: int, base: int) -> list[int]:
        # Generate 16 ratios based on the keys
        ratios = []
        for i in range(16):
            ultra_key = HashProcessor._combine_keys_secure(key1, key2, key3)
            ratios.append(ultra_key % 997 + i + base)

            # Dynamically update the keys for the next iteration
            key1 = (key1 ^ (ultra_key + i)) + (key2 << (i % 4))
            key2 = (key2 * ultra_key + (key3 >> (i % 3))) % (base * 101)
            key3 = (key3 + ultra_key) ^ (key1 * key2) % (base * 199)

            # Optional: Add dynamic scaling or modular arithmetic
            key1 = abs(key1) % (10**6)  # Keep the key within  reasonable range
            key2 = abs(key2) % (10**6)
            key3 = abs(key3) % (10**6)
        
        # Normalize the ratios to calculate segment lengths
        total_ratios = sum(ratios)
        number_string = str(card_number)
        number_length = len(number_string)
        split_lengths = [number_length * ratio // total_ratios for ratio in ratios]

        # Adjust for any remainder in the split
        split_lengths[-1] += number_length - sum(split_lengths)

        # Split the card_number into parts
        parts = []
        start = 0
        for length in split_lengths:
            parts.append(int(number_string[start:start + length]))
            start += length
        
        return parts

    @staticmethod
    def _process_part(part: int, base: int, charset: str) -> str:
        part_string = HashProcessor._number_to_string(part)
        part_number = HashProcessor._string_to_number_dynamic(part_string, base)
        key1, key2, key3 = HashProcessor._calculate_three_primary_keys(part_string, part_number, base)
        part_ultra_key = HashProcessor._combine_keys_secure(key1, key2, key3)
        return charset[part_ultra_key % len(charset)]

    @staticmethod
    def _multiprocessing_create_final_hash(parts: list[int], base: int, charset: str) -> str:
        with ProcessPoolExecutor() as executor:
            # Distribute the work among processes and gather results
            results = executor.map(HashProcessor._process_part, parts, itertools.repeat(base), itertools.repeat(charset)) # create infinite iterable base with itertools
            # Aggregate results
            output = ''.join(results)
        return output

    @staticmethod
    def _create_final_hash(parts: list[str], base: int, charset: str, use_additional_security: bool):
        output = ""

        for part in parts:
            part_string = HashProcessor._number_to_string(part)
            part_number = HashProcessor._string_to_number_dynamic(part_string, base)
            key1, key2, key3 = HashProcessor._calculate_three_primary_keys(part_string, part_number, base)
            part_ultra_key = HashProcessor._combine_keys_secure(key1, key2, key3)
            output += charset[part_ultra_key % len(charset)]
            if use_additional_security:
                base = PrimeGenerator.generate_prime(part_ultra_key)
        return output

    @staticmethod
    def hash_input_data(
        hash_key: str,
        input_data: str,
        initial_base: int = 2951,
        use_additional_security: bool = True,
        use_multiprocessing: bool = False,
        charset: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@%-.$="
    ) -> str:
        # Step 1: Generate the base primes and keys for hashing
        ultra_key_base_prime = HashProcessor._generate_ultra_key_base_prime(hash_key, initial_base)

        # Step 2: Process the input data into numeric form
        parts = HashProcessor._process_input_data(input_data, ultra_key_base_prime)

        # Step 3: Generate the final hash using the selected method
        if use_multiprocessing:
            return HashProcessor._multiprocessing_create_final_hash(parts, ultra_key_base_prime, charset)
        else:
            return HashProcessor._create_final_hash(parts, ultra_key_base_prime, charset, use_additional_security)


    @staticmethod
    def _generate_ultra_key_base_prime(hash_key: str, initial_base: int) -> int:
        """Generates the ultra key base prime for hashing."""
        initial_base_prime = PrimeGenerator.generate_prime(initial_base)
        key_number = HashProcessor._string_to_number_dynamic(hash_key, initial_base_prime)
        key1, key2, key3 = HashProcessor._calculate_three_primary_keys(hash_key, key_number, initial_base_prime)
        ultra_key_base = HashProcessor._combine_keys_secure(key1, key2, key3)
        return PrimeGenerator.generate_prime(ultra_key_base)

    @staticmethod
    def _process_input_data(input_data: str, ultra_key_base_prime: int):
        """Processes the input data into numeric form and splits it into parts."""
        input_data_number = HashProcessor._string_to_number_dynamic(input_data, ultra_key_base_prime)
        key1, key2, key3 = HashProcessor._calculate_three_primary_keys(input_data, input_data_number, ultra_key_base_prime)
        parts = HashProcessor._split_number_by_key(input_data_number, key1, key2, key3, ultra_key_base_prime)
        return parts

    
