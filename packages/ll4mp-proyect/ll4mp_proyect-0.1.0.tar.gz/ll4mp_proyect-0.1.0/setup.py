from setuptools import setup, find_packages

# Leer el contenido del archivo README.md para usarlo como long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

from setuptools import setup, find_packages

setup(
    name="ll4mp_proyect",
    version="0.1.0",
    author="Tu Nombre",
    author_email="pikp0k4@gmail.com",  
    description="Un proyecto de ejemplo",
    packages=find_packages(),
    install_requires=[],
)

