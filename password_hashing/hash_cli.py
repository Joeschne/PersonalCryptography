from hash_processing import HashProcessor

if __name__ == "__main__":
    key = input("Please input your hashing key:")
    input = input("Please input a string to hash:")
    print(HashProcessor.hash_input_data(key, input))


