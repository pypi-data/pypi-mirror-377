
from .checker import is_palindrome
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: PalindromeCheckerLib <text>")
        return
    text = " ".join(sys.argv[1:])
    if is_palindrome(text):
        print(f" '{text}' is a palindrome!")
    else:
        print(f" '{text}' is not a palindrome.")

if __name__ == "__main__":
    main()
