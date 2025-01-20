import pytest
from shared.config.config import Config

def test_config_load():
    """測試配置載入"""
    config = Config.get_instance()
    assert config is not None
    assert isinstance(config, Config)

def test_config_singleton():
    """測試單例模式"""
    config1 = Config.get_instance()
    config2 = Config.get_instance()
    assert config1 is config2

def test_config_update():
    """測試配置更新"""
    config = Config.get_instance()
    test_value = "test_value"
    config.update(MODEL_NAME=test_value)
    assert config.MODEL_NAME == test_value 