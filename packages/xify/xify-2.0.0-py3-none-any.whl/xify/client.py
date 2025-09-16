import logging
import types

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Xify:
    """An asynchronous Python client for interacting with the X API."""

    def __init__(self) -> None:
        """Initialize the Xify instance."""
        logger.info("Xify instance has been initialized.")

    async def __aenter__(self) -> "Xify":
        """Enter async context and intialize resources.

        Returns:
            The initialized Xify instance.
        """
        logger.debug("Xify context entered.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit async context and close resources."""
        logger.debug("Xify context exited.")
