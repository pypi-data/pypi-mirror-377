from setuptools import setup, find_packages

setup(
    name="risk-custom-secrets-provider",
    version="1.0.5",
    packages=find_packages(),
    install_requires=[
        "hvac ==2.3.0",
        "apache-airflow-providers-google ==10.23.0",
        "apache-airflow ==2.9.3",
    ],
)