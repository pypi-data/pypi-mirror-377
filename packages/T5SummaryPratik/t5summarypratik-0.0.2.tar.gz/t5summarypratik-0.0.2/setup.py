from setuptools import setup, find_packages

setup(
    name="T5SummaryPratik",
    version="0.0.2",
    description="A summarization pipeline using T5 with evaluation metrics and utilities.",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.30.0",
        "torch>=1.13.0",
        "evaluate>=0.4.0",
        "nltk>=3.8.1",
        "textstat>=0.7.3"
    ],
    python_requires=">=3.8",
)
