import sys
import time


korpus_path = '/afs/kth.se/misc/info/kurser/DD2350/adk24/labb1/korpus'
raw_index_path = '/afs/kth.se/misc/info/kurser/DD2350/adk24/labb1/rawindex.txt'
index_txt_path = '/var/tmp/index.txt'
hash_txt_path = '/var/tmp/hash.txt'




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

def search_hash_positions_in_hash_list(word):
    hash_value = latmanshashing(word)
    line_length = 20  # Fixed line length for each entry (20 bytes)
    byte_offset = hash_value * line_length

    # Open the file and check if it can be read
    hash_file = open(hash_txt_path, 'r', encoding='latin-1')
    try:
        # Seek to the calculated byte offset
        hash_file.seek(byte_offset)
        
        # Read exactly 20 characters (the fixed line length)
        current_position_line = hash_file.read(line_length).strip()

        # Check if the current position is valid (non-empty, non-`-1`)
        if current_position_line == '-1' or not current_position_line:
            print(f"Det finns inga förekomster av '{word}' i korpus filen")
            hash_file.close()
            return None, None

        # Extract the first number as the current position
        parts = current_position_line.split()
        if not parts:
            print(f"Invalid format at position: '{current_position_line}'")
            hash_file.close()
            return None, None

        current_position = parts[0]
        
        # Ensure current_position is numeric before converting to int
        if not current_position.isdigit():
            print(f"Invalid current position found: '{current_position}'")
            hash_file.close()
            return None, None

        #NSök efter current och next position

        current_position = int(current_position)

        # Initialize next_position
        next_position = None
        

        while True:
            # Move 20 bytes ahead for the next position
            byte_offset += line_length
            hash_file.seek(byte_offset)
            
            # Read the next 20 bytes (line length)
            next_position_line = hash_file.read(line_length).strip()

            # If the next line is empty or the end of the file is reached, break the loop
            if not next_position_line:
                break

            # Split the next position line and check for validity
            next_position_parts = next_position_line.split()

            if not next_position_parts:
                print(f"Invalid format at position: '{next_position_line}'")
                continue  # Skip this line if format is invalid

            if next_position_parts[0] != '-1':
                next_position = next_position_parts[0]
                
                if next_position.isdigit():
                    next_position = int(next_position)  
                else:
                    print(f"Invalid next position found: '{next_position}'")
                    next_position = None
                    break

        # After the loop, determine if the next position is valid
       

            return current_position, None

        # Return the current and next positions (next position can be None)
        return current_position, next_position

    finally:
        hash_file.close()




# Step 2: Binary search in the index file
def binary_search_on_index_file(current_position, next_position, word):
    
    
    if current_position is None and next_position is None:
        return None, 0, word  # No need to proceed with the binary search
    
    with open(index_txt_path, 'r', encoding='latin-1') as index_file:
        i = int(current_position)
        # If next_position is None, set j to the end of the file
        if next_position is None:
            index_file.seek(0, 2)  # Seek to the end of the file
            j = index_file.tell()  # Get the position of the end of the file
        else:
            j = int(next_position)

        found = False

        while (j - i) > 1000:
            middle = (i + j) // 2
            index_file.seek(middle)
            index_file.readline()
            line = index_file.readline()
            if not line:
                break
            parts = line.split()
            middle_word = parts[0]
            if middle_word == word:
                instances_of_words = int(parts[1])
                array_for_instances = [int(parts[2 + k]) for k in range(instances_of_words)]
                found = True
                return array_for_instances, instances_of_words, word
            elif middle_word > word:
                j = middle
            else:
                i = middle
        
        if not found:
           return linear_search_on_index_file_with_q(i, j, word)

        # If still not found, handle the "word doesn't exist" ca
    
    return None, 0, word


# Step 3: Fallback to linear search
def linear_search_on_index_file_with_q(low, high, word):
    
   
    
    
    with open(index_txt_path, 'r', encoding='latin-1') as index_file:
        index_file.seek(low)  # Start from the low position

        while low < high:  # Restrict the search range
            line = index_file.readline()
            if not line or low >= high:
                break
            parts = line.split()
            if parts[0] == word:
                instances_of_words = int(parts[1])
                array_for_instances = [int(parts[2 + k]) for k in range(instances_of_words)]
                return array_for_instances, instances_of_words, word
            low = index_file.tell()  # Move to the next position
        return None, 0, word

# Step 4: Function to print appearances in the corpus
def appearences_korpus(array_for_instances, instances_of_words, word):

    with open(korpus_path, 'r', encoding='latin-1') as korpus_file:
        word_length = len(word)
        
        if (array_for_instances is None or instances_of_words == '0'):
            print(f"Det finns inga förekomster av order '{word}' i korpus filen")
            return 


        for byte_position in array_for_instances[:25]:
            start_pos = max(byte_position - 30, 0)  # 30 bytes before the word (but no negative positions)
            end_pos = byte_position + word_length + 30  # 30 bytes after the word
            korpus_file.seek(start_pos)
            line_containing_word = korpus_file.read(end_pos - start_pos)
            line_containing_word = line_containing_word.replace('\r\n', ' ').replace('\n', ' ')
            print(line_containing_word)
            
        while(instances_of_words >25):
                question = input(f" Det finna fler än 25 förekomster av ordet '{word}', Vill du ha förekomsterna utskriva på skärmen. Svara [Ja] eller [Nej]").strip().lower()

                if(question == ("nej")):
                    break
                elif(question == ("ja")):
                    for byte_position in array_for_instances[25:]:
                        start_pos = max(byte_position - 30, 0)
                        end_pos = byte_position + word_length + 30
                        korpus_file.seek(start_pos)
                        line_containing_word = korpus_file.read(end_pos - start_pos)
                        line_containing_word = line_containing_word.replace('\r\n', ' ').replace('\n', ' ')
                        print(line_containing_word)
                    break
                else:
                    print("ogiltigt svar. Svara [Ja] eller [Nej]")
        

# Main test runner
if __name__ == "__main__":
    
   
    
     # Ensure a word is provided as an argument
    if len(sys.argv) < 2:
        print("No word was provided for the search.")
        sys.exit(1)

    # Extract and clean the word
    word = sys.argv[1].strip().lower()
    print(f"Searching for word: {word}")

    # Search for the positions in the hash list
    current_position, next_position = search_hash_positions_in_hash_list(word)

    # Check if positions were found and print the result
    if current_position is not None:
        
        
        # Seek to a specific position in the index file (you can update 733743430 as needed)
        #test_seek_to_position(index_txt_path, 733743430)

        # Perform binary search in the index file for the word's instances
        array_for_instances, instances_of_words, word = binary_search_on_index_file(current_position, next_position, word)
        
    
        
        appearences_korpus(array_for_instances, instances_of_words, word)
    else:
        print(f"No valid position found for '{word}'.")



    