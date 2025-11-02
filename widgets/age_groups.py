from typing import Annotated, Type
from enum import StrEnum

from newsflash.widgets.base import Widget
from newsflash.widgets import (
    ListSelect,
    BarChart,
    Button,
    Notifications,
)

from data import get_age_distribution


class GroupOption(StrEnum):
    TOTAL = "Total"
    WOMEN = "Women"
    MEN = "Men"


class YearSelect(ListSelect):
    id: str = "year-select"
    options: list[str] = [str(year) for year in range(1950, 2025)]
    selected: str = "2024"

    def on_input(
        self,
        bar_chart: Annotated["AgeDistributionChart", "age-distribution-bar-chart"],
    ) -> None:
        labels, bars = get_age_distribution(int(self.selected))
        bar_chart.title = f"Age Distribution in {self.selected}"
        bar_chart.set_points(labels, bars)


class AgeDistributionChart(BarChart):
    id: str = "age-distribution-bar-chart"
    x_axis_description: str = "Age Groups"

    def on_load(self, year_select: Annotated[YearSelect, "year-select"]) -> None:
        labels, bars = get_age_distribution(int(year_select.selected))
        self.title = f"Age Distribution in {year_select.selected}"
        self.set_points(labels, [float(x) for x in bars])


class SetYearButton(Button):
    def get_new_year(self, current_year: int) -> int: ...

    def on_click(
        self,
        chart: Annotated[AgeDistributionChart, "age-distribution-bar-chart"],
        year_select: Annotated[YearSelect, "year-select", "input+output"],
        notifications: Annotated[Notifications, "notifications"],
    ) -> None:
        current_year = int(year_select.selected)
        new_year = self.get_new_year(current_year)

        if new_year > 2024:
            notifications.push(text="No data available after 2024.")
            year_select.cancel_update()
            chart.cancel_update()

        elif new_year < 1950:
            notifications.push(text="No data available before 1950.")
            year_select.cancel_update()
            chart.cancel_update()

        else:
            year_select.selected = str(new_year)
            chart.on_load(year_select)


class NextYearButton(SetYearButton):
    id: str = "next-year-button"
    text: str = "Next Year"

    def get_new_year(self, current_year: int) -> int:
        return current_year + 1


class PreviousYearButton(SetYearButton):
    id: str = "previous-year-button"
    text: str = "Previous Year"

    def get_new_year(self, current_year: int) -> int:
        return current_year - 1


class ResetYearButton(SetYearButton):
    id: str = "reset-year-button"
    text: str = "Reset to 2024"

    def get_new_year(self, current_year: int) -> int:
        return 2024


age_groups_widgets: list[Type[Widget]] = [
    YearSelect,
    AgeDistributionChart,
    NextYearButton,
    PreviousYearButton,
    ResetYearButton,
]
