from setuptools import setup, find_packages

setup(
    name="risk-custom-secrets-provider",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "apache_airflow_provider": [
            "risk_custom_secrets_provider = risk_secret_provider.my_secrets:MySecretManager"
        ]
    },
    install_requires=[
        "hvac ==2.3.0",
        "apache-airflow-providers-google ==10.23.0",
        "apache-airflow ==2.9.3",
    ],
)