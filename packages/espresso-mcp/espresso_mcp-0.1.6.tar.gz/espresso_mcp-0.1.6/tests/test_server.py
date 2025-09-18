import pytest


def test_import_server():
    import espresso_mcp.server


def test_dummy():
    assert True


def test_main_exists():
    from espresso_mcp import server

    assert hasattr(server, "main")
    assert callable(server.main)


def test_list_avds_exists():
    from espresso_mcp import server

    assert hasattr(server, "list_avds")
    assert callable(server.list_avds)


def test_list_emulators_exists():
    from espresso_mcp import server

    assert hasattr(server, "list_emulators")
    assert callable(server.list_emulators)


def test_dump_current_activity_exists():
    from espresso_mcp import server

    assert hasattr(server, "dump_current_activity")
    assert callable(server.dump_current_activity)


def test_replace_text_exists():
    from espresso_mcp import server

    assert hasattr(server, "replace_text")
    assert callable(server.replace_text)
