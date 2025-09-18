import os
import logging
import pickle
import base64
import hashlib
import getpass
import platform
import socket
import subprocess
import sys
import requests
import psutil
from cryptography.fernet import Fernet
from trino.dbapi import connect
from trino.auth import BasicAuthentication

# --- CONFIG ---
DEFAULT_PICKLE = "token.pkl"
# Change this if you want a strict VPN IP check (otherwise None = allow any private IP)
REQUIRED_IPV4 = "192.168"


class MaskedCreds(dict):
    """Dictionary wrapper that masks sensitive fields on print/repr."""

    SENSITIVE_KEYS = {"TRINO_USER", "TRINO_PASSWORD"}

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __repr__(self):
        masked = {
            k: ("***masked***" if k in self.SENSITIVE_KEYS else v)
            for k, v in self.items()
        }
        return str(masked)


def email_to_fernet_key(email: str) -> bytes:
    if not isinstance(email, str) or not email:
        raise ValueError("Email must be a non-empty string")
    digest = hashlib.sha256(email.strip().lower().encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return key


def load_credentials_from_pickle(pickle_file: str, email_for_key: str):
    if not os.path.exists(pickle_file):
        raise FileNotFoundError(f"{pickle_file} not found")

    fernet_key = email_to_fernet_key(email_for_key)
    fernet = Fernet(fernet_key)

    with open(pickle_file, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted = fernet.decrypt(encrypted_data)
    except Exception as e:
        raise ValueError("Unauthorised User, Please enter correct mail?") from e

    creds = pickle.loads(decrypted)
    if not isinstance(creds, dict):
        raise ValueError("Failed to fetch Credentials")

    if "JUPYTERHUB_USER" not in creds or not creds["JUPYTERHUB_USER"]:
        raise ValueError("Unauthorised User")

    return MaskedCreds(creds)


# ---------------------------
# VPN / Network checks
# ---------------------------
def vpn_connected(required_ip: str = None) -> bool:
    """
    Check if VPN is connected on Windows/Linux/macOS.
    If required_ip is given, match it. Otherwise, just ensure we have a private IP.
    """
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4 only
                    ip = addr.address
                    if required_ip and ip == required_ip:
                        return True
                    if ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172."):
                        return True
        return False
    except Exception as e:
        logging.error(f"VPN check failed: {e}")
        return False

# ---------------------------
# Package version check + reload
# ---------------------------
def ensure_latest_pwpy_db(force_update: bool = False):
    """
    Check installed pwpy_db version vs PyPI.
    If outdated, upgrade automatically.
    Reload inside current session so Jupyter doesn't need restart.
    """
    import importlib

    try:
        from importlib.metadata import version, PackageNotFoundError
    except ImportError:
        from importlib_metadata import version, PackageNotFoundError  # type: ignore

    local_ver = None
    try:
        local_ver = version("pwpy_db")
    except PackageNotFoundError:
        pass

    latest_ver = None
    try:
        resp = requests.get("https://pypi.org/pypi/pwpy_db/json", timeout=5)
        resp.raise_for_status()
        latest_ver = resp.json()["info"]["version"]
    except Exception as e:
        logging.warning(f"Could not fetch latest version info: {e}")
        return

    needs_update = force_update or (local_ver != latest_ver)

    if needs_update:
        print(f"Installing/Updating pwpy_db (local: {local_ver}, latest: {latest_ver}) ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "pwpy_db"])

        # force reload in Jupyter kernel (no restart needed)
        if "pwpy_db" in sys.modules:
            print("Reloading pwpy_db in current session ...")
            importlib.reload(sys.modules["pwpy_db"])
    else:
        print(f"pwpy_db is up-to-date (version {local_ver})")


# ---------------------------
# Trino fetch function
# ---------------------------
def fetch_trino_data(query: str, pickle_file: str = DEFAULT_PICKLE, entered_email: str = None):
    # check latest pwpy_db
    ensure_latest_pwpy_db()

    # check VPN
    if not vpn_connected(REQUIRED_IPV4):
        print("VPN not connected. Aborting.")
        return None

    if entered_email is None:
        entered_email = input("Enter the email to connect: ").strip()

    if not entered_email:
        print("No email entered. Aborting.")
        return None

    # --- load credentials ---
    try:
        creds = load_credentials_from_pickle(pickle_file, entered_email)
    except Exception as e:
        logging.error(f"Failed to load credentials: {e}")
        print(f"Failed to load credentials: {e}")
        return None

    # extract trino connection parameters
    try:
        user_type = creds["USER_TYPE"]
        user_name = creds["TRINO_USER"]
        password = creds["TRINO_PASSWORD"]
        host = creds["TRINO_HOST"]
        port = int(creds.get("TRINO_PORT", 443))
        http_scheme = creds.get("TRINO_HTTP_SCHEME", "https")
        jupyter_user_email = creds["JUPYTERHUB_USER"]
    except KeyError as ke:
        logging.error(f"Missing required Trino credential key: {ke}")
        print(f"Missing required Trino credential key: {ke}")
        return None

    # logged-in user and PC
    logged_user = getpass.getuser()
    pc_name = platform.node()

    # inject identifying comment
    comment = (
        f"/*entered_email:{entered_email}, jupyter_user:{jupyter_user_email}, "
        f"logged_user:{logged_user}, pc_name:{pc_name}, user_type={user_type}*/ "
    )
    modified_query = comment + query

    # connect to Trino and execute
    try:
        print(f"Connecting to Trino as {user_name} (jupyter_user={jupyter_user_email})")
        conn = connect(
            host=host,
            port=port,
            user=user_name,
            auth=BasicAuthentication(user_name, password),
            http_scheme=http_scheme,
        )
        cur = conn.cursor()
        cur.execute(modified_query)
        results = cur.fetchall()
        # If you prefer a DataFrame, return DataFrame (pandas optional)
        try:
            import pandas as pd
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            cur.close()
            conn.close()
            print("Query executed successfully.")
            return df
        except Exception:
            # fallback to raw results
            cur.close()
            conn.close()
            return results

    except Exception as e:
        logging.error(f"Error executing query: {e}")
        print(f"Error executing query: {e}")
        return None
