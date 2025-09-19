"""conftest.py module for testing."""

########################################################################
# Standard Library
########################################################################
import pytest

from typing import Any, cast, Generator

import logging

########################################################################
# Third Party
########################################################################

########################################################################
# Local
########################################################################
from scottbrian_utils.exc_hook import ExcHook

########################################################################
# logging
########################################################################
# logging.basicConfig(filename='MyLogFile.log',
#                     filemode='w',
#                     level=logging.DEBUG,
#                     format='%(asctime)s '
#                            '%(msecs)03d '
#                            '[%(levelname)8s] '
#                            '%(filename)s:'
#                            '%(funcName)s:'
#                            '%(lineno)d '
#                            '%(message)s')

logger = logging.getLogger(__name__)


########################################################################
# thread_exc
#
# Usage:
# The thread_exc is an autouse fixture which means it does not need to
# be specified as an argument in the test case methods. If a thread
# fails, such as an assertion error, then thread_exc will capture the
# error and raise it for the thread, and will also raise it during
# cleanup processing for the mainline to ensure the test case fails.
# Without thread_exc, any uncaptured thread failure will appear in the
# output, but the test case itself will not fail.
# Also, if you need to issue the thread error earlier, before cleanup,
# then specify thread_exc as an argument on the test method and then in
# mainline issue:
#     thread_exc.raise_exc_if_one()
#
# When the above is done, cleanup will not raise the error again.
#
########################################################################
@pytest.fixture(autouse=True)
def thread_exc(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> Generator[ExcHook, None, None]:
    """Instantiate and return a ThreadExc for testing.

    Args:
        monkeypatch: pytest fixture used to modify code for testing
        request: for pytest

    Yields:
        a thread exception handler

    """
    with ExcHook(monkeypatch) as exc_hook:
        yield exc_hook


########################################################################
# dt_format_arg_list
########################################################################
dt_format_arg_list = [
    None,
    "%H:%M",
    "%H:%M:%S",
    "%m/%d %H:%M:%S",
    "%b %d %H:%M:%S",
    "%m/%d/%y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%b %d %Y %H:%M:%S",
    "%a %b %d %Y %H:%M:%S",
    "%a %b %d %H:%M:%S.%f",
    "%A %b %d %H:%M:%S.%f",
    "%A %B %d %H:%M:%S.%f",
]


@pytest.fixture(params=dt_format_arg_list)
def dt_format_arg(request: Any) -> str:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)
