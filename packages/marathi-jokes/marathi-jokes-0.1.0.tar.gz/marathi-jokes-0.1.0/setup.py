from setuptools import setup, find_packages

setup(
    name="marathi-jokes",
    version="0.1.0",
    description="A fun Marathi Jokes library 😂",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Aditya Pawar",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/marathi-jokes",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
