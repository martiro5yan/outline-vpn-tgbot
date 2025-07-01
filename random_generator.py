import random
import string

def generate_random_string(length: int=10, include_digits: bool = True, include_uppercase: bool = True, include_lowercase: bool = True) -> str:
    characters = ''
    if include_digits:
        characters += string.digits
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    
    if not characters:
        raise ValueError("At least one character set must be included.")
    
    return ''.join(random.choice(characters) for _ in range(length))

