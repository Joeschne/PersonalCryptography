from collections import Counter
import random
import matplotlib.pyplot as plt
from hash_processing import HashProcessor


# Function to analyze raw hash output
def analyze_raw_hash_output(hash_function, key, num_samples=100):
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

    # Normalize frequencies for visualization
    total_characters = sum(char_frequencies.values())
    normalized_frequencies = {char: freq / total_characters for char, freq in char_frequencies.items()}
    
    # Visualize the distribution
    plt.figure(figsize=(12, 6))
    plt.bar(normalized_frequencies.keys(), normalized_frequencies.values(), width=0.8, align='center')
    plt.title("Character Frequency Distribution in Hash Output")
    plt.xlabel("Characters")
    plt.ylabel("Normalized Frequency")
    plt.xticks(rotation=90)  # Rotate labels for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    return normalized_frequencies


if __name__ == "__main__":
    # Run the analysis
    key = "test_key"
    bucket_counts = analyze_raw_hash_output(HashProcessor.hash_input_data, key)
