from collections import defaultdict
import time
import os

korpus_path = '/afs/kth.se/misc/info/kurser/DD2350/adk24/labb1/korpus'
raw_index_path = '/afs/kth.se/misc/info/kurser/DD2350/adk24/labb1/rawindex.txt'
index_txt_path = '/var/tmp/index.txt'
hash_txt_path = '/var/tmp/hash.txt'


# Step 1: Process the raw index
def process_raw_index():
    
    word_positions = defaultdict(list)
    with open(raw_index_path, 'r', encoding='latin-1') as rawindex_data:
        for line in rawindex_data:
            line = line.strip()
            word, position = line.split()
            word_positions[word].append(int(position))
    return word_positions

# Step 2: Create the index file
def create_index(word_positions):
    with open(index_txt_path, 'w', encoding='latin-1') as index_data:
        for word, positions in word_positions.items():
            repetitions = len(positions)
            positions_str = ' '.join(map(str, positions))
            index_data.write(f"{word} {repetitions} {positions_str}\n")
    print(f"Index file created at: {index_txt_path}")

# Step 3: Create the hash file (lazy hashing)
def create_hash_list():
    total_entries = 27000  # Total number of hash entries (30 * 30 * 30)

    # Fixed width of each entry in the hash file (e.g., 20 bytes for the position)
    entry_size = 20  # Adjust this size if necessary

    # Open the index file to read
    with open(index_txt_path, 'r', encoding='latin-1') as index_file:
        # Open the hash file in read/write mode and initialize all entries with "-1"
        with open(hash_txt_path, 'w+', encoding='latin-1') as hash_file:
            for _ in range(total_entries):
                # Write "-1" for every possible hash value to initialize the file
                # We ensure that each line takes exactly `entry_size` bytes
                hash_file.write(f"{'-1':<{entry_size - 1}}\n")
            
            # Move the file pointer to the start of the hash file
            hash_file.seek(0)

            # Iterate through each line in the index file
            while True:
                # Get the current byte position in the index file before reading the line
                current_position = index_file.tell()
                line = index_file.readline()

                # Break if the line is empty (end of file)
                if not line:
                    break

                # Split the line into parts (word and positions)
                parts = line.split()

                # Check if the first part is a valid word (not a number)
                if parts and parts[0].isalpha():
                    word = parts[0]  # The first part is the word

                    # Hash the word to find its corresponding position in the hash file
                    hash_value = latmanshashing(word)

                    # Calculate the byte position in the hash file
                    # Since each entry has `entry_size` bytes, multiply the hash value by `entry_size`
                    byte_position = hash_value * (entry_size)  # +1 for newline character

                    # Seek to the byte position in the hash file
                    hash_file.seek(byte_position)

                    # Read the existing value at the current hash position
                    existing_position = hash_file.read(entry_size)
                

                    # If the position is currently "-1", we replace it with the current position
                    
                    # Ensure that the string is not empty before checking the first characte
                    if existing_position and existing_position[0] == "-":

                    
                
                        # Seek back to the correct position
                        hash_file.seek(byte_position)
                        # Write the current byte position from the index file
                        # Ensure the written value takes exactly `entry_size` bytes
                        
                        hash_file.write(f"{str(current_position)}")
                        #hash_file.write(f"{'-2'}")

            print(f"Hash file created at: {hash_txt_path}")

# Step 4: Latmanshashing function (as per instructions)

def hash_conditions(number):
    # a-z becomes 0-25
    if 96 < number < 123:
        return number - 97
    # å becomes 26, ä becomes 27, and ö becomes 28
    elif number == 229:
        return 26
    elif number == 228:
        return 27
    elif number == 246:
        return 28
    # All other characters (spaces, special characters) become 0
    else:
        return 0

def latmanshashing(word):
    word = word[:3]  # Take the first three letters or fewer if the word is shorter
    if len(word) == 1:
        hash_value = hash_conditions(ord(word[0]))  # Single letters (0-28)
    elif len(word) == 2:
        hash_value = 29 + (hash_conditions(ord(word[0])) * 29) + hash_conditions(ord(word[1]))  # Start from 29
    else:
        hash_value = 900 + (hash_conditions(ord(word[0])) * 900) + (hash_conditions(ord(word[1])) * 30) + hash_conditions(ord(word[2]))
    return hash_value
# Run the construction program


if __name__ == "__main__":
    # Step 1: Process the raw index
    start_time = time.time()
    word_positions = process_raw_index()

    # Step 2: Create the index file
    create_index(word_positions)

    # Step 3: Create the hash file
    create_hash_list()
    end_time= time.time()
    print("Konkordans skapad")
    print(f"Hash list created in {end_time - start_time:.4f} seconds at: {hash_txt_path}")