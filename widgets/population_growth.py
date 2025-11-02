from typing import Annotated, Type
from enum import StrEnum

from newsflash.widgets.base import Widget
from newsflash.widgets import (
    Button,
    EnumSelect,
    LineChart,
)

from data import get_population_growth_data


class GroupOption(StrEnum):
    TOTAL = "Total"
    WOMEN = "Women"
    MEN = "Men"


class GroupSelect(EnumSelect):
    id: str = "group-select"
    options: Type[StrEnum] = GroupOption
    selected: GroupOption = GroupOption.TOTAL

    def on_input(
        self,
        line_chart: Annotated["PopulationGrowthChart", "population-growth-line-chart"],
    ) -> None:
        years, points = get_population_growth_data(self.selected)
        line_chart.title = f"Population Growth ({self.selected})"
        line_chart.set_points(xs=years, ys=points)


class PopulationGrowthChart(LineChart):
    id: str = "population-growth-line-chart"
    x_axis_description: str = "Years"

    def on_load(self, group_select: Annotated[GroupSelect, "group-select"]) -> None:
        years, points = get_population_growth_data(group_select.selected)
        self.title = f"Population Growth ({group_select.selected})"
        self.set_points(xs=years, ys=points)


class SetGroupButton(Button):
    group: GroupOption

    def on_click(
        self,
        chart: Annotated[PopulationGrowthChart, "population-growth-line-chart"],
        group_select: Annotated[GroupSelect, "group-select", "input+output"],
    ) -> None:
        group_select.selected = self.group
        chart.on_load(group_select)


class TotalGroupButton(SetGroupButton):
    id: str = "total-group-button"
    text: str = "Total"
    group: GroupOption = GroupOption.TOTAL


class WomenGroupButton(SetGroupButton):
    id: str = "women-group-button"
    text: str = "Women"
    group: GroupOption = GroupOption.WOMEN


class MenGroupButton(SetGroupButton):
    id: str = "men-group-button"
    text: str = "Men"
    group: GroupOption = GroupOption.MEN


population_growth_widgets: list[Type[Widget]] = [
    GroupSelect,
    PopulationGrowthChart,
    TotalGroupButton,
    WomenGroupButton,
    MenGroupButton,
]
