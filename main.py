from typing import Annotated, Type
from enum import StrEnum

from newsflash import App
from newsflash.types import Layout
from newsflash.widgets import (
    Columns,
    FlexRows,
    Rows,
    Title,
    Paragraph,
    Button,
    Notifications,
    EnumSelect,
    ListSelect,
    Space,
)
from newsflash.widgets.chart.bar import BarChart
from newsflash.widgets.chart.line import LineChart

from data import get_population_growth_data, get_age_distribution


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
        year, population = get_population_growth_data(self.selected)
        line_chart.title = f"Population ({self.selected}) Over Time"
        line_chart.set_points(year, population)


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
        bar_chart.set_bars(labels, bars)


class GroupResetBtn(Button):
    id: str = "reset-group"
    text: str = "Reset Inputs"

    def on_click(
        self,
        group_select: Annotated[GroupSelect, "group-select", "input+output"],
        year_select: Annotated[YearSelect, "year-select", "input+output"],
        line_chart: Annotated["PopulationGrowthChart", "population-growth-line-chart"],
        bar_chart: Annotated["AgeDistributionChart", "age-distribution-bar-chart"],
        notifications: Annotated[Notifications, "notifications"],
    ) -> None:
        current_group = group_select.selected
        current_year = year_select.selected
        notification = ""

        if current_group != GroupOption.TOTAL:
            group_select.selected = GroupOption.TOTAL
            group_select.on_input(line_chart)
            notification += f"Resetting group (was {current_group}). "
        else:
            group_select.cancel_update()
            line_chart.cancel_update()

        if current_year != "2024":
            year_select.selected = "2024"
            year_select.on_input(bar_chart)
            notification += f"Resetting year (was {current_year}). "
        else:
            year_select.cancel_update()
            bar_chart.cancel_update()

        if notification == "":
            notifications.push("Nothing to reset.", 5000)
        else:
            notifications.push(notification, 5000)


class PreviousYearBtn(Button):
    id: str = "previous-year-btn"
    text: str = "Previous Year"

    def on_click(
        self,
        year_select: Annotated[YearSelect, "year-select", "input+output"],
        bar_chart: Annotated["AgeDistributionChart", "age-distribution-bar-chart"],
    ) -> None:
        current_year = int(year_select.selected)
        year_select.selected = str(current_year - 1)
        year_select.on_input(bar_chart)


class NextYearBtn(Button):
    id: str = "next-year-btn"
    text: str = "Next Year"

    def on_click(
        self,
        year_select: Annotated[YearSelect, "year-select", "input+output"],
        bar_chart: Annotated["AgeDistributionChart", "age-distribution-bar-chart"],
    ) -> None:
        current_year = int(year_select.selected)
        year_select.selected = str(current_year + 1)
        year_select.on_input(bar_chart)


class NotificationBtn(Button):
    id: str = "notification-btn"
    text: str = "Press Me!"

    def on_click(
        self,
        notifications: Annotated[Notifications, "notifications"],
        choice: Annotated[GroupSelect, "group-select"],
    ) -> None:
        notifications.push(f"You selected: {choice.selected}", 5000)


class AgeDistributionChart(BarChart):
    id: str = "age-distribution-bar-chart"
    title: str = "Bar Chart"
    y_major_grid_lines: bool = True

    def on_load(self, year_select: Annotated[YearSelect, "year-select"]) -> None:
        labels, bars = get_age_distribution(int(year_select.selected))
        self.title = f"Age Distribution in {year_select.selected}"
        self.set_bars(labels, bars)


class PopulationGrowthChart(LineChart):
    id: str = "population-growth-line-chart"
    title: str = "Line Chart"
    y_major_grid_lines: bool = True
    x_major_grid_lines: bool = True

    def on_load(self, group_select: Annotated[GroupSelect, "group-select"]) -> None:
        year, population = get_population_growth_data(group_select.selected)
        self.title = f"Population ({group_select.selected}) Over Time"
        self.set_points(year, population)


class BasicApp(App):
    def compose(self) -> Layout:
        group_select_text = (
            "Select a population in the following dropdown menu "
            "to view the population growth over time for this specific group."
        )
        year_select_text = (
            "Select a population in the following dropdown menu to view the age "
            "distribution in this specific year."
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

        charts_column = Rows(
            children=[
                PopulationGrowthChart(),
                AgeDistributionChart(),
            ]
        )

        title_row = Title(title="Dutch Population Dashboard")
        explanations_row = Columns(
            children=[
                Paragraph(text=group_select_text),
                Paragraph(text=year_select_text),
            ]
        )

        group_input_block = FlexRows(children=[GroupSelect(), GroupResetBtn()])
        year_input_block = FlexRows(
            children=[
                YearSelect(),
                Columns(children=[PreviousYearBtn(), NextYearBtn()]),
            ]
        )
        inputs_row = Columns(children=[group_input_block, year_input_block])

        dataset_col = FlexRows(
            children=[
                Title(title="Data", text_size="2xl"),
                Paragraph(text=dataset_text),
            ]
        )
        code_col = FlexRows(
            children=[
                Title(title="Code", text_size="2xl"),
                Paragraph(text=dashboard_code_text),
            ]
        )
        acknowledgements_row = Columns(children=[dataset_col, code_col])

        right_column = FlexRows(
            children=[
                title_row,
                explanations_row,
                inputs_row,
                Space(),
                acknowledgements_row,
            ]
        )

        return Columns(children=[charts_column, right_column])


app = BasicApp.get_wsgi_application()


if __name__ == "__main__":
    BasicApp.run()
