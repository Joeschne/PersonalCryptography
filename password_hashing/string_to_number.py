from math import ceil
from helper import Helperly
import time

# Basically SHA but not really
class StringToNumber:
    
    # Fractional part of 17th root of first 8 fibonacci primes
    IVS = [
        0x0aa758ccbbf77d97,
        0x11170f59d3fedfef,
        0x196baae1e081144c,
        0x29b0f4a53216f576,
        0x4d5b77ccd312fd89,
        0x60c610fb40f0d298,
        0x8b10e608b036b8f0,
        0xd432d02eaa478c24
    ]

    # Fractional part of 17th root of first 80 non-fibonacci primes
    WORDS = [
        0x1F0BCBA784A8473F, 0x26C7BD6242D7C312, 0x2E6D16ED9416A182, 0x30694AC12EB7041B,
        0x33DA0B2C89B1BD4D, 0x3814024DE7773E96, 0x394E0AEDC0402380, 0x3C952949E5898434,
        0x3E80080A18E67357, 0x3F64C9809C5BF6A0, 0x4111B7E924F1A39A, 0x4358AA230169435A,
        0x4564844FBD59C392, 0x460806CDFD8FDFFE, 0x47D5EAC46E1982A7, 0x48F4ADAD9F0B842A,
        0x497E66F5FFDE7585, 0x4B073CE6C0EF3324, 0x4BFDD04E5D76D05F, 0x4F0CA7D1E1432D5C,
        0x4FD8C849D3B10CE6, 0x503C02341AAB2AC0, 0x50FD22BC7923ED2F, 0x515B2A280DE32176,
        0x521272CF0EBFBBCF, 0x54671DFC0AB8B400, 0x55063903763818B1, 0x55EC823BEF044FFF,
        0x56372A24A1C3B957, 0x579DE9DA2890B566, 0x57E2EF37C076553C, 0x58ACF3BFB2CA697B,
        0x596FD48699A7699D, 0x59EE08460B26D894, 0x5AA61995C95C9C59, 0x5B5841288DFBC84C,
        0x5B926455C42A4841, 0x5CAC4DF2F763AD44, 0x5CE303FB958BFB5B, 0x5D4EDAEACF8B3646,
        0x5D8401200E813816, 0x5EB8B81360D5B90F, 0x5FDD54CDFBF09451, 0x603B94DFC3F2A137,
        0x606A1F3BEA3D1EB6, 0x614D3C0D9682D5EE, 0x617994E42E3E689F, 0x62523FC5DAF964D3,
        0x62D061C081FFDFD1, 0x634BC5DE7F196BD5, 0x63C48AE16B7130C3, 0x63EC3C70F8E3C511,
        0x6461AF0FAD0795A9, 0x64AEA8CBBAD72310, 0x64D4C2DD67920601, 0x658F8C8B5D1A06B6,
        0x668B36C8C94FF3BC, 0x66D122806B833A18, 0x66F3C741FA5DCA03, 0x673871E4F0F00C30,
        0x68228513343DF609, 0x6883FF2F9C3393CC, 0x6922E2BDE4155D49, 0x694225465DF1A63B,
        0x698029AD512A8F5A, 0x69DBF5A028311378, 0x6A54225B924961F8, 0x6AACA8719A95854E,
        0x6B03D9FF904AD14F, 0x6B3D43000D276C39, 0x6B9253DA34939DA0, 0x6C01D904E6EDBE18,
        0x6C38D125D99B8891, 0x6CA5396B859308B1, 0x6D29F606AAA4E832, 0x6D4426722E12763F,
        0x6DC55D527E0EB3DC, 0x6DDEDE51694D8223, 0x6E2AB861902A9AE9, 0x6E5CBF7770CA318E
    ]

    @staticmethod
    def hash_string(message: str) -> int:
        blocks = StringToNumber._preprocess_message(message)
        
        state = StringToNumber.IVS
        for block in blocks:
            words = [
                int.from_bytes(block[i:i + 8], 'big')
                for i in range(0, len(block), 8)
            ]
            full_words = StringToNumber._expand_schedule(words)
            state = StringToNumber._compress(state, full_words, StringToNumber.WORDS)

        assert len(state) == 8, "State must contain exactly 8 integers."
        for num in state:
            assert 0 <= num < 2**64, f"Number {num} is not a 64-bit integer."

        # Concatenate all integers into a single 512-bit integer
        concatenated = 0
        for num in state:
            concatenated = (concatenated << 64) | num  # Shift left and append
        return concatenated

    @staticmethod
    def _preprocess_message(message: str, block_size: int = 128) -> list[bytes]:
        message_bytes = message.encode('utf-8') #byte conversion

        message_length = len(message_bytes) * 8 # Append message length to disable extension attacks
        length_bytes = message_length.to_bytes(16)  
        message_bytes += length_bytes

        total_length = ceil(len(message_bytes) / block_size) * block_size

        padded_message = StringToNumber._fibonacci_xor_pad(message_bytes, total_length)

        # Split the padded message into 1024-bit (128-byte) blocks
        blocks = [padded_message[i:i + block_size] for i in range(0, len(padded_message), block_size)]

        return blocks

    @staticmethod
    def _expand_schedule(initial_words: list[int]):
        W = initial_words[:]
        
        for t in range(16, 80):
            new_word = (
                StringToNumber.wave(W[t-16]) +
                StringToNumber.draft(W[t-15]) +
                StringToNumber.breeze(W[t-7]) +
                StringToNumber.ripple(W[t-2])
            ) & 0xFFFFFFFFFFFFFFFF  # Efficient modulo
            print(hex(new_word))
            W.append(new_word)
        
        return W

    @staticmethod
    def _compress(state: list[int], schedule: list[int], constants: list[int]) -> list[int]:
        
        assert len(state) == 8, "State must have 8 variables."
        assert len(schedule) == 80, "Schedule must have 80 words."
        assert len(constants) == 80, "Constants must have 80 words."
        
        initial_state = state

        # Compression rounds
        for t in range(80):
            T1 = (
                StringToNumber.torrent(state[3]) +
                StringToNumber.crosscurrent(state[0], state[1], state[2]) +
                schedule[t] +
                constants[t]
            ) & 0xFFFFFFFFFFFFFFFF  
            T2 = (
                StringToNumber.cyclone(state[4]) +
                StringToNumber.confluence(state[5], state[6], state[7])
            ) & 0xFFFFFFFFFFFFFFFF
            
            state [3] = state [3] + T1 & 0xFFFFFFFFFFFFFFFF

            state = [(T1 + T2) & 0xFFFFFFFFFFFFFFFF] + state[:-1]
        
        for t in range(len(state)):
            state[t] = state[t] + initial_state[t] & 0xFFFFFFFFFFFFFFFF
        return state

    @staticmethod
    def _fibonacci_xor_pad(message: bytes, target_length: int) -> bytes:
        # If the message is already long enough, truncate it
        if len(message) >= target_length:
            return message[:target_length]

        # Start with a mutable list of bytes
        padded = bytearray(message)

        var = sum(message) & 0xFF # introduce slight variability

        # Initialize "Fibonacci" seed values
        prev1 = (padded[-2] + var) & 0xFF
        prev2 = (padded[-1] + var) & 0xFF

        # Generate padding bytes
        for i in range(len(padded), target_length):
            next_byte = (prev1 + prev2 + var) ^ i  # Fibonacci + XOR with index
            padded.append(next_byte & 0xFF)  # Ensure byte range (0–255)
            prev1, prev2 = prev2, next_byte  # Update Fibonacci state

        return bytes(padded)
    
    @staticmethod
    def breeze(x):
        # Gentle rightward nudge, then localized disruption
        gust = Helperly.rotate_right(x, 5)  # A soft rotation, like a light breeze
        drift = (x >> 2) ^ 0xF0F0F0F0F0F0F0F0  # Adds localized turbulence to airflow
        return gust ^ drift  # Combines the motions
    
    @staticmethod
    def draft(x):
        # Alternating directional force
        uplift = Helperly.rotate_left(x, 9)  # Pushes bits upward like an updraft
        downdraft = Helperly.rotate_right(x, 13)  # A stronger downward pull
        eddy = x >> 3  # Localized disruption
        return uplift ^ downdraft ^ eddy  # Combines for balanced motion        
    
    @staticmethod
    def cyclone(x):
        # Chaotic swirling motions
        vortex_inward = Helperly.rotate_right(x, 17)  # Pulls bits inward
        vortex_outward = Helperly.rotate_left(x, 23)  # Expels bits outward
        whirl = Helperly.rotate_right(x, 31)  # Adds additional turbulence
        combined = vortex_inward ^ vortex_outward
        chaos = combined & whirl
        return vortex_inward ^  chaos  # Combines the swirl       
    
    @staticmethod
    def ripple(x):
        # Oscillating and spreading motions
        wavefront = (x >> 3)  # Initial disturbance in the water
        oscillation = Helperly.rotate_right(wavefront, 7)  # Spreads the ripple outward
        propagation = wavefront ^ 0xAAAAAAAAAAAAAAAA  # Adds oscillatory disruption to forward expansion
        return oscillation ^ propagation  # Combines spreading effects       

    @staticmethod
    def wave(x):
        # Rolling and oscillating motions with interference
        crest = Helperly.rotate_left(x, 19)  # The smooth rise of the wave
        trough = (x >> 7) | (x << 5)  # The fall into the trough
        return crest ^ trough # Combines         
    
    @staticmethod
    def torrent(x):
        # Fast and forceful motions
        cascade = Helperly.rotate_right(x, 37)  # A downward, rushing force
        surge = Helperly.rotate_left(x, 29)  # Counterbalancing upward surge
        overflow = x ^ (x >> 15)  # Excessive pressure disrupting bits
        return cascade ^ surge ^ overflow  # Combines for rapid scrambling
    
    @staticmethod
    def confluence(a, b, c):
        # Weighted combination using addition and shifts
        return ((a << 1) + b + (c >> 1)) & 0xFFFFFFFFFFFFFFFF
    
    @staticmethod
    def crosscurrent(a, b, c):
        # Direct bitwise blend based on most significant bit of a
        mask = a >> 63  # Extract the most significant bit as the "current direction"
        return (b & ~mask) | (c & mask)

        
if __name__ == "__main__":
    start_time = time.time()
    
    result = StringToNumber.hash_string("f")

    elapsed_time = time.time() - start_time
    print(f"Took {elapsed_time:.6f} seconds")
    print(result)