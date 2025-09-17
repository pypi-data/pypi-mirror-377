import yaml

from hep_data_llm.query_config import load_config, load_yaml_file


def test_load_yaml_known() -> None:
    """One from resources"""
    data = load_yaml_file("atlas-sx-awk-hist.yaml")
    assert "hint_collections" in data
    assert "prompts" in data
    assert "model_name" in data


def test_load_config_default() -> None:
    """Ensure the default profile loads correctly."""
    cfg = load_config()
    assert cfg.model_name == "gpt-4.1"


def test_load_config_custom_profile(tmp_path) -> None:
    """Profiles should resolve to local YAML files."""
    test_data = {
        "hint_collections": {
            "default": {
                "hint_files": ["hint.txt"],
                "python_files": ["helper.py"],
            },
            "legacy": ["legacy-hint.md"],
        },
        "prompts": {
            "prompt": {"text": "p", "hint_collection": "default"},
            "modify_prompt": {"text": "m", "hint_collection": "default"},
        },
        "model_name": "foo-model",
        "docker_image": "",
    }
    cfg_file = tmp_path / "my-profile.yaml"
    with cfg_file.open("w", encoding="utf-8") as f:
        yaml.dump(test_data, f)
    cfg = load_config(str(cfg_file.with_suffix("")))
    assert cfg.model_name == "foo-model"
    assert cfg.hint_collections["default"].python_files == ["helper.py"]
    assert cfg.hint_collections["legacy"].hint_files == ["legacy-hint.md"]
    assert cfg.hint_collections["legacy"].python_files == []


def test_load_yaml_file_with_tempfile(tmp_path):
    test_data = {"foo": "bar", "baz": [1, 2, 3]}
    tmp_file = tmp_path / "test.yaml"
    with tmp_file.open("w") as f:
        yaml.dump(test_data, f)
    loaded = load_yaml_file(str(tmp_file))
    assert loaded == test_data


def test_load_yaml_file_not_found():
    import pytest

    with pytest.raises(FileNotFoundError):
        load_yaml_file("this_file_does_not_exist.yaml")
