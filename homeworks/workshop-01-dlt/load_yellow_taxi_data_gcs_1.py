#!/usr/bin/env python

import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

import dlt
from dlt.destinations import filesystem as dest_fs
from dlt.sources.filesystem import filesystem as src_fs
from dlt.sources.filesystem import read_parquet

BUCKET_NAME = os.environ.get("BUCKET_NAME")
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-"
MONTHS = [f"{i:02d}" for i in range(1, 7)]


def download_file(month: str, *, dir: Path) -> None:
    url = f"{BASE_URL}{month}.parquet"
    file_path = dir / f"yellow_tripdata_2024-{month}.parquet"

    try:
        print(f"Downloading {url}...")

        with urlopen(url) as response, file_path.open("wb") as file:
            shutil.copyfileobj(response, file)

        print(f"Downloaded: {file_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")


def download_yellow_taxi_data(months: list[str], download_dir: Path) -> None:
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(partial(download_file, dir=download_dir), months))


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="file_to_gcs",
        dataset_name="ny_taxi",
        destination=dest_fs(bucket_url=f"gs://{BUCKET_NAME}"),
        progress="alive_progress",
    )

    with TemporaryDirectory(dir=".") as td:
        download_dir = Path(td)
        download_yellow_taxi_data(MONTHS, download_dir)
        files = (
            src_fs(bucket_url=download_dir.as_uri(), file_glob="*.parquet")
            | read_parquet()
        ).with_name("yellow_taxi_data")

        print("Running pipeline...")

        load_info = pipeline.run(
            files, write_disposition="replace", loader_file_format="parquet"
        )
        print(load_info)

        print("Done!")
