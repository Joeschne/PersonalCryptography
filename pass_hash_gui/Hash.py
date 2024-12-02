import tkinter as tk
from tkinter import messagebox
import itertools
from concurrent.futures import ProcessPoolExecutor

charset_full = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@%-.$="

# Helper function to perform multiplication in galois field(2^8)
def gf_mul(a, b):
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

def string_to_number_dynamic(card_info, base, min_length=991):
    # Ensure `card_info` is  string
    if not isinstance(card_info, str):
        card_info = str(card_info)

    # Initialize an empty dictionary to store character mappings
    char_to_num = {}

    # Generate the dictionary dynamically
    for i, char in enumerate(card_info):
        # Simple custom hash function for mapping
        mapped_value = (ord(char) * base + i ** 2) % 997  # Modulo to limit size
        char_to_num[char] = mapped_value

    # Use the dictionary to encode the string into  concatenated number
    raw_number = "".join(str(char_to_num[char]) for char in card_info)

    # Step 1: Scramble the raw number with  cascade modifier
    cascade = base
    scrambled = []
    for i, digit in enumerate(raw_number):
        # Cascade influences the scrambling to prevent repetition
        cascade = ((cascade ^ (ord(char) * (ord(card_info[i % len(card_info)]) + 1))) + int(digit) ** 2 + (cascade << 3)) % 10007
        scrambled_digit = (int(digit) + cascade + (i * base)) % 10
        scrambled.append(str(scrambled_digit))
    scrambled_number = "".join(scrambled)

    # Step 2: Pad to ensure minimum length with cascade influence
    while len(scrambled_number) < min_length:
        pad_digit = (len(scrambled_number) * base + cascade) % 10
        scrambled_number += str(pad_digit)
        cascade = (cascade * 13 + pad_digit) % 997  # Continue modifying the cascade

    # Step 3: Scale the number to spread out digits with cascade influence
    scaled_number = []
    for i, d in enumerate(scrambled_number):
        cascade = (gf_mul(cascade, int(d) + i) * cascade * 7 + int(d) + i) % 997  # Update cascade during scaling
        scaled_digit = (int(d) + cascade + base * i) % 10
        scaled_number.append(str(scaled_digit))

    # Ensure the result is still deterministic and of the desired length
    return int("".join(scaled_number))



def number_to_string(num, ascii_min=32, ascii_max=126):
    num = int(num)  # Ensure the input is an integer

    result = []
    ascii_range = ascii_max - ascii_min + 1

    # Initialize  dynamic scramble factor based on the input number
    scramble_factor = (num % ascii_range) + ascii_min
    cascade = 0  #  cascading variable to mix in previous iterations

    while num > 0:
        # Map  chunk of the number into the ASCII range
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




def generate_prime(seed: int, limit: int = 10**6) -> int:
    # Dynamically generate  prime number starting from the given seed
    seed = int(seed)
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    for num in range(seed + 50, limit):
        if is_prime(num):
            return num
    return 2  # Fallback (unlikely to happen with  reasonable seed/limit)


def calculate_primary_keys(card_info, card_number, base):
    # **Key 1 Calculation**
    # Step 1: Compute `key1mod` using both `card_info` and `card_number`
    key1mod = sum(
        ((ord(c) + i) * (base ** ((i + 1) % 7))) +
        (int(str(card_number)[i % len(str(card_number))]) if card_number else 0)
        for i, c in enumerate(card_info)
    ) % (base * 100)  # Scale to avoid clustering in  small range

    # Step 2: Generate  large prime for `key1mod`
    key1mod = generate_prime(key1mod + len(card_info) + card_number % 100)

    # Step 3: Calculate `key1` with scaling and enhanced mixing
    key1 = 1
    for i, c in enumerate(card_info):
        card_digit = int(str(card_number)[i % len(str(card_number))])
        key1 *= (ord(c) ^ card_digit) + (key1mod % (i + 3)) + (base ** ((i + 1) % 5))  # XOR + modular + scaling
    key1 = abs(key1) % (key1mod * 10) + base * 3  # Scale and offset the final result

    print(f"Key 1: {key1}")


    # **Key 2 Calculation**
    # Step 1: Compute `key2mod` using an aggressive mixing strategy
    key2mod = 1
    for i, c in enumerate(card_info):
        card_digit = int(str(card_number)[i % len(str(card_number))])
        # Mix ASCII value, digit, and position with cascading XOR and shifts
        key2mod ^= (((key2mod << 5) ^ ord(c)) + ((key2mod >> 3) ^ card_digit) + (base * (i + 1)))

    # Generate  large prime for `key2mod` to introduce unpredictability
    key2mod = generate_prime(abs(key2mod) + len(card_info) + sum(int(d) for d in str(card_number)))

    # Step 2: Calculate `key2` with cascading and position-based variability
    key2 = 0
    cascade = key2mod  # Start cascading from `key2mod`
    for i, digit in enumerate(str(card_number)):
        # Incorporate cascading value with shifts, base, and modular influences
        cascade = (cascade ^ (int(digit) * base ** (i % 4))) + ((cascade << 3) | (cascade >> 2))
        key2 += cascade

    # Normalize `key2` to  large, dynamic range
    key2 = abs(key2) % (key2mod * 100) + base * 7  # Scale and offset for larger variability

    print(f"Key 2: {key2}")



    # **Key 3 Calculation**
    # Step 1: Compute `key3mod`
    # - Uses  multiplicative hash to compute  base value
    # - Combines the ASCII value of each character with the previous result, modded to 32 bits
    key3mod = 1
    for c in card_info:
        key3mod = (key3mod * key2mod + ord(c)) & 0xFFFFFFFF  # Limit to 32-bit integer

    # - Generate  dynamic prime number for `key3mod`
    key3mod = generate_prime(key3mod % (10**5) + 1)

    # Step 2: Calculate `key3`
    # - Initialize `key3` to 0
    # - Use cyclic bit shifts for mixing: left-shift the ASCII value by `i % 16` bits
    # - Incorporate  right-shift for additional variability
    key3 = 0
    for i, c in enumerate(card_info):
        key3 ^= ((ord(c) << (i % 16)) | (ord(c) >> (16 - (i % 16)))) + key3mod % (i + 1)  # Cyclic shift + prime influence

    # - Take the modulus of the result with `key3mod` and offset by `base` for non-zero outputs
    key3 = (key3 % key3mod) + base

    # Debug output for Key 3
    print(f"Key 3: {key3}")

    # Return all three keys as the result
    return key1, key2, key3

def combine_keys_secure(key1, key2, key3):
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
    prime_mod = generate_prime(abs(key1 + key2 * key3 + cascade % (10 ** (total_length % 4 + 3))))
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


def split_number_by_key(card_number, key1, key2, key3, base):
    # Generate 16 ratios based on the keys
    ratios = []
    for i in range(16):
        ultra_key = combine_keys_secure(key1, key2, key3)
        ratios.append(ultra_key % 997 + i + base)

        # Dynamically update the keys for the next iteration
        key1 = (key1 ^ (ultra_key + i)) + (key2 << (i % 4))
        key2 = (key2 * ultra_key + (key3 >> (i % 3))) % (base * 100)
        key3 = (key3 + ultra_key) ^ (key1 * key2) % (base * 200)

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
        parts.append(number_string[start:start + length])
        start += length
    
    return parts


def process_part(part, base):
    part_string = number_to_string(part)
    part_number = string_to_number_dynamic(part_string, base)
    key1, key2, key3 = calculate_primary_keys(part_string, part_number, base)
    return charset_full[combine_keys_secure(key1, key2, key3) % len(charset_full)]


def multiprocessing_hash_input(card_info, base):
    card_number = string_to_number_dynamic(card_info, base)
    key1, key2, key3 = calculate_primary_keys(card_info, card_number, base)
    print(card_number)
    parts = split_number_by_key(card_number, key1, key2, key3, base)

    with ProcessPoolExecutor() as executor:
        # Distribute the work among processes and gather results
        results = executor.map(process_part, parts, itertools.repeat(base)) # create infinite iterable base with itertools
        # Aggregate results
        output = ''.join(results)
    return output


def hash_input(card_info, base):
    output = ""
    card_number = string_to_number_dynamic(card_info, base)
    key1, key2, key3 = calculate_primary_keys(card_info, card_number, base)
    print(card_number)
    parts = split_number_by_key(card_number, key1, key2, key3, base)

    for part in parts:
        part_string = number_to_string(part)
        part_number = string_to_number_dynamic(part_string, base)
        key1, key2, key3 = calculate_primary_keys(part_string, part_number, base)
        part_ultra_key = combine_keys_secure(key1, key2, key3)
        output += charset_full[part_ultra_key % len(charset_full)]
    return output

def hash(hash_key, input, base=2951):
    key_number = string_to_number_dynamic(hash_key, generate_prime(base))
    key1, key2, key3 = calculate_primary_keys(hash_key, key_number, generate_prime(base))
    key_base = combine_keys_secure(key1, key2, key3)
    output = hash_input(input, generate_prime(key_base))
    return (output)


class HashingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hashing Application")
        self.root.geometry("800x500")  # Set fixed size to avoid resizing
        self.root.configure(bg="#282c34")  # Updated background color

        # Title Label
        self.title_label = tk.Label(
            root, text="Cool Hashing Tool", bg="#282c34", fg="#ffffff", font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(pady=10)

        # Frame for Inputs
        self.input_frame = tk.Frame(root, bg="#282c34")
        self.input_frame.pack(pady=10)

        # Key Input
        self.key_label = tk.Label(self.input_frame, text="Key:", bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.key_label.grid(row=0, column=0, padx=5, pady=5)
        self.key_entry = tk.Entry(self.input_frame, width=40, bg="#e8e8e8", fg="#000000", font=("Helvetica", 12))
        self.key_entry.grid(row=0, column=1, padx=5, pady=5)

        # Input for Custom String
        self.custom_label = tk.Label(self.input_frame, text="Custom String:", bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.custom_label.grid(row=1, column=0, padx=5, pady=5)  
        self.custom_entry = tk.Entry(self.input_frame, width=40, bg="#e8e8e8", fg="#000000", font=("Helvetica", 12))
        self.custom_entry.grid(row=1, column=1, padx=5, pady=5)     


        # Output Box
        self.output_label = tk.Label(root, text="Output:", bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.output_label.pack(pady=10)
        self.output_text = tk.Text(root, height=8, width=60, bg="#282c34", fg="#ffffff", font=("Helvetica", 12))
        self.output_text.pack(pady=5)

        # Hash Button
        self.hash_button = tk.Button(
            root,
            text="Generate Hash",
            bg="#4caf50",
            fg="#ffffff",
            font=("Helvetica", 14, "bold"),
            activebackground="#45a049",
            command=self.generate_hash,
        )
        self.hash_button.pack(pady=10)

    def generate_hash(self):
        """Generate the hash based on the inputs."""
        key = self.key_entry.get()
        if not key:
            messagebox.showerror("Error", "Key is required!")
            return

        custom_string = self.custom_entry.get()
        if not custom_string:
            messagebox.showerror("Error", "Custom String is required!")
            return
        try:
            output = hash(key, custom_string)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Hash: {output}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating hash: {e}")



# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = HashingApp(root)
    root.mainloop()
