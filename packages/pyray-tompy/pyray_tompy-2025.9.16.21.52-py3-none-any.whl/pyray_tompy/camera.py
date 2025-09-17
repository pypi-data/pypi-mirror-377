from decimal import Decimal

from .window import get_window_aspect_ratio


class FOVY:
    def __init__(self, minimum_vertical_units: float, minimum_horizontal_units: float) -> None:
        self._minimum_vertical_units: float = minimum_vertical_units
        self._minimum_horizontal_units: float = minimum_horizontal_units

    def update(self) -> float:
        # Correct fovy for window aspect ratio
        window_aspect_ratio: Decimal = get_window_aspect_ratio()
        vertical_fovy: float = self._minimum_vertical_units
        horizontal_fovy: float = self._minimum_horizontal_units / float(window_aspect_ratio)
        greatest_fovy: float = max(vertical_fovy, horizontal_fovy)
        return greatest_fovy
