from setuptools import setup, find_packages

setup(
    name="nobiaspy",
    author="jamcha123",
    author_email="jameschambers732@gmail.com",
    description="nobiaspy helps you find fallacies and fact checks youtube videos",
    packages=find_packages(where="pipy"),
    url="https://github.com/Jamcha123/NoBS",
    entry_points={
        "console_scripts": [
            "nobiaspy=pipy.index:cli"
        ]
    }
)