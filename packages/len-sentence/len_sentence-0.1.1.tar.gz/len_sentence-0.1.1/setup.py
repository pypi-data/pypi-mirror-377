from setuptools import setup, find_packages

setup(
    name="len-sentence",
    version="0.1.1",
    author="JackyHe398",
    author_email="hekinghung@gmail.com",
    description="Length of sentence utilities for counting the number of words/characters in a sentence",
    install_requires=[],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)

# python -m build
# twine upload dist/*