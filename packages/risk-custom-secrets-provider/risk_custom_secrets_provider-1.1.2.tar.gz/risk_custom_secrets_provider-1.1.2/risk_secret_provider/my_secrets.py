from airflow.providers.google.cloud.secrets.secret_manager import CloudSecretManagerBackend
from airflow.secrets import BaseSecretsBackend
from airflow.secrets.metastore import MetastoreBackend
from airflow.utils.log.logging_mixin import LoggingMixin
from typing import Optional, Dict

import hvac
import time
import json


class MyVaultManager(LoggingMixin):
    _dbx_connection_template = "databricks://https://{sp_client_id}:{sp_secret}@{workspace_url}/?service_principal_oauth=true"
    def __init__(self, cloud_secret_manager) -> None:
        super().__init__()
        self.cloud_secret_manager = cloud_secret_manager
        self.vault_client: VaultClient | None = None
        self.metastore: MetastoreBackend | None = None
        self.config: dict = {}
        self.env: str | None = None
        self.supported_connections: list = []
        self._is_initialized = False

    def _init_vault_client(self) -> None:
        if self.vault_client is not None:
            return
        # Initialize Vault client
        role_id = self.cloud_secret_manager.get_variable("risk_vault_role_id")
        if not role_id:
            self.log.warning("Vault Role ID is not found in Cloud Secret Manager.")
        secret_id = self.cloud_secret_manager.get_variable("risk_vault_secret_id")
        if not secret_id:
            self.log.warning("Vault Secret ID is not found in Cloud Secret Manager.")
        vault_url = self.config.get("vault_url", "")
        self.log.info("init with vault_url: {}".format(vault_url))
        self.vault_client = VaultClient(role_id=role_id, secret_id=secret_id, vault_url=vault_url)

    def _load_config(self) -> None:
        if not self.metastore:
            self.metastore = MetastoreBackend()
        if not self.env:
            self.env = 'prod' if self.metastore.get_variable("env") == 'prod' else 'preprod'
        _config = self.metastore.get_variable("custom_sm_config")
        self.config = json.loads(_config) if _config else {}
        self.log.info("Custom Vault Manager config: {}".format(self.config))
        self.supported_connections = self.config.get("supported_connections", [])

    def _get_secret_path(self, conn_id: str) -> str:
        sp = self.config[conn_id]['sp']
        return f'databricks/service_principal_secret/{self.env}/{sp}'

    def get_conn_value(self, conn_id: str) -> str | None:
        self._load_config()
        if conn_id not in self.supported_connections:
            return None
        try:
            self._init_vault_client()
            vault_secrets = self.vault_client.get_credentials(secret_path=self._get_secret_path(conn_id))
            return self._dbx_connection_template.format(
                sp_client_id=vault_secrets['client_id'],
                sp_secret=vault_secrets['secret'],
                workspace_url=self.config[conn_id]['workspace_url']
            )
        except Exception as e:
            self.log.error(f"Error retrieving connection for conn_id {conn_id} from Vault: {e}")
            return None


class VaultClient(LoggingMixin):
    """
    A client for interacting with HashiCorp Vault to retrieve secrets.
    This version includes automatic token renewal and re-authentication.
    """

    def __init__(self, role_id: str, secret_id: str, vault_url: str, max_vault_conn_retry: int = 30,
                 re_auth_interval_minutes: int = 30):
        super().__init__()
        self.role_id = role_id
        self.secret_id = secret_id
        self.vault_url = vault_url
        self.max_vault_conn_retry = max_vault_conn_retry
        self.re_auth_interval_minutes = re_auth_interval_minutes
        self.last_auth_time = None

    def _get_vault_client(self, client_token: Optional[str] = None) -> hvac.Client:
        """Creates and configures an hvac.Client instance."""
        return hvac.Client(url=self.vault_url, token=client_token, timeout=30)

    def _get_vault_token(self) -> str:
        """Logs into Vault using AppRole and retrieves an authentication token."""
        unauthenticated_client = self._get_vault_client()
        for i in range(1, self.max_vault_conn_retry + 1):
            try:
                self.log.info(f"Attempting AppRole login to Vault (attempt #{i})")
                response = unauthenticated_client.auth.approle.login(
                    role_id=self.role_id,
                    secret_id=self.secret_id,
                )
                return response['auth']['client_token']
            except Exception as e:
                self.log.warning(f"Authentication attempt #{i} failed: {e}")
                if i == self.max_vault_conn_retry:
                    raise
                time.sleep(10 * i)
        raise Exception("Failed to get Vault auth token after all retries.")

    def _re_authenticate(self) -> None:
        """Gets a completely new token and re-creates the client."""
        self.log.info("Re-authenticating with AppRole...")
        client_token = self._get_vault_token()
        self.client = self._get_vault_client(client_token)
        self.last_auth_time = time.time()
        self.log.info("Successfully re-authenticated and created new Vault client.")

    def _ensure_token_validity(self) -> None:
        """
        Re-authenticates if 30 minutes have passed since last authentication.
        """
        if self.last_auth_time is None:
            self._re_authenticate()
            return

        current_time = time.time()
        time_since_auth = (current_time - self.last_auth_time) / 60  # Convert to minutes

        if time_since_auth >= self.re_auth_interval_minutes:
            self.log.info(f"Re-authenticating after {time_since_auth:.1f} minutes (threshold: {self.re_auth_interval_minutes} minutes)")
            self._re_authenticate()

    def get_credentials(self, secret_path: str, mount_point: str = 'secret/devops') -> Dict:
        """
        Retrieves credentials from Vault, ensuring the auth token is valid first.
        """
        self._ensure_token_validity()

        try:
            response = self.client.secrets.kv.read_secret_version(path=secret_path, mount_point=mount_point)
            return response['data']['data']
        except Exception as e:
            if "403" in str(e) or "Forbidden" in str(e):
                self.log.warning("Received a 403 Forbidden error. Attempting to re-authenticate and retry...")
                self._re_authenticate()
                response = self.client.secrets.kv.read_secret_version(path=secret_path, mount_point=mount_point)
                return response['data']['data']
            else:
                self.log.error(f"Failed to read secret from '{secret_path}'. Error: {e}")
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

