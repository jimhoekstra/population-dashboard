import requests
import json
import polars as pl
from newsflash.cache import cache_result


@cache_result(60 * 60)
def load_data_from_api():
    response = requests.get(
        "https://opendata.cbs.nl/ODataApi/odata/85496NED/TypedDataSet"
    )
    response.raise_for_status()
    return json.loads(response.content)


def preprocess_year(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(pl.col("Year").str.slice(0, 4).cast(int).alias("Year"))


def get_population_growth_data(column: str) -> tuple[list[int], list[int]]:
    data = load_data_from_api()
    df = (
        pl.from_dicts(data["value"])
        .select(["Perioden", "TotaleBevolking_1", "Mannen_2", "Vrouwen_3"])
        .rename(
            {
                "Perioden": "Year",
                "TotaleBevolking_1": "Total",
                "Mannen_2": "Men",
                "Vrouwen_3": "Women",
            }
        )
    )

    df = preprocess_year(df)

    return df.get_column("Year").to_list(), df.get_column(column).to_list()


def get_age_distribution(year: int) -> tuple[list[str], list[int]]:
    data = load_data_from_api()
    df = (
        pl.from_dicts(data["value"])
        .select(
            [
                "Perioden",
                "JongerDan20Jaar_10",
                "k_20Tot40Jaar_11",
                "k_40Tot65Jaar_12",
                "k_65Tot80Jaar_13",
                "k_80JaarOfOuder_14",
            ]
        )
        .rename(
            {
                "Perioden": "Year",
                "JongerDan20Jaar_10": "<20",
                "k_20Tot40Jaar_11": "20-40",
                "k_40Tot65Jaar_12": "40-65",
                "k_65Tot80Jaar_13": "65-80",
                "k_80JaarOfOuder_14": ">80",
            }
        )
    )
    df = preprocess_year(df)
    df = df.filter(pl.col("Year") == year).drop("Year")

    as_dict = df.to_dicts()[0]
    return list(as_dict.keys()), list(as_dict.values())
