from setuptools import setup, find_packages

setup(
    name="options-pricer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'pytz',
        'tensorflow',
        'scikit-learn',
        'scipy',
    ],
)