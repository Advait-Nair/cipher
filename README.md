# Cipheria
Custom Python 3.12/NiceGUI application used to crack and solve the National Cipher Challenge 2025's 10 chapters.

This Python program was designed and amended to meet the unique requirements for the NCC2025 as it continued. Built on NiceGUI, it runs a local webserver that allows interaction with the main cipher-breaking functionality.

## Ciphers available
- Caesar
- Substitution
- Affine
- Transposition
- Vigenère + Brute-Force utilities
- Playfair + Brute-Force utilities
- Four Square

## Features
- IoC analysis: Analyses plaintext and ciphertext both automatically and on-request, providing insight on whether a cipher is polyalphabetic or follows standard English patterns
- IoC Poisson Hypothesis Testing: Uses a pre-calibrated hypothesis test to determine whether an IoC fits the English Language's patterns, or has been passed through a polyalphabetic cipher
- Parameter Cycling (unstable for larger ciphers): allows looping through a certain parameter, such as a Caesar Shift, and returns the plaintext with the best IoC
- Text Utilities: Text manipulation for cleanliness and output
- Order Mapping: Recognises patterns in non-polyalphabetic text by matching them with a dictionary
- Built-in dictionary with compiled order map for order analysis
- Full extract of A Christmas Carol, which can be input as a file location to brute-force various ciphers. The NCC2025 used words in A Christmas Carol as keys.
- QoL: auto-running ciphers on parameter change (which should be disabled for many polyalphabetic ciphers due to their compute-intense implementation!)

## Recommendations
- This software has no safeguards to prevent crashing, memory leaks or instability. More intense ciphers, especially during brute forces, have a much higher chance of crashing your tab/server and as a result you should limit BF parameter sizes
- Do not enable auto-run for intense ciphers, as once the first change/keystroke has been logged, the cipher runs in parallel until complete, forcing you to wait until completion for the program to then re-run your complete ciphertext.
- Be careful using the cycler, as it loses stability on more intense ciphers

## Installation
0. You need Python 3.12.11+. This program is untested on other versions of Python, but may work!
1. Clone this repo or download source to your machine with `git clone "https://github.com/Advait-Nair/cipher.git"`
2. Setup your .venv by running `python -m venv .venv`
3. Install dependencies with pip: `pip install -r requirements.txt`
4. Run main.py **after activating venv**: `source .venv/bin/.activate && python3 main.py` Use Python 3.12+.
