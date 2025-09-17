from airflow.providers.google.cloud.secrets.secret_manager import CloudSecretManagerBackend
from airflow.secrets import BaseSecretsBackend
from airflow.models import Variable
from airflow.utils.log.logging_mixin import LoggingMixin
from typing import Optional, Dict, List

import hvac
import time


class MyVaultManager(LoggingMixin):
    _dbx_connection_template = "databricks://https://{sp_client_id}:{sp_secret}@{workspace_url}/?service_principal_oauth=true"
    def __init__(self, cloud_secret_manager) -> None:
        self.vault_client = None
        self.env = 'prod' if Variable.get("env") == 'prod' else 'preprod'
        self.cloud_secret_manager = cloud_secret_manager
        self.config = Variable.get("custom_secret_manager_config", deserialize_json=True, default_var={})
        self.log.info("Custom Vault Manager config: {}".format(self.config))
        self.supported_connections = self.config.get("supported_connections", [])
        super().__init__()

    def _lazy_init(self) -> None:
        role_id = self.cloud_secret_manager.get_variable("risk_vault_role_id")
        if not role_id:
            self.log.warning("Vault Role ID is not found in Cloud Secret Manager.")
        secret_id = self.cloud_secret_manager.get_variable("risk_vault_secret_id")
        if not secret_id:
            self.log.warning("Vault Secret ID is not found in Cloud Secret Manager.")
        vault_url = self.config.get("vault_url", "")
        self.log.info("init with vault_url: {}".format(vault_url))
        self.vault_client = VaultClient(role_id=role_id, secret_id=secret_id, vault_url=vault_url)

    def _get_secret_path(self, conn_id: str) -> str:
        sp = self.config[conn_id]['sp']
        return f'databricks/service_principal_secret/{self.env}/{sp}'

    def get_conn_value(self, conn_id: str) -> str | None:
        if conn_id not in self.supported_connections:
            return None
        if self.vault_client is None:
            self._lazy_init()
        vault_secrets = self.vault_client.get_credentials(secret_path=self._get_secret_path(conn_id))
        return self._dbx_connection_template.format(
            sp_client_id=vault_secrets['client_id'],
            sp_secret=vault_secrets['secret'],
            workspace_url=self.config[conn_id]['workspace_url']
        )

class VaultClient(LoggingMixin):
    """
    A client for interacting with HashiCorp Vault to retrieve secrets.
    This class is a Python equivalent of the Java VaultClient, using the 'hvac' library.
    """

    def __init__(self, role_id: str, secret_id: str, vault_url: str, max_vault_conn_retry: int = 30):
        """
        Initializes the VaultClient.

        Args:
            role_id (str): The AppRole Role ID for authentication.
            secret_id (str): The AppRole Secret ID for authentication.
            vault_url (str, optional): The URL of the Vault server. Defaults to "https://vault-toolbox-pci.awx.im".
            max_vault_conn_retry (int, optional): Maximum number of retries for connecting to Vault. Defaults to 30.
        """
        self.role_id = role_id
        self.secret_id = secret_id
        self.vault_url = vault_url
        self.max_vault_conn_retry = max_vault_conn_retry
        self._client_token = self._get_vault_token()
        self.client = self._get_vault_client(self._client_token)
        super().__init__()


    def _get_vault_client(self, client_token: Optional[str] = None) -> hvac.Client:
        """
        Creates and configures an hvac.Client instance.

        Args:
            client_token (Optional[str]): A Vault client token. If None, the client is unauthenticated.

        Returns:
            hvac.Client: A configured hvac client instance.
        """
        # In hvac, the equivalent of 'prefixPathDepth' is handled by mounting paths.
        # We will assume standard secret engine paths.
        client = hvac.Client(
            url=self.vault_url,
            token=client_token,
            timeout=30
        )
        return client

    def _get_vault_token(self) -> str:
        """
        Logs into Vault using AppRole and retrieves an authentication token.
        Returns:
            str: The Vault authentication token.
        """
        unauthenticated_client = self._get_vault_client()
        for i in range(1, self.max_vault_conn_retry + 1):
            try:
                self.log.info(f"Attempting to connect to Vault and get auth token #{i}")
                response = unauthenticated_client.auth.approle.login(
                    role_id=self.role_id,
                    secret_id=self.secret_id,
                )
                return response['auth']['client_token']
            except Exception as e:
                self.log.warning(f"Authentication attempt #{i} failed: {e}")
                if i == self.max_vault_conn_retry:
                    raise  # Re-raise the last exception if all retries fail
                # Linear backoff, sleeping for 10, 20, 30... seconds
                time.sleep(10 * i)
        raise Exception("Failed to get Vault auth token after all retries.")

    def get_credentials(self, secret_path: str, mount_point: str = 'secret/devops') -> Dict:
        try:
            # The hvac library automatically handles different versions of KV secrets engine.
            # For KVv2, the data is nested under response['data']['data'].
            # For KVv1, it's response['data'].
            response = self.client.secrets.kv.read_secret_version(path=secret_path, mount_point=mount_point)
            return response['data']['data']
        except Exception as e:
            print(f"Failed to read secret from '{secret_path}'. Error: {e}")
            raise

class MySecretManager(BaseSecretsBackend, LoggingMixin):
    def __init__(
        self,
        connections_prefix: str = "risk-airflow-connection",
        variables_prefix: str = "risk-airflow-variable",
        config_prefix: str = "risk-airflow-config",
        sep: str = "-",
        **kwargs,
    ) -> None:
        self.cloud_secret_manager = CloudSecretManagerBackend(
            connections_prefix=connections_prefix,
            variables_prefix=variables_prefix,
            config_prefix=config_prefix,
            sep=sep,
            **kwargs
        )
        self.vault_secret_manager = MyVaultManager(self.cloud_secret_manager)

        super().__init__()

    def get_conn_value(self, conn_id: str) -> str | None:
        self.log.info(f"Retrieving connection for conn_id: {conn_id}")
        vault_value = self.vault_secret_manager.get_conn_value(conn_id=conn_id)
        if vault_value is not None:
            self.log.info(f"Connection for conn_id: {conn_id} retrieved from Vault.")
            return vault_value
        self.log.info(f"Connection for conn_id: {conn_id} not found in Vault. Falling back to Cloud Secret Manager.")
        return self.cloud_secret_manager.get_conn_value(conn_id=conn_id)

    def get_variable(self, key: str) -> str | None:
        self.log.info(f"Retrieving variable for key: {key}")
        return self.cloud_secret_manager.get_variable(key=key)

