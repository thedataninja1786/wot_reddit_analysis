def get_env_variable(var_name: str) -> str:
    import os
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Environment variable '{var_name}' is not set or empty.")
    return value
