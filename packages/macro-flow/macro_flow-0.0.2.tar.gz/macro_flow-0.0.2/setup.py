from setuptools import setup , find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='macro-flow',
    version='0.0.2',
    description='ETL Para banco macro, extrae pdf desde la url que le pongas, extrae datos y crea chunks que sube a s3 (aws)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Walter Facundo Vega',
    author_email='facundo.vega1234@gmail.com',
    url='https://github.com/facuvegaingenieer/macro-flow',
    license='MIT', 
    packages=find_packages(),
    install_requires=[
        'pandas',
        'boto3',
        'pyarrow',
        'python-dotenv',
        'requests',
        'pdfplumber',
        'langchain',
    ],
    entry_points={
        'console_scripts': [
            'trackflow=track_flow.main:main',
        ],
    },
    python_requires='>=3.8',
    
    classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
],
)