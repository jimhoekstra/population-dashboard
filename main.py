from pathlib import Path
from newsflash import App, Page

from widgets.age_groups import age_groups_widgets
from widgets.population_growth import population_growth_widgets
from widgets.histogram import histogram_widgets


root_page = Page(
    # For now only the "/" path actually does something.
    path="/",
    name="root",
    layout="index.html",
    widgets=age_groups_widgets + population_growth_widgets + histogram_widgets,
)

app = App(
    pages=[root_page],
    layout_dirs=[Path.cwd() / "layouts"],
)


if __name__ == "__main__":
    app.run()
