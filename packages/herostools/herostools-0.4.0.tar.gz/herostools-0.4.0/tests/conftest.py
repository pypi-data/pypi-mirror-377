import pytest
from heros import LocalHERO, RemoteHERO
from heros.event import event
import numpy as np
import time


@pytest.fixture(scope="session")
def local_hero_device():
    class TestDevice(LocalHERO):
        test_var = 1

        def trigger_np(self, data: np.typing.NDArray, metadata: dict) -> None:
            self.np_event(data, metadata)

        @event
        def np_event(self, data: np.typing.NDArray, metadata: dict) -> tuple:
            return data, metadata

        def trigger_json(self, data: dict, metadata: dict) -> None:
            self.json_event(data, metadata)

        @event
        def json_event(self, data: dict, metadata: dict) -> tuple:
            return data, metadata

    dev = TestDevice("test_hero")
    yield dev
    dev._destroy_hero()
    dev._session_manager.force_close()


@pytest.fixture(scope="session")
def remote_hero_device():
    return RemoteHERO("test_hero")


@pytest.fixture()
def check_async_saved_np_file():
    def func(path: str, reference, max_retries: int = 10):
        retries = 0
        data = False
        while retries < max_retries and not isinstance(data, np.ndarray):
            time.sleep(0.1)
            try:
                data = np.load(path)
            except (ValueError, FileNotFoundError, EOFError):
                # not fully written
                pass
            retries += 1
        assert ((data == reference) | (np.isnan(data) & np.isnan(reference))).all()

    return func
