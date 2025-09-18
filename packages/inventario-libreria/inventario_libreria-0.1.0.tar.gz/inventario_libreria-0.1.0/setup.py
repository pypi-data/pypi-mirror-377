from setuptools import setup, find_packages

setup(
    name='inventario-libreria',
    version='0.1.0',
    author='Celso Paolo Velasco Espinoza', 
    author_email='celsovelasco.sis24ch@tecba.edu.bo',
    description='Una librería pequeña para la gestión de inventario y cálculos básicos.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/CelsoPaolo/Mi_libreria.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)