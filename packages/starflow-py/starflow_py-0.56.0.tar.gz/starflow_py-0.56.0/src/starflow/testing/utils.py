import os
import pytest

def skip_envs(*envs):
    env = os.environ.get('STARFLOW_TESTS_ENVIRONMENT')
    return pytest.mark.skipif(env in list(envs),reason=f"Not suitable envrionment {env} for current test")