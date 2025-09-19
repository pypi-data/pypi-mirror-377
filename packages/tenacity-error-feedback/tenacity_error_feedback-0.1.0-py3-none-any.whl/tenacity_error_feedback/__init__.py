"""
Tenacity Error Feedback - Error context propagation for tenacity retries.

This package provides utilities to pass error information between retry attempts in tenacity.
"""

from tenacity_error_feedback.core import retry_with_error_context

__all__ = ["retry_with_error_context"]
