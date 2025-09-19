from pathlib import Path
from setuptools import setup, find_packages

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="TextAnalyzerLib",
    version="0.1.0",
    description="Analyze text: words, sentences, characters, word frequency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="aisha aljmal",
    author_email="moaljml3601@gmail.com",
    packages=find_packages(),
    python_requires='>=3.13',
    license="MIT",
    entry_points={
        "console_scripts": ["TextAnalyzerLib=textanalyzer.__main__:main"]
    }
)
