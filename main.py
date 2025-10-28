from typing import Annotated, Type
from enum import StrEnum
from random import gauss

from newsflash import App
from newsflash.widgets import (
    Button,
    ListSelect,
    EnumSelect,
    Notifications,
    BarChart,
    LineChart,
    HistChart,
)

from data import get_population_growth_data, get_age_distribution


# For now only the "/" route actually does something.
app = App(routes={"/": "index.html"})


class GroupOption(StrEnum):
    TOTAL = "Total"
    WOMEN = "Women"
    MEN = "Men"


@app.widget
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


@app.widget
class AgeDistributionChart(BarChart):
    id: str = "age-distribution-bar-chart"
    y_major_grid_lines: bool = True

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
            notifications.push(text="Not data available before 1950.")
            year_select.cancel_update()
            chart.cancel_update()

        else:
            year_select.selected = str(new_year)
            chart.on_load(year_select)


@app.widget
class NextYearButton(SetYearButton):
    id: str = "next-year-button"
    text: str = "Next Year"

    def get_new_year(self, current_year: int) -> int:
        return current_year + 1


@app.widget
class PreviousYearButton(SetYearButton):
    id: str = "previous-year-button"
    text: str = "Previous Year"

    def get_new_year(self, current_year: int) -> int:
        return current_year - 1


@app.widget
class ResetYearButton(SetYearButton):
    id: str = "reset-year-button"
    text: str = "Reset to 2024"

    def get_new_year(self, current_year: int) -> int:
        return 2024


@app.widget
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


@app.widget
class PopulationGrowthChart(LineChart):
    id: str = "population-growth-line-chart"
    y_major_grid_lines: bool = True

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


@app.widget
class TotalGroupButton(SetGroupButton):
    id: str = "total-group-button"
    text: str = "Total"
    group: GroupOption = GroupOption.TOTAL


@app.widget
class WomenGroupButton(SetGroupButton):
    id: str = "women-group-button"
    text: str = "Women"
    group: GroupOption = GroupOption.WOMEN


@app.widget
class MenGroupButton(SetGroupButton):
    id: str = "men-group-button"
    text: str = "Men"
    group: GroupOption = GroupOption.MEN


@app.widget
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


@app.widget
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


@app.widget
class NormalDistribution(HistChart):
    id: str = "normal-distribution"
    y_major_grid_lines: bool = True
    title: str = "Normal Distribution"

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


# TODO: how to expose this wsgi object in a cleaner way?
wsgi_app = app.get_wsgi_application()


if __name__ == "__main__":
    app.run()
