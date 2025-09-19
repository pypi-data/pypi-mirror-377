"""test_msgs.py module."""

########################################################################
# Standard Library
########################################################################
import logging
import os
import re
import threading
from typing import Any, cast, Optional, Union

########################################################################
# Third Party
########################################################################
import pytest

########################################################################
# Local
########################################################################
from scottbrian_utils.log_verifier import LogVer
from scottbrian_utils.msgs import Msgs, GetMsgTimedOut
from scottbrian_utils.testlib_verifier import verify_lib
from scottbrian_utils.stop_watch import StopWatch


########################################################################
# type aliases
########################################################################
IntFloat = Union[int, float]
OptIntFloat = Optional[IntFloat]

########################################################################
# Set up logging
########################################################################
logger = logging.getLogger("test_msgs")
logger.debug("about to start the tests")


########################################################################
# Msgs test exceptions
########################################################################
class ErrorTstMsgs(Exception):
    """Base class for exception in this module."""

    pass


########################################################################
# who_arg fixture
########################################################################
who_arg_list = ["beta", "charlie", "both"]


@pytest.fixture(params=who_arg_list)
def who_arg(request: Any) -> str:
    """Using different msg targets.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


#######################################################################
# msg_arg fixture
########################################################################
msg_arg_list = [0, "0", 0.0, "hello", 1, [1, 2, 3], ("a", "b", "c")]


@pytest.fixture(params=msg_arg_list)
def msg_arg(request: Any) -> Any:
    """Using different msgs.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return request.param


#######################################################################
# start_arg fixture
########################################################################
start_arg_list = ["before", "mid1", "mid2", "after"]


@pytest.fixture(params=start_arg_list)
def start_arg(request: Any) -> str:
    """Using different remote thread start points.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


########################################################################
# TestMsgsCorrectSource
########################################################################
class TestMsgsCorrectSource:
    """Verify that we are testing with correctly built code."""

    ####################################################################
    # test_msgs_correct_source
    ####################################################################
    def test_msgs_correct_source(self) -> None:
        """Test msgs correct source."""
        if "TOX_ENV_NAME" in os.environ:
            verify_lib(obj_to_check=Msgs)


########################################################################
# TestMsgsErrors class
########################################################################
class TestMsgsErrors:
    """TestMsgsErrors class."""

    @pytest.mark.parametrize("timeout_arg", [0.0, 0.3, 0.5, 1, 2, 4])
    @pytest.mark.cover
    def test_msgs_timeout(
        self, timeout_arg: float, caplog: pytest.LogCaptureFixture
    ) -> None:
        """test_msgs_timeout.

        Args:
            timeout_arg: number of seconds to use for timeout value
                           on get_msg request
            caplog: pytest fixture to capture log output

        """

        ################################################################
        # log_test_msg
        ################################################################
        def log_test_msg(log_ver: LogVer, log_msg: str) -> None:
            """Issue log msgs for test rtn.

            Args:
                log_ver: instance of LogVer
                log_msg: the message to log

            """
            log_ver.add_pattern(pattern=re.escape(log_msg))
            logger.debug(log_msg, stacklevel=2)

        ################################################################
        # f1
        ################################################################
        def f1() -> None:
            """Beta f1 function."""
            log_test_msg(log_ver, "f1 beta entered")

            f1_to_low = f1_timeout * 0.9
            f1_to_high = f1_timeout * 1.1

            f1_stop_watch = StopWatch()

            log_test_msg(log_ver, "f1 beta starting timeout -1")

            f1_stop_watch.start_clock(clock_iter=1)
            msgs.get_msg("beta", timeout=-1)
            assert f1_to_low <= f1_stop_watch.duration() <= f1_to_high

            log_test_msg(log_ver, "f1 beta starting timeout 0")

            f1_stop_watch.start_clock(clock_iter=2)
            msgs.get_msg("beta", timeout=0)
            assert f1_to_low <= f1_stop_watch.duration() <= f1_to_high

            log_test_msg(log_ver, "f1 beta starting timeout None")

            f1_stop_watch.start_clock(clock_iter=3)
            msgs.get_msg("beta", timeout=None)
            assert f1_to_low <= f1_stop_watch.duration() <= f1_to_high

            log_test_msg(log_ver, "f1 beta exiting")

        ################################################################
        # mainline
        ################################################################
        msgs = Msgs()
        ml_stop_watch = StopWatch()
        log_ver = LogVer(log_name="test_msgs")
        alpha_call_seq = "test_msgs.py::TestMsgsErrors.test_msgs_timeout"
        log_ver.add_call_seq(name="alpha", seq=alpha_call_seq)

        log_test_msg(log_ver, "mainline entered")

        f1_timeout = 5
        f1_thread = threading.Thread(target=f1)

        # we expect to get this log message in the following code
        thread_info = re.escape(f"{threading.current_thread()}")
        log_msg = (
            f"Thread {thread_info} "
            f"timed out on get_msg for recipient: beta "
            f'{log_ver.get_call_seq("alpha")}'
        )
        log_ver.add_pattern(
            log_name="scottbrian_utils.msgs", level=logging.DEBUG, pattern=log_msg
        )

        # we will try -1 as a timeout value in the section below, and
        # we also use the -1 value to do the default value
        if timeout_arg == 0.0:  # if do default timeout
            ############################################################
            # get_msg timeout with default
            ############################################################
            to_low = Msgs.GET_CMD_TIMEOUT
            to_high = Msgs.GET_CMD_TIMEOUT * 1.1
            ml_stop_watch.start_clock(clock_iter=1)

            with pytest.raises(GetMsgTimedOut):
                _ = msgs.get_msg("beta")
            assert to_low <= ml_stop_watch.duration() <= to_high

            f1_thread.start()
            log_test_msg(log_ver, "mainline starting timeout loop")

            for idx in range(2, 5):  # 2, 3, 4
                log_test_msg(log_ver, f"mainline starting timeout loop {idx}")

                ml_stop_watch.start_clock(clock_iter=idx)
                ml_stop_watch.pause(seconds=f1_timeout, clock_iter=idx)
                log_test_msg(log_ver, f"mainline duration {ml_stop_watch.duration()}")

                msgs.queue_msg("beta")
            f1_thread.join()
        else:
            ############################################################
            # get_msg timeout with timeout_arg
            ############################################################
            to_low = timeout_arg
            to_high = timeout_arg * 1.2
            log_test_msg(log_ver, f"mainline starting timeout {timeout_arg}")

            ml_stop_watch.start_clock(clock_iter=1)
            with pytest.raises(GetMsgTimedOut):
                _ = msgs.get_msg("beta", timeout_arg)
            assert to_low <= ml_stop_watch.duration() <= to_high

        match_results = log_ver.get_match_results(caplog=caplog)
        log_ver.print_match_results(match_results, print_matched=True)
        log_ver.verify_match_results(match_results)

        logger.debug("mainline exiting")


########################################################################
# TestMsgsExamples class
########################################################################
class TestMsgsExamples:
    """Test examples of Msgs."""

    ####################################################################
    # test_msgs_example1
    ####################################################################
    def test_msgs_example1(self, capsys: Any) -> None:
        """Test msgs example1.

        Args:
            capsys: pytest fixture to capture print output

        """

        def f1() -> None:
            """Beta f1 function."""
            print("f1 beta entered")
            my_msg = msgs.get_msg("beta")
            print(my_msg)
            print("f1 beta exiting")

        print("mainline entered")
        msgs = Msgs()
        f1_thread = threading.Thread(target=f1)
        f1_thread.start()
        msgs.queue_msg("beta", "hello beta")
        f1_thread.join()
        print("mainline exiting")

        expected_result = "mainline entered\n"
        expected_result += "f1 beta entered\n"
        expected_result += "hello beta\n"
        expected_result += "f1 beta exiting\n"
        expected_result += "mainline exiting\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_msgs_example2
    ####################################################################
    def test_msgs_example2(self, capsys: Any) -> None:
        """Test msgs example2.

        Args:
            capsys: pytest fixture to capture print output

        """

        def f1() -> None:
            """Beta f1 function."""
            print("f1 beta entered")
            while True:
                my_msg = msgs.get_msg("beta")
                if my_msg == "exit":
                    break
                else:
                    # handle command
                    print(f"beta received cmd: {my_msg}")
                    msgs.queue_msg("alpha", f'cmd "{my_msg}" completed')
            print("f1 beta exiting")

        print("mainline alpha entered")
        msgs = Msgs()
        f1_thread = threading.Thread(target=f1)
        f1_thread.start()
        msgs.queue_msg("beta", "do command a")
        print(msgs.get_msg("alpha"))
        msgs.queue_msg("beta", "do command b")
        print(f"alpha received response: {msgs.get_msg('alpha')}")
        msgs.queue_msg("beta", "exit")
        f1_thread.join()
        print("mainline alpha exiting")

        expected_result = "mainline alpha entered"
        expected_result += "f1 beta entered"
        expected_result += "beta received cmd: do command a"
        expected_result += "alpha received response: " 'cmd "do command a" completed'
        expected_result += "beta received cmd: do command b"
        expected_result += "alpha received response: " 'cmd "do command b" completed'
        expected_result += "f1 beta exiting"
        expected_result += "mainline alpha exiting"


########################################################################
# TestMsgsMsgs class
########################################################################
class TestMsgsMsgs:
    """Test queue_msg and get_msg methods of Msgs."""

    ####################################################################
    # test_msgs_example1
    ####################################################################
    def test_msgs_msgs1(self, who_arg: str, msg_arg: Any, start_arg: str) -> None:
        """Test msgs queue_msg and get_msg methods.

        Args:
            who_arg: who to send msg to
            msg_arg: what to send
            start_arg: when to start the remote thread

        """

        def f1() -> None:
            """Beta f1 function."""
            logger.debug("f1 beta entered")
            f1_event.set()
            assert msgs.get_msg("beta") == "go"
            while True:
                my_msg = msgs.get_msg("beta")
                if my_msg == "exit now":
                    break
                else:
                    assert my_msg == msg_arg
            logger.debug("f1 beta exiting")

        def f2() -> None:
            """Charlie f2 function."""
            logger.debug("f2 charlie entered")
            f2_event.set()
            msgs.queue_msg("alpha", "charlie ready")
            assert msgs.get_msg("charlie") == "go"
            while True:
                my_msg = msgs.get_msg("charlie")
                if my_msg == "exit now":
                    break
                else:
                    assert my_msg == msg_arg

            logger.debug("f2 charlie exiting")

        logger.debug("mainline entered")
        msgs = Msgs()
        f1_event = threading.Event()
        f2_event = threading.Event()

        if who_arg == "beta" or who_arg == "both":
            f1_thread = threading.Thread(target=f1)
            if start_arg == "before":
                logger.debug("mainline starting beta before")
                f1_thread.start()
                f1_event.wait()
            msgs.queue_msg("beta")  # no arg, default is 'go'
            if start_arg == "mid1":
                logger.debug("mainline starting beta mid1")
                f1_thread.start()
                f1_event.wait()
            msgs.queue_msg("beta", msg_arg)
            if start_arg == "mid2":
                logger.debug("mainline starting beta mid2")
                f1_thread.start()
                f1_event.wait()
            if who_arg == "beta":
                msgs.queue_msg(who_arg, "exit now")
            else:
                msgs.queue_msg("beta", "exit now")
            if start_arg == "after":
                logger.debug("mainline starting beta after")
                f1_thread.start()
                f1_event.wait()
            logger.debug("mainline about to join f1 beta")
            f1_thread.join()

        if who_arg == "charlie" or who_arg == "both":
            logger.debug("mainline starting charlie")
            f2_thread = threading.Thread(target=f2)
            if start_arg == "before":
                logger.debug("mainline starting charlie before")
                f2_thread.start()
                f2_event.wait()
            msgs.queue_msg("charlie")  # no arg, default is 'go'
            if start_arg == "mid1":
                logger.debug("mainline starting charlie mid1")
                f2_thread.start()
                f2_event.wait()
            msgs.queue_msg("charlie", msg_arg)
            if start_arg == "mid2":
                logger.debug("mainline starting charlie mid2")
                f2_thread.start()
                f2_event.wait()
            if who_arg == "charlie":
                msgs.queue_msg(who_arg, "exit now")
            else:
                msgs.queue_msg("charlie", "exit now")
            logger.debug("mainline about to join f2 charlie")
            if start_arg == "after":
                logger.debug("mainline starting charlie after")
                f2_thread.start()
                f2_event.wait()
            f2_thread.join()

        logger.debug("mainline exiting")
