"""
Core functionality for tenacity error feedback.

This module provides the main function for capturing errors during retries
and passing them to subsequent retry attempts.
"""

from tenacity import RetryCallState
import logging

logger = logging.getLogger(__name__)


def retry_with_error_context(error_message_parameter_name: str):
    """
    Create a callback that captures exceptions from failed attempts and passes them to the next retry.

    This function returns a callback suitable for use with tenacity's `before_sleep` parameter.
    It captures the exception from the current failed attempt and injects it into the kwargs
    of the next retry attempt under the specified parameter name.

    Args:
        error_message_parameter_name: The parameter name under which the exception will be passed
                                      to the next retry attempt.

    Returns:
        A callback function to be used with tenacity's `before_sleep` hook.

    Example:
        @retry(stop=stop_after_attempt(3),
               before_sleep=retry_with_error_context("last_error"))
        def my_function(last_error=None):
            if last_error:
                print(f"Previous attempt failed with: {last_error}")
            # Function implementation
    """

    def _retry_with_error_context(retry_state: RetryCallState):
        exception = retry_state.outcome.exception()
        logger.debug("Captured error for next retry: %s", exception)
        retry_state.kwargs[error_message_parameter_name] = exception

    return _retry_with_error_context
