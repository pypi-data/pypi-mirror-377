"""
Credential validation utilities for API credentials.
Provides validation logic for different platform credential requirements.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CredentialValidator:
    """Validates API credentials for different trading platforms."""
    
    # Platform-specific validation rules
    VALIDATION_RULES = {
        'binance': {
            'apiKey': {
                'min_length': 64,
                'max_length': 64,
                'pattern': r'^[A-Za-z0-9]{64}$',
                'description': 'Binance API key should be 64 alphanumeric characters'
            },
            'secret': {
                'min_length': 64,
                'max_length': 64,
                'pattern': r'^[A-Za-z0-9]{64}$',
                'description': 'Binance secret should be 64 alphanumeric characters'
            }
        },
        'okx': {
            'apiKey': {
                'min_length': 32,
                'max_length': 40,
                'pattern': r'^[a-f0-9-]{32,40}$',
                'description': 'OKX API key should be 32-40 characters with lowercase hex and dashes'
            },
            'secret': {
                'min_length': 32,
                'max_length': 32,
                'pattern': r'^[A-F0-9]{32}$',
                'description': 'OKX secret should be 32 uppercase hexadecimal characters'
            },
            'password': {
                'min_length': 1,
                'max_length': 30,
                'pattern': r'^.+$',
                'description': 'OKX passphrase should be 1-30 characters'
            }
        },
        'bitget': {
            'apiKey': {
                'min_length': 20,
                'max_length': 50,
                'pattern': r'^[A-Za-z0-9]+$',
                'description': 'Bitget API key should be 20-50 alphanumeric characters'
            },
            'secret': {
                'min_length': 20,
                'max_length': 50,
                'pattern': r'^[A-Za-z0-9+/=]+$',
                'description': 'Bitget secret should be base64-encoded string'
            }
        }
    }

    def validate_platform_credentials(self, platform: str, credentials: Dict[str, Optional[str]]) -> Tuple[bool, List[str]]:
        """
        Validate all credentials for a specific platform.
        
        Args:
            platform: Platform name (binance, okx, bitget)
            credentials: Dictionary of credential key-value pairs
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if platform not in self.VALIDATION_RULES:
            return False, [f"Unsupported platform: {platform}"]
        
        errors = []
        platform_rules = self.VALIDATION_RULES[platform]
        
        for cred_key, rules in platform_rules.items():
            credential_value = credentials.get(cred_key)
            
            # Check if credential is present
            if not credential_value:
                errors.append(f"Missing {cred_key} for {platform}")
                continue
            
            # Validate credential format
            validation_errors = self._validate_credential_format(
                platform, cred_key, credential_value, rules
            )
            errors.extend(validation_errors)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info(f"All credentials valid for {platform}")
        else:
            logger.error(f"Credential validation failed for {platform}: {errors}")
        
        return is_valid, errors

    def _validate_credential_format(self, platform: str, cred_key: str, 
                                  value: str, rules: Dict) -> List[str]:
        """
        Validate a single credential against format rules.
        
        Args:
            platform: Platform name
            cred_key: Credential key (apiKey, secret, password)
            value: Credential value to validate
            rules: Validation rules for this credential
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check length requirements
        if 'min_length' in rules and len(value) < rules['min_length']:
            errors.append(
                f"{platform} {cred_key} too short: {len(value)} chars "
                f"(minimum {rules['min_length']})"
            )
        
        if 'max_length' in rules and len(value) > rules['max_length']:
            errors.append(
                f"{platform} {cred_key} too long: {len(value)} chars "
                f"(maximum {rules['max_length']})"
            )
        
        # Check pattern requirements
        if 'pattern' in rules:
            pattern = rules['pattern']
            if not re.match(pattern, value):
                description = rules.get('description', f'Invalid format for {platform} {cred_key}')
                errors.append(f"{description}")
        
        return errors

    def get_missing_credentials(self, platform: str, credentials: Dict[str, Optional[str]]) -> List[str]:
        """
        Get list of missing required credentials for a platform.
        
        Args:
            platform: Platform name
            credentials: Dictionary of available credentials
            
        Returns:
            List of missing credential keys
        """
        if platform not in self.VALIDATION_RULES:
            return []
        
        missing = []
        platform_rules = self.VALIDATION_RULES[platform]
        
        for cred_key in platform_rules.keys():
            if not credentials.get(cred_key):
                missing.append(cred_key)
        
        return missing

    def validate_credential_completeness(self, platform: str, credentials: Dict[str, Optional[str]]) -> bool:
        """
        Check if all required credentials are present (without format validation).
        
        Args:
            platform: Platform name
            credentials: Dictionary of credentials
            
        Returns:
            True if all required credentials are present
        """
        missing = self.get_missing_credentials(platform, credentials)
        return len(missing) == 0

    def get_validation_help(self, platform: str) -> Dict[str, str]:
        """
        Get help text for credential validation requirements.
        
        Args:
            platform: Platform name
            
        Returns:
            Dictionary mapping credential keys to their validation descriptions
        """
        if platform not in self.VALIDATION_RULES:
            return {}
        
        help_text = {}
        platform_rules = self.VALIDATION_RULES[platform]
        
        for cred_key, rules in platform_rules.items():
            help_text[cred_key] = rules.get('description', f'No description available for {cred_key}')
        
        return help_text

    def sanitize_credential_for_logging(self, credential: str) -> str:
        """
        Sanitize credential value for safe logging (show only first/last few characters).
        
        Args:
            credential: Credential value to sanitize
            
        Returns:
            Sanitized credential string safe for logging
        """
        if not credential or len(credential) < 8:
            return "***"
        
        return f"{credential[:4]}...{credential[-4:]}"