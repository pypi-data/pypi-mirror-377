from setuptools import setup, find_packages

setup(
    name='JobTitleTransformer',  # Must be unique on PyPI
    version='0.1.11',
    packages=find_packages(), # include=["jobtitletransformer"]
    package_data={"JobTitleTransformer": ["job_scripts/*.py"]},
    install_requires=[
        'pandas',
        'numpy',
        'nltk',
        'termcolor',
        'tabulate',
        "scikit-learn",
        "sentence-transformers",
        "faiss-cpu",
        "torch"
    ],
    author='Prasanna UTHAMARAJ',
    author_email='prasanna.uthamaraj@informa.com',  # Optional but nice
    description='A healthcare-focused job title transformation pipeline.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/PrasannaDataBus/JobTitleTransformer',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'jobtitle-transformer = JobTitleTransformer.runner:run_pipeline',
        ],
    }
)