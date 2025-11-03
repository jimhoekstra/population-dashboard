from typing import Annotated, Type
from random import gauss

from newsflash.widgets.base import Widget
from newsflash.widgets import (
    ListSelect,
    HistChart,
)


class MeanSelect(ListSelect):
    id: str = "mean-select"
    options: list[str] = ["0", "5", "20", "-1000", "3921.4"]
    selected: str = "0"

    def on_input(
        self,
        hist: Annotated["NormalDistribution", "normal-distribution"],
        standard_deviation_select: Annotated[
            "StandardDeviationSelect", "standard-deviation-select"
        ],
    ) -> None:
        hist.on_load(self, standard_deviation_select)


class StandardDeviationSelect(ListSelect):
    id: str = "standard-deviation-select"
    options: list[str] = ["2", "30", "4000"]
    selected: str = "2"

    def on_input(
        self,
        hist: Annotated["NormalDistribution", "normal-distribution"],
        mean_select: Annotated[MeanSelect, "mean-select"],
    ) -> None:
        hist.on_load(mean_select, self)


class NormalDistribution(HistChart):
    id: str = "normal-distribution"
    y_major_grid_lines: bool = True
    title: str = "Normal Distribution"
    x_axis_label: str = "Value"
    y_axis_label: str = "Occurrence"

    def on_load(
        self,
        mean_select: Annotated[MeanSelect, "mean-select"],
        standard_deviation_select: Annotated[
            StandardDeviationSelect, "standard-deviation-select"
        ],
    ) -> None:
        mean = float(mean_select.selected)
        standard_deviation = float(standard_deviation_select.selected)
        self.title = f"Normal (mean={mean_select.selected}, std={standard_deviation_select.selected})"
        self.set_points([gauss(mean, standard_deviation) for _ in range(10000)], 50)


histogram_widgets: list[Type[Widget]] = [
    MeanSelect,
    StandardDeviationSelect,
    NormalDistribution,
]
