from collections import Counter
import random
import matplotlib.pyplot as plt
from hash_processing import HashProcessor
import math

# Function to analyze raw hash output
def analyze_raw_hash_output(hash_function, key, num_samples=10000, visualize=True):
    char_frequencies = Counter()
    counter = 0
    interval = num_samples // 100

    for _ in range(num_samples):
        # Generate random input data
        random_data = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
        hash_value = hash_function(random_data, key, 2951, True, False)

        # Count the occurrences of each character in the hash output
        char_frequencies.update(hash_value)

        # Progress indicator
        counter += 1
        if counter % interval == 0:
            print(f"{counter / num_samples * 100:.2f}% complete")

    # Normalize frequencies for analysis and visualization
    total_characters = sum(char_frequencies.values())
    normalized_frequencies = {char: freq / total_characters for char, freq in char_frequencies.items()}
    
    # Visualize the distribution if required
    if visualize:
        plt.figure(figsize=(12, 6))
        plt.bar(normalized_frequencies.keys(), normalized_frequencies.values(), width=0.8, align='center')
        plt.title("Character Frequency Distribution in Hash Output")
        plt.xlabel("Characters")
        plt.ylabel("Normalized Frequency")
        plt.xticks(rotation=90)  # Rotate labels for better readability
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.show()

    return normalized_frequencies

# Function to test if distribution is within acceptable bounds
def test_distribution_bounds(normalized_frequencies, total_characters):
    # Number of distinct characters
    N = len(normalized_frequencies)

    # Expected entropy for a uniform distribution of N characters
    expected_entropy = math.log2(N)

    # Calculate observed entropy
    entropy = -sum(p * math.log2(p) for p in normalized_frequencies.values() if p > 0)

    # Allowable entropy deviation: decreases with sqrt of total_samples
    # Feel free to adjust these parameters to be more or less strict
    max_entropy_deviation = 0.05 + 1.0 / math.sqrt(total_characters)

    # Check entropy bounds
    if abs(entropy - expected_entropy) > max_entropy_deviation:
        return False, (
            f"Entropy {entropy:.4f} deviates from expected {expected_entropy:.4f} "
            f"by more than {max_entropy_deviation:.4f}."
        )

    # Uniform frequency for each character
    uniform_frequency = 1.0 / N

    # Standard error for uniform frequency estimation:
    # se = sqrt(p*(1-p)/M) ≈ sqrt((1/N)*(N-1)/M) for large M
    std_dev_freq = math.sqrt((1.0/N) * ((N-1.0)/N) / total_characters)
    # Allow frequencies to deviate by, say, 3 standard deviations
    max_freq_deviation = 3 * std_dev_freq

    # Check individual frequency deviations
    for char, freq in normalized_frequencies.items():
        if abs(freq - uniform_frequency) > max_freq_deviation:
            return (
                f"Character '{char}' frequency {freq:.4f} deviates too much from "
                f"uniform frequency {uniform_frequency:.4f} (allowed deviation {max_freq_deviation:.4f})."
            )

    return "Distribution is within acceptable bounds."

# Example unit test
if __name__ == "__main__":
    sample_size=1000
    # Run the analysis
    key = "test_key"
    normalized_frequencies = analyze_raw_hash_output(HashProcessor.hash_input_data, key, num_samples=sample_size, visualize=True)

    # Test parameters
    EXPECTED_ENTROPY = 5.7  # Expected entropy for ~62 characters with uniform distribution
    MAX_DEVIATION = 0.005  # Allowable deviation in frequency and entropy

    # Validate distribution
    test_result, message = test_distribution_bounds(normalized_frequencies, sample_size*16)
    print(message)

    if not test_result:
        raise AssertionError(message)
