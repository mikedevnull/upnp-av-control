try:
    from typing import Protocol, Literal  # noqa
except ImportError:
    # Running on pre-3.8 Python; use typing_extensions package
    from typing_extensions import Protocol, Literal  # noqa
