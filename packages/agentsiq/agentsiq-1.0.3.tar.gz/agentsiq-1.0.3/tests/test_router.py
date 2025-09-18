"""
Tests for AgentsIQ Router
"""

import pytest
from agentsiq.router import ModelRouter
from agentsiq.config_loader import load_config


def test_router_initialization():
    """Test that ModelRouter initializes correctly"""
    router = ModelRouter()
    assert router is not None
    assert hasattr(router, 'profiles')
    assert hasattr(router, 'weights')
    assert hasattr(router, 'strategy')


def test_router_profiles():
    """Test that router has expected model profiles"""
    router = ModelRouter()
    profiles = router.profiles
    
    # Check that we have some expected models
    expected_models = [
        'openai:gpt-4o-mini',
        'openai:gpt-4o',
        'anthropic:claude-3-haiku',
        'google:gemini-pro'
    ]
    
    for model in expected_models:
        assert model in profiles
        assert 'cost' in profiles[model]
        assert 'latency' in profiles[model]
        assert 'quality' in profiles[model]


def test_router_weights():
    """Test that router has correct default weights"""
    router = ModelRouter()
    weights = router.weights
    
    assert 'cost' in weights
    assert 'latency' in weights
    assert 'quality' in weights
    assert weights['cost'] + weights['latency'] + weights['quality'] == 1.0


def test_router_strategy():
    """Test that router has a valid strategy"""
    router = ModelRouter()
    valid_strategies = ['smart', 'cheapest', 'fastest', 'hybrid']
    assert router.strategy in valid_strategies


def test_select_model():
    """Test model selection functionality"""
    router = ModelRouter()
    
    # Test with a simple task
    task = "Hello world"
    model = router.select_model(task)
    
    assert model is not None
    assert isinstance(model, str)
    assert ':' in model  # Should be in format "provider:model"


def test_traits_detection():
    """Test task trait detection"""
    from agentsiq.router import _traits
    
    # Test code detection
    code_task = "Write a Python function to sort a list"
    traits = _traits(code_task)
    assert traits['is_code'] is True
    
    # Test summary detection
    summary_task = "Summarize this document"
    traits = _traits(summary_task)
    assert traits['is_summary'] is True
    
    # Test math detection
    math_task = "Calculate 2 + 2"
    traits = _traits(math_task)
    assert traits['has_math'] is True


def test_config_loading():
    """Test configuration loading"""
    config = load_config()
    assert config is not None
    assert 'settings' in config
    assert 'router' in config['settings']


if __name__ == "__main__":
    pytest.main([__file__])
