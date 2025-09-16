from setuptools import setup, find_packages

setup(
    name="baza-crypto",  # Nombre de tu librería
    version="0.2.0",
    author="Artemio Baza",
    author_email="alexdevmega@proton.me",
    description="Librería de encriptación y hashing personalizable en Python",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Alex-Dev-Beep/baza",  # Si tienes repo
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "cryptography>=41.0",
        "argon2-cffi>=21.3",
        "bcrypt>=4.0"
    ],
)
