"""Models to support telemetry data."""

from pydantic import BaseModel


class Progress(BaseModel, validate_assignment=True):
    """Container for tracking progress for a metering instrument."""

    current: int = 0
    total: int = 0

    def increment(self, step: int = 1) -> None:
        """Increment the current progress by the given step."""
        self.current += step

    @property
    def percent_complete(self) -> float:
        """Return the percent complete as a float between 0 and 100."""
        if self.total > 0:
            return (self.current / self.total) * 100
        return 0.0
