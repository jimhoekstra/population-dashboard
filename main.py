from typing import Annotated, Type
from enum import StrEnum

from newsflash import App
from newsflash.types import Layout
from newsflash.widgets import (
    Title,
    Paragraph,
    Button,
    ListSelect,
    EnumSelect,
)
from newsflash.widgets.chart.bar import BarChart
from newsflash.widgets.chart.line import LineChart
from data import get_population_growth_data, get_age_distribution
from newsflash.widgets.layout.columns import build_columns
from newsflash.widgets.layout.flex import build_rows


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
        bar_chart.set_points(labels, [float(x) for x in bars])


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


class AgeDistributionChart(BarChart):
    id: str = "age-distribution-bar-chart"
    y_major_grid_lines: bool = True

    def on_load(self, year_select: Annotated[YearSelect, "year-select"]) -> None:
        labels, bars = get_age_distribution(int(year_select.selected))
        self.title = f"Age Distribution in {year_select.selected}"
        self.set_points(labels, [float(x) for x in bars])


class PopulationGrowthChart(LineChart):
    id: str = "population-growth-line-chart"
    y_major_grid_lines: bool = True

    def on_load(self, group_select: Annotated[GroupSelect, "group-select"]) -> None:
        years, points = get_population_growth_data(group_select.selected)
        self.title = f"Population Growth ({group_select.selected})"
        self.set_points(xs=years, ys=points)


class SetYearButton(Button):
    previous: bool = False
    target: int | None = None

    def on_click(
        self,
        chart: Annotated[AgeDistributionChart, "age-distribution-bar-chart"],
        year_select: Annotated[YearSelect, "year-select", "input+output"],
    ) -> None:
        current_year = int(year_select.selected)

        if self.target:
            new_year = self.target
        else:
            if self.previous:
                new_year = current_year - 1
            else:
                new_year = current_year + 1

        year_select.selected = str(new_year)
        chart.on_load(year_select)


class SetGroupButton(Button):
    group: GroupOption

    def on_click(
        self,
        chart: Annotated[PopulationGrowthChart, "population-growth-line-chart"],
        group_select: Annotated[GroupSelect, "group-select", "output"],
    ) -> None:
        group_select.selected = self.group
        chart.on_load(group_select)


class BasicApp(App):
    def compose(self) -> Layout:
        age_distribution_text = (
            "Select a year to view the age distribution in that year. "
            "Alternatively you can use the buttons below the chart to "
            "select the previous or next year."
        )

        population_growth_text = (
            "Select a population group to view the growth in population "
            "for that group over time."
        )

        dataset_text = (
            "The data comes from the Dutch Centraal Bureau voor de Statistiek (CBS). "
            "The data is retrieved periodically through the StatLine API. The population "
            "dataset can be found [here](https://opendata.cbs.nl/portal.html?_la=nl&_catalog"
            "=CBS&tableId=85496NED&_theme=61)."
        )

        dashboard_code_text = (
            "The code that implements this dashboard is licensed under the "
            "open-source MIT license and can be found on the [GitHub page]"
            "(https://github.com/jimhoekstra/population-dashboard)."
        )

        return build_rows(
            Title(title="Dutch Population Dashboard"),
            Title(title="Age Groups", text_size="3xl"),
            Paragraph(text=age_distribution_text),
            YearSelect(),
            AgeDistributionChart(),
            build_columns(
                SetYearButton(id="prev-year-btn", text="Previous Year", previous=True),
                SetYearButton(id="next-year-btn", text="Next Year"),
                SetYearButton(id="reset-year-btn", text="Reset to 2024", target=2024),
            ),
            Title(title="Population Growth", text_size="3xl"),
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
            build_columns(
                build_rows(
                    Title(title="Data", text_size="3xl"),
                    Paragraph(text=dataset_text),
                ),
                build_rows(
                    Title(title="Code", text_size="3xl"),
                    Paragraph(text=dashboard_code_text),
                ),
            ),
        )


app = BasicApp.get_wsgi_application()


if __name__ == "__main__":
    BasicApp.run()
