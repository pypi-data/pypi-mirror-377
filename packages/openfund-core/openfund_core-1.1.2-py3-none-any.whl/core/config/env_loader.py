"""
Environment variable loader for API credentials.
Handles loading and validating API credentials from environment variables.
"""

import os
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PlatformCredentials:
    """Data class for platform API credentials."""
    api_key: Optional[str] = None
    secret: Optional[str] = None
    password: Optional[str] = None


class EnvironmentConfigLoader:
    """Loads and validates API credentials from environment variables."""
    
    # Mapping of platform names to their environment variable keys
    CREDENTIAL_ENV_MAPPING = {
        'binance': {
            'apiKey': 'OPENFUND_BINANCE_API_KEY',
            'secret': 'OPENFUND_BINANCE_SECRET'
        },
        'okx': {
            'apiKey': 'OPENFUND_OKX_API_KEY',
            'secret': 'OPENFUND_OKX_SECRET',
            'password': 'OPENFUND_OKX_PASSWORD'
        },
        'bitget': {
            'apiKey': 'OPENFUND_BITGET_API_KEY',
            'secret': 'OPENFUND_BITGET_SECRET'
        }
    }
    
    # Required credentials for each platform
    REQUIRED_CREDENTIALS = {
        'binance': ['apiKey', 'secret'],
        'okx': ['apiKey', 'secret', 'password'],
        'bitget': ['apiKey', 'secret']
    }

    def __init__(self):
        """Initialize the environment config loader."""
        self._load_dotenv()

    def _load_dotenv(self) -> None:
        """Load environment variables from .env file if it exists."""
        env_file = '.env'
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value:
                                os.environ[key] = value
                logger.info(f"Loaded environment variables from {env_file}")
            except Exception as e:
                logger.warning(f"Could not load .env file: {e}")

    def load_platform_credentials(self, platform: str) -> Dict[str, Optional[str]]:
        """
        Load API credentials for a specific platform from environment variables.
        
        Args:
            platform: Platform name (binance, okx, bitget)
            
        Returns:
            Dictionary with credential keys and their values from environment variables
            
        Raises:
            ValueError: If platform is not supported
        """
        if platform not in self.CREDENTIAL_ENV_MAPPING:
            raise ValueError(f"Unsupported platform: {platform}")
        
        platform_mapping = self.CREDENTIAL_ENV_MAPPING[platform]
        credentials = {}
        
        for cred_key, env_key in platform_mapping.items():
            env_value = os.getenv(env_key)
            credentials[cred_key] = env_value
            
            if env_value:
                logger.debug(f"Loaded {cred_key} for {platform} from environment variable {env_key}")
            else:
                logger.debug(f"Environment variable {env_key} not set for {platform} {cred_key}")
        
        return credentials

    def validate_credentials(self, platform: str, credentials: Dict[str, Optional[str]]) -> bool:
        """
        Validate that all required credentials are present for a platform.
        
        Args:
            platform: Platform name
            credentials: Dictionary of credentials to validate
            
        Returns:
            True if all required credentials are present and non-empty
        """
        if platform not in self.REQUIRED_CREDENTIALS:
            logger.error(f"Unknown platform for validation: {platform}")
            return False
        
        required_creds = self.REQUIRED_CREDENTIALS[platform]
        missing_creds = []
        
        for cred_key in required_creds:
            if not credentials.get(cred_key):
                missing_creds.append(cred_key)
        
        if missing_creds:
            logger.error(f"Missing required credentials for {platform}: {missing_creds}")
            return False
        
        logger.info(f"All required credentials present for {platform}")
        return True

    def get_credential_with_fallback(self, env_key: str, yaml_value: Optional[str]) -> Optional[str]:
        """
        Get credential value with fallback from environment variable to YAML value.
        
        Args:
            env_key: Environment variable key
            yaml_value: Fallback value from YAML configuration
            
        Returns:
            Credential value from environment variable or YAML fallback
        """
        env_value = os.getenv(env_key)
        
        if env_value:
            logger.debug(f"Using environment variable {env_key}")
            return env_value
        elif yaml_value and yaml_value.strip():
            logger.warning(f"Using YAML value for {env_key} (deprecated - please use environment variables)")
            return yaml_value
        else:
            logger.error(f"No value found for {env_key} in environment variables or YAML")
            return None

    def get_missing_credentials(self, platform: str) -> List[str]:
        """
        Get list of missing environment variables for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            List of missing environment variable names
        """
        if platform not in self.CREDENTIAL_ENV_MAPPING:
            return []
        
        platform_mapping = self.CREDENTIAL_ENV_MAPPING[platform]
        required_creds = self.REQUIRED_CREDENTIALS.get(platform, [])
        missing_env_vars = []
        
        for cred_key in required_creds:
            env_key = platform_mapping.get(cred_key)
            if env_key and not os.getenv(env_key):
                missing_env_vars.append(env_key)
        
        return missing_env_vars

    def get_all_platforms_status(self) -> Dict[str, Dict[str, bool]]:
        """
        Get credential status for all supported platforms.
        
        Returns:
            Dictionary with platform names and their credential availability status
        """
        status = {}
        
        for platform in self.CREDENTIAL_ENV_MAPPING.keys():
            credentials = self.load_platform_credentials(platform)
            platform_status = {}
            
            for cred_key, value in credentials.items():
                platform_status[cred_key] = bool(value and value.strip())
            
            status[platform] = platform_status
        
        return status