from typing import Annotated, Type
from enum import StrEnum

from newsflash import App
from newsflash.types import Layout
from newsflash.widgets import (
    Title,
    SubTitle,
    SubSubTitle,
    Paragraph,
    Button,
    ListSelect,
    EnumSelect,
    Notifications,
)
from newsflash.widgets.chart.bar import BarChart
from newsflash.widgets.chart.line import LineChart
from newsflash.widgets.chart.hist import HistChart
from newsflash.widgets.layout.columns import build_columns
from newsflash.widgets.layout.flex import build_rows

from data import get_population_growth_data, get_age_distribution
from random import gauss


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
    y_major_grid_lines: bool = True

    def on_load(self, year_select: Annotated[YearSelect, "year-select"]) -> None:
        labels, bars = get_age_distribution(int(year_select.selected))
        self.title = f"Age Distribution in {year_select.selected}"
        self.set_points(labels, [float(x) for x in bars])


class NormalDistribution(HistChart):
    id: str = "hist-test"
    y_major_grid_lines: bool = True
    title: str = "Normal Distribution"

    def on_load(self) -> None:
        self.set_points([gauss(5, 2) for _ in range(10000)], 50)


class SetYearButton(Button):
    previous: bool = False
    target: int | None = None

    def get_new_year(self, current_year: int) -> int:
        if self.target:
            new_year = self.target
        else:
            if self.previous:
                new_year = current_year - 1
            else:
                new_year = current_year + 1

        return new_year

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


class PopulationDashboard(App):
    def compose(self) -> Layout:
        dashboard_explanation_text = (
            "Welcome! This dashboard presents information about the population "
            "of The Netherlands. It is a showcase for how to use the [NewsFlash]"
            "(https://github.com/jimhoekstra/newsflash) framework to build simple "
            "apps for presenting data and responding to user input in a flexible "
            "and robust way."
        )

        dashboard_code_link = (
            "Check out the code for this dashboard [on GitHub]"
            "(https://github.com/jimhoekstra/population-dashboard)."
        )

        age_distribution_text = (
            "Select a year to view the age distribution in that year in the "
            "bar chart below. Note you can also type to search and select the "
            "first search result by pressing Enter."
        )

        year_select_buttons_text = (
            "As an alternative to selecting a year in the dropdown above, "
            "press one of these buttons. Note that the result of pressing a "
            "button depends on the current value of the dropdown, and that "
            "the value in the dropdown is updated when pressing one of the "
            "buttons."
        )

        population_growth_text = (
            "Select a population group to view the growth in population "
            "for that group over time. Alternatively use the buttons below "
            "the line chart."
        )

        normal_distribution_text = (
            "I haven't yet found good data to demo the histogram functionality "
            "with, so here is a histogram of values generated from a Gaussian "
            "function with mean 5 and standard deviation 2."
        )

        dataset_text = (
            "The data comes from the Dutch Centraal Bureau voor de Statistiek (CBS). "
            "The data is retrieved periodically through the StatLine API. The population "
            "dataset can be found [here](https://opendata.cbs.nl/portal.html?_la=nl&_catalog"
            "=CBS&tableId=85496NED&_theme=61)."
        )

        dashboard_code_text = (
            "The code that implements this dashboard is licensed under the "
            "open-source MIT license and can be found on [GitHub]"
            "(https://github.com/jimhoekstra/population-dashboard)."
        )

        return build_rows(
            Title(title="Population Dashboard"),
            Paragraph(text=dashboard_explanation_text),
            Paragraph(text=dashboard_code_link),
            SubTitle(title="Age Groups"),
            Paragraph(text=age_distribution_text),
            YearSelect(),
            AgeDistributionChart(),
            Paragraph(text=year_select_buttons_text),
            build_columns(
                SetYearButton(id="prev-year-btn", text="Previous Year", previous=True),
                SetYearButton(id="next-year-btn", text="Next Year"),
                SetYearButton(id="reset-year-btn", text="Reset to 2024", target=2024),
            ),
            SubTitle(title="Population Growth"),
            Paragraph(text=population_growth_text),
            GroupSelect(),
            PopulationGrowthChart(),
            build_columns(
                SetGroupButton(
                    id="select-total", group=GroupOption.TOTAL, text=GroupOption.TOTAL
                ),
                SetGroupButton(
                    id="select-women", group=GroupOption.WOMEN, text=GroupOption.WOMEN
                ),
                SetGroupButton(
                    id="select-men", group=GroupOption.MEN, text=GroupOption.MEN
                ),
            ),
            SubTitle(title="Histogram"),
            Paragraph(text=normal_distribution_text),
            NormalDistribution(),
            Title(title="Links"),
            build_columns(
                SubSubTitle(title="Data"),
                SubSubTitle(title="Code"),
            ),
            build_columns(
                Paragraph(text=dataset_text),
                Paragraph(text=dashboard_code_text),
            ),
        )


app = PopulationDashboard.get_wsgi_application()


if __name__ == "__main__":
    PopulationDashboard.run()
