"""Load YAML configuration and allow environment variables to override it."""
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _as_bool ( value ) :
    """Convert common environment string values to a real boolean."""
    return str(value).strip().lower() in {"1" , "true" , "yes" , "y"}


def load_config () :
    """Return application configuration with environment overrides applied."""
    config_path = PROJECT_ROOT / "config" / "config.yaml"
    with config_path.open(encoding="utf-8") as config_file :
        config = yaml.safe_load(config_file) or {}

    overrides = {
        "base_url" : os.getenv("BASE_URL") ,
        "browser" : os.getenv("BROWSER") ,
        "transfer_amount" : os.getenv("TRANSFER_AMOUNT") ,
        "account_type" : os.getenv("ACCOUNT_TYPE") ,
        "wait_timeout" : os.getenv("WAIT_TIMEOUT") ,
    }
    for key , value in overrides.items() :
        if value not in (None , "") :
            config[key] = float(value) if key == "transfer_amount" else (
                int(value) if key == "wait_timeout" else value
            )

    headless = os.getenv("HEADLESS")
    if headless is not None :
        config["headless"] = _as_bool(headless)
    return config


def load_test_data () :
    """Load non-sensitive registration defaults from the test-data YAML file."""
    path = PROJECT_ROOT / "data" / "test_data.yaml"
    with path.open(encoding="utf-8") as data_file :
        return yaml.safe_load(data_file) or {}
