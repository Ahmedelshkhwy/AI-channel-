def claude_client() -> Any | None:
    """Only when a key is configured; the built-in engine answers otherwise."""
    source = ai_key_source()
    if not source:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    return anthropic.Anthropic(api_key=saved_ai_key() if source == "saved" else None, max_retries=1, timeout=60.0)
