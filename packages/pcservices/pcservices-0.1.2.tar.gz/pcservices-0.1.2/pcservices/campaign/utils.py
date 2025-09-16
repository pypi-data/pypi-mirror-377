# pcservices/campaign/utils.py
import hashlib
import random
from typing import List, Optional, Union, Any, Dict
import yaml

def generate_buckets(
    n: int,
    control_group: List[int],
    max_bucket: int = 99,
    seed: Optional[int] = None
) -> List[int]:
    """
    Generate `n` random bucket numbers between 0 and max_bucket (inclusive),
    excluding the values in control_group. Optionally set a random seed.
    
    Parameters:
        n (int)                : number of buckets to generate
        control_group (list)   : list of bucket numbers to exclude
        max_bucket (int)       : upper bound of bucket range (default = 99)
        seed (int or None)     : random seed for reproducibility (default = None)
    
    Returns:
        List[int]: list of generated bucket numbers, sorted
    """
    if seed is not None:
        random.seed(seed)

    # Build a list of eligible buckets
    eligible = [b for b in range(max_bucket + 1) if b not in control_group]

    if n > len(eligible):
        raise ValueError(
            f"Requested {n} buckets, but only {len(eligible)} are available "
            f"after excluding the control group."
        )

    return sorted(random.sample(eligible, n))


def get_consistent_customer_number(customer_id: Union[str, None]) -> int:
    """
    Generate a deterministic integer between 0 and 99 for a customer ID (e.g., email).
    
    Parameters:
        customer_id (str or None): customer identifier
    
    Returns:
        int: deterministic number between 0 and 99, -1 if invalid input
    """
    if not customer_id or not isinstance(customer_id, str):
        return -1

    # Step 1: Normalize the customer ID
    normalized = customer_id.strip().lower()
    
    # Step 2: Hash the normalized string using SHA-256
    hash_digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    
    # Step 3: Convert a portion of the hash to integer
    hash_int = int(hash_digest[:15], 16)
    
    # Step 4: Map to 0-99
    return hash_int % 100

def assign_cohort(df, customer_number_col="customer_number", control_bucket=None):
    from pyspark.sql import functions as F
    if control_bucket is None:
        raise ValueError("control_bucket must be provided")
    return df.withColumn(
        "cohort",
        F.when(F.col(customer_number_col).isin(control_bucket), "control").otherwise("treatment")
    )


def load_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file into a dictionary."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def save_config(config: Dict[str, Any], path: str) -> None:
    """Save dictionary to YAML file."""
    with open(path, "w") as f:
        yaml.safe_dump(config, f)

def add_campaign(config: Dict[str, Any], name: str, campaign_dict: Dict[str, Any]) -> None:
    """Add a new campaign to the config."""
    if "campaigns" not in config:
        config["campaigns"] = {}
    config["campaigns"][name] = campaign_dict

def update_campaign(config: Dict[str, Any], name: str, updates_dict: Dict[str, Any]) -> bool:
    """Update an existing campaign. Returns True if updated, False if campaign not found."""
    if name in config.get("campaigns", {}):
        config["campaigns"][name].update(updates_dict)
        return True
    return False

def delete_campaign(config: Dict[str, Any], name: str) -> bool:
    """Delete a campaign. Returns True if deleted, False if campaign not found."""
    if name in config.get("campaigns", {}):
        config["campaigns"].pop(name)
        return True
    return False