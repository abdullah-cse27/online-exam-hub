import hashlib

def word_to_sha256(word):
    # convert string to bytes
    word_bytes = word.encode('utf-8')
    
    # create sha256 hash
    sha256_hash = hashlib.sha256(word_bytes)
    
    # convert to hexadecimal
    return sha256_hash.hexdigest()


# Example
text = input("Enter word: ")
hashed_value = word_to_sha256(text)

print("SHA256 Hash:", hashed_value)