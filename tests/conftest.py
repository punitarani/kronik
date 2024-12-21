def pytest_configure(config):
    """Configure pytest options."""
    config.option.asyncio_default_fixture_loop_scope = "function"
