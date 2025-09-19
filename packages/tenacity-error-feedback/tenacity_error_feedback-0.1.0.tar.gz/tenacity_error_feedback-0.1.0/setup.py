"""
Setup script for backward compatibility.
For modern Python installations, use pyproject.toml instead.
"""

from setuptools import setup

setup(
    name="tenacity-error-feedback",
    version="0.1.0",
    description="Propagate error context between tenacity retry attempts",
    packages=["tenacity_error_feedback"],
    install_requires=[
        "tenacity>=8.0.0",
    ],
)
