def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def normalize_config(user_cfg, defaults):
    cfg = deep_merge(defaults, user_cfg or {})
    if not cfg["openai"]["apiKey"]:
        raise ValueError("openai.apiKey is required")
    # ensure logger
    if not cfg.get("logger"):
        import logging
        cfg["logger"] = logging.getLogger("python_ai_ragbot")
    return cfg
