# Overview

The purpose of this library is to Create, Edit, and Display Truth Tables of any size. 

It is able to be used seemlessly inside jupyter notebooks.

I wrote this software because I was searching for something that would simplify the process of creating truth tables, but I was unable to find anything that did the job how I wanted it to do it. In the end I wrote this to streamline the entire process down to a few lines of code.

[Software Demo Video](https://youtu.be/dvyICgiUduQ)

# Development Environment

I programmed the entire thing inside of VS Code using Python 3.11.9. I also had the Gemini Code Assist extension enabling faster production. I also will be installing and using the following libraries: setuptools, wheel, twine, and multiprocess.

# Useful Websites

- [Python.org : multiprocessing — Process-based parallelism](https://docs.python.org/3/library/multiprocessing.html)
- [Real Python : How to Publish an Open-Source Python Package to PyPI](https://realpython.com/pypi-publish-python-package/)
- [Packaging Python User Guide : Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Youtube : How to Publish a Python Package to PyPI (pip)](https://youtu.be/Kz6IlDCyOUY?si=OIfgLYkwv6yhSrez)

# Future Work

- [x] It is not setup in a way to be made into a python library just yet. This is the next step in the development process.  
- [x] The entire program needs to be re-written in such a way that you can remove columns and it wont break the previously written lines of code.  
- [ ] Currently has functionality to create a truth table of any size, but it is incredibly slow to create them after a certain size is reached considering the nature of truth table length being 2^n possible scenarios (n being the number of vaiables in the truth table). There are plans to add multiprocessing to help speed up the process of creating truth tables.
- [ ] Add the package to the official PyPi repository.