
import string

def is_palindrome(text: str, ignore_case=True, ignore_spaces=True, ignore_punctuation=True) -> bool:
    """Check if the word or sentence is a Palindrome"""
    if ignore_case:
        text = text.lower()
    if ignore_spaces:
        text = text.replace(" ", "")
    if ignore_punctuation:
        text = text.translate(str.maketrans('', '', string.punctuation))
    return text == text[::-1]

def check_multiple(texts: list, **kwargs) -> list:
    """Check the texts list if they are Palindrome."""
    return [is_palindrome(t, **kwargs) for t in texts]
