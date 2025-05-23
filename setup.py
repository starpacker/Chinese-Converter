from setuptools import setup, find_packages

setup(
    name='Chinese Converter',
    version='0.1.0',
    description='A smart pinyin-to-Chinese converter using LLMs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='starpacker',
    url='https://github.com/starpacker/Chinese-Converter', 
    packages=find_packages(),
    install_requires=[
        'torch',
        'transformers',
        'jieba',
        'streamlit',
        'accelerate',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
