"""
SSL Certificate Analysis Utilities

This module provides functions to parse and analyze SSL certificates
for both server and client sides of SimpleLinks connections.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


def get_certificate_info(cert_path: str) -> Dict:
    """
    Get detailed information from an SSL certificate file
    
    Args:
        cert_path: Path to the certificate file
        
    Returns:
        Dictionary containing certificate details or error information
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        return {"error": "cryptography library not available"}
    
    cert_file = Path(cert_path)
    if not cert_file.exists():
        return {"error": f"Certificate file not found: {cert_path}"}
    
    try:
        with open(cert_file, "rb") as f:
            cert_data = f.read()
        
        # Try to load as PEM first, then DER
        try:
            cert = x509.load_pem_x509_certificate(cert_data)
        except ValueError:
            try:
                cert = x509.load_der_x509_certificate(cert_data)
            except ValueError:
                return {"error": "Invalid certificate format (not PEM or DER)"}
        
        # Extract certificate details
        subject = cert.subject
        common_name = None
        for attribute in subject:
            if attribute.oid == NameOID.COMMON_NAME:
                common_name = attribute.value
                break
        
        # Get SAN (Subject Alternative Names)
        san_list = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_list = [str(name) for name in san_ext.value]
        except x509.ExtensionNotFound:
            pass
        
        # Get public key info
        public_key = cert.public_key()
        key_type = "Unknown"
        key_size = None
        
        if hasattr(public_key, 'key_size'):
            key_size = public_key.key_size
            # Determine key type based on the key object type
            key_class_name = public_key.__class__.__name__
            if 'RSA' in key_class_name:
                key_type = "RSA"
            elif 'EC' in key_class_name or 'ECC' in key_class_name:
                key_type = "ECDSA"
            elif 'Ed25519' in key_class_name:
                key_type = "Ed25519"
            elif 'Ed448' in key_class_name:
                key_type = "Ed448"
        
        # Handle different cryptography library versions for datetime
        not_valid_before = None
        not_valid_after = None
        
        # Try new attribute names first (cryptography >= 42.0.0)
        if hasattr(cert, 'not_valid_before_utc'):
            not_valid_before = cert.not_valid_before_utc
            not_valid_after = cert.not_valid_after_utc
        # Fallback to old attribute names
        elif hasattr(cert, 'not_valid_before'):
            not_valid_before = cert.not_valid_before
            not_valid_after = cert.not_valid_after
        
        # Calculate expiry information
        is_expired = False
        days_until_expiry = 0
        
        if not_valid_after:
            now = datetime.utcnow()
            # Handle timezone-aware datetime objects
            if hasattr(not_valid_after, 'tzinfo') and not_valid_after.tzinfo is not None:
                # If certificate time is timezone-aware, make sure now is also UTC
                from datetime import timezone
                now = now.replace(tzinfo=timezone.utc)
            elif hasattr(now, 'tzinfo') and now.tzinfo is not None:
                # If now is timezone-aware but cert time isn't, make now naive
                now = now.replace(tzinfo=None)
            
            is_expired = not_valid_after < now
            days_until_expiry = (not_valid_after - now).days
        
        # Get signature algorithm
        signature_algorithm = "Unknown"
        if hasattr(cert, 'signature_algorithm_oid'):
            signature_algorithm = cert.signature_algorithm_oid._name
        
        return {
            "fqdn": common_name,
            "subject": str(subject),
            "issuer": str(cert.issuer),
            "serial_number": str(cert.serial_number),
            "not_valid_before": not_valid_before.isoformat() if not_valid_before else None,
            "not_valid_after": not_valid_after.isoformat() if not_valid_after else None,
            "is_expired": is_expired,
            "days_until_expiry": days_until_expiry,
            "key_type": key_type,
            "key_size": key_size,
            "san": san_list,
            "signature_algorithm": signature_algorithm,
            "cert_path": str(cert_file)
        }
        
    except Exception as e:
        return {"error": f"Failed to parse certificate: {str(e)}"}


def get_peer_certificate_info(ssl_object) -> Dict:
    """
    Get certificate information from an SSL connection
    
    Args:
        ssl_object: SSL socket object
        
    Returns:
        Dictionary containing peer certificate details
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        return {"error": "cryptography library not available"}
    
    try:
        # Get peer certificate in DER format
        peer_cert = ssl_object.getpeercert(binary_form=True)
        if not peer_cert:
            return {"error": "No peer certificate available"}
        
        cert = x509.load_der_x509_certificate(peer_cert)
        
        # Extract certificate details
        subject = cert.subject
        common_name = None
        for attribute in subject:
            if attribute.oid == NameOID.COMMON_NAME:
                common_name = attribute.value
                break
        
        # Get SAN
        san_list = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            san_list = [str(name) for name in san_ext.value]
        except x509.ExtensionNotFound:
            pass
        
        # Handle different cryptography library versions for datetime
        not_valid_after = None
        if hasattr(cert, 'not_valid_after_utc'):
            not_valid_after = cert.not_valid_after_utc
        elif hasattr(cert, 'not_valid_after'):
            not_valid_after = cert.not_valid_after
        
        # Calculate days until expiry
        days_until_expiry = 0
        if not_valid_after:
            now = datetime.utcnow()
            # Handle timezone-aware datetime objects
            if hasattr(not_valid_after, 'tzinfo') and not_valid_after.tzinfo is not None:
                from datetime import timezone
                now = now.replace(tzinfo=timezone.utc)
            elif hasattr(now, 'tzinfo') and now.tzinfo is not None:
                now = now.replace(tzinfo=None)
            
            days_until_expiry = (not_valid_after - now).days
        
        return {
            "server_fqdn": common_name,
            "server_issuer": str(cert.issuer),
            "server_san": san_list,
            "server_expires": not_valid_after.isoformat() if not_valid_after else None,
            "server_days_until_expiry": days_until_expiry
        }
        
    except Exception as e:
        return {"error": f"Failed to get peer certificate info: {str(e)}"}


def format_ssl_info_for_display(ssl_info: Dict, prefix: str = "") -> List[str]:
    """
    Format SSL information for console display
    
    Args:
        ssl_info: SSL information dictionary
        prefix: Prefix for each line
        
    Returns:
        List of formatted strings ready for display
    """
    lines = []
    
    if not ssl_info.get('enabled', False):
        lines.append(f"{prefix}SSL: Disabled")
        return lines
    
    if 'error' in ssl_info:
        lines.append(f"{prefix}SSL: Enabled (Error: {ssl_info['error']})")
        return lines
    
    lines.append(f"{prefix}SSL: Enabled")
    
    if 'fqdn' in ssl_info and ssl_info['fqdn']:
        lines.append(f"{prefix}  FQDN: {ssl_info['fqdn']}")
    
    if 'key_type' in ssl_info and 'key_size' in ssl_info and ssl_info['key_size']:
        lines.append(f"{prefix}  Key: {ssl_info['key_type']}/{ssl_info['key_size']}")
    
    if 'days_until_expiry' in ssl_info:
        days = ssl_info['days_until_expiry']
        if ssl_info.get('is_expired'):
            lines.append(f"{prefix}  Certificate: ⚠️ EXPIRED {abs(days)} days ago")
        elif days < 30:
            lines.append(f"{prefix}  Certificate: ⚠️ Expires in {days} days")
        else:
            lines.append(f"{prefix}  Certificate: Valid ({days} days remaining)")
    
    if 'san' in ssl_info and ssl_info['san']:
        san_display = ', '.join(ssl_info['san'][:3])
        if len(ssl_info['san']) > 3:
            san_display += ' ...'
        lines.append(f"{prefix}  SAN: {san_display}")
    
    return lines


def format_client_ssl_info_for_display(ssl_info: Dict, prefix: str = "") -> List[str]:
    """
    Format client SSL information for console display
    
    Args:
        ssl_info: SSL information dictionary
        prefix: Prefix for each line
        
    Returns:
        List of formatted strings ready for display
    """
    lines = []
    
    if not ssl_info.get('enabled', False):
        lines.append(f"{prefix}SSL: Disabled")
        return lines
    
    verification_status = "Verified" if ssl_info.get('verified') else "Unverified (Self-signed)"
    lines.append(f"{prefix}SSL: Enabled ({verification_status})")
    
    if 'server_fqdn' in ssl_info and ssl_info['server_fqdn']:
        lines.append(f"{prefix}  Server FQDN: {ssl_info['server_fqdn']}")
    
    if 'server_days_until_expiry' in ssl_info:
        days = ssl_info['server_days_until_expiry']
        if days < 30:
            lines.append(f"{prefix}  Certificate: ⚠️ Expires in {days} days")
        else:
            lines.append(f"{prefix}  Certificate: Valid ({days} days remaining)")
    
    return lines
