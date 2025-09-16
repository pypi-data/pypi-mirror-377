# pcservices/campaign/utils.py
import hashlib
import random
from typing import List, Optional, Union, Any, Dict
import yaml
from pyspark.sql import functions as F
from pyspark.sql import DataFrame
from pyspark.sql.types import IntegerType

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


# --------------------------
# Deterministic bucket number
# --------------------------
def get_consistent_customer_number(customer_id: Union[str, None]) -> int:
    """Generate a deterministic integer between 0 and 99 for a customer ID (e.g., email)."""
    if not customer_id or not isinstance(customer_id, str):
        return -1

    normalized = customer_id.strip().lower()
    hash_digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    hash_int = int(hash_digest[:15], 16)
    return hash_int % 100


# --------------------------
# UDF wrapper for Spark usage
# --------------------------
def udf_customer_number(col_name: str = "customer_id", output_col: str = "customer_number"):
    """
    Return a DataFrame transform that adds a deterministic customer_number column.
    """
    udf_func = F.udf(get_consistent_customer_number, IntegerType())

    def _transform(df: DataFrame) -> DataFrame:
        return df.withColumn(output_col, udf_func(F.col(col_name)))

    return _transform


# --------------------------
# Cohort assignment
# --------------------------
def assign_cohort(
    df: DataFrame,
    customer_number_col: str = "customer_number",
    control_bucket: list = None,
    cohort_col: str = "cohort"
) -> DataFrame:
    """Assign control vs treatment groups based on deterministic customer_number."""
    if control_bucket is None:
        raise ValueError("control_bucket must be provided")

    return df.withColumn(
        cohort_col,
        F.when(F.col(customer_number_col).isin(control_bucket), "control").otherwise("treatment")
    )


# --------------------------
# Composite helper
# --------------------------
def assign_control_treatment(
    df: DataFrame,
    customer_id_col: str = "customer_id",
    control_bucket: list = None,
    customer_number_col: str = "customer_number",
    cohort_col: str = "cohort"
) -> DataFrame:
    """
    Composite function:
    1. Deterministically map customer_id -> customer_number (0–99)
    2. Assign cohort as control/treatment
    """
    df = udf_customer_number(col_name=customer_id_col, output_col=customer_number_col)(df)
    df = assign_cohort(df, customer_number_col=customer_number_col, control_bucket=control_bucket, cohort_col=cohort_col)
    return df


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