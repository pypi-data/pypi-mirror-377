
from setuptools import setup, find_packages

setup(
    name="PalindromeCheckerLib",
    version="0.1.0",
    description="Check if text is a palindrome",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ali Alsheikh",
    author_email="a77561289@gmail.com ",
    packages=find_packages(),
    python_requires='>=3.13',
    license="MIT",
    entry_points={"console_scripts": ["PalindromeCheckerLib=palindrome.__main__:main"]}
)
