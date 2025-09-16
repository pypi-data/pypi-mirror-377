# pcservices/campaign/validator.py
import yaml

VALID_OPERATORS = {"=", "!=", ">", ">=", "<", "<=", "IN"}

def validate_campaign_yaml(yaml_path: str):
    """
    Validate the structure of a campaign YAML file.
    Raises ValueError if validation fails.
    """
    with open(yaml_path, "r") as f:
        cfg = yaml.safe_load(f)

    if "campaigns" not in cfg:
        raise ValueError("Missing top-level 'campaigns' key")

    for campaign_name, campaign_def in cfg["campaigns"].items():
        # Check data_sources
        data_sources = campaign_def.get("data_sources", [])
        if not data_sources:
            raise ValueError(f"Campaign '{campaign_name}' has no data_sources defined")

        for ds in data_sources:
            if "table" not in ds:
                raise ValueError(f"Data source '{ds.get('name')}' missing 'table'")
            for flt in ds.get("filters", []):
                if "column" not in flt or "operator" not in flt or "value" not in flt:
                    raise ValueError(f"Invalid filter definition: {flt}")
                if flt["operator"] not in VALID_OPERATORS:
                    raise ValueError(f"Unsupported operator '{flt['operator']}' in filter {flt}")

            # derived_columns are optional, just check name and expression if provided
            for col_def in ds.get("derived_columns", []):
                if "name" not in col_def or "expression" not in col_def:
                    raise ValueError(f"Invalid derived column: {col_def}")

        # Control group
        cg = campaign_def.get("control_group")
        if cg:
            if "customer_id" not in cg or "selection_method" not in cg or "buckets" not in cg:
                raise ValueError(f"Control group incomplete: {cg}")

        # Timeframes
        tf = campaign_def.get("timeframes")
        if tf:
            required_keys = ["training_start", "training_end", "campaign_start", "campaign_end"]
            for k in required_keys:
                if k not in tf:
                    raise ValueError(f"Missing timeframe '{k}' in campaign '{campaign_name}'")

        # Output tables
        out_tbls = campaign_def.get("output_tables", {})
        for key in ["exposure", "response", "execution_list"]:
            if key not in out_tbls:
                raise ValueError(f"Missing output table '{key}' in campaign '{campaign_name}'")

    print(f"✅ Campaign YAML '{yaml_path}' passed validation")
    return True