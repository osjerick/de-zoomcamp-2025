#!/usr/bin/env python

import os
import shutil
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

import dlt
from dlt.common.storages.fsspec_filesystem import MTIME_DISPATCH, FileItem, FileItemDict
from dlt.destinations import filesystem
from dlt.sources.filesystem import read_parquet
from fsspec.core import url_to_fs

BUCKET_NAME = os.environ.get("BUCKET_NAME")
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-"
MONTHS = [f"{i:02d}" for i in range(1, 7)]


def download_file(month: str, *, dir: Path) -> Path | None:
    url = f"{BASE_URL}{month}.parquet"
    file_path = dir / f"yellow_tripdata_2024-{month}.parquet"

    try:
        print(f"Downloading {url}...")

        with urlopen(url) as response, file_path.open("wb") as file:
            shutil.copyfileobj(response, file)

        print(f"Downloaded: {file_path}")

        return file_path
    except Exception as e:
        print(f"Failed to download {url}: {e}")

    return None


@dlt.resource
def data_files(months: list[str], download_dir: Path) -> Iterator[list[FileItemDict]]:
    fs_client = url_to_fs(download_dir.as_uri())[0]

    for month in months:
        path = download_file(month, dir=download_dir)

        if path:
            metadata = fs_client.info(path.as_posix())

            yield [
                FileItemDict(
                    FileItem(
                        file_name=path.name,
                        relative_path=path.relative_to(download_dir).as_posix(),
                        file_url=path.as_uri(),
                        mime_type="application/parquet",
                        encoding=None,
                        modification_date=MTIME_DISPATCH["file"](metadata),
                        size_in_bytes=int(metadata["size"]),
                    ),
                    fs_client,
                )
            ]


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="file_to_gcs",
        dataset_name="ny_taxi",
        destination=filesystem(bucket_url=f"gs://{BUCKET_NAME}"),
        progress="alive_progress",
    )

    with TemporaryDirectory(dir=".") as td:
        download_dir = Path(td)
        files = (
            data_files(months=MONTHS, download_dir=download_dir) | read_parquet()
        ).with_name("yellow_taxi_data")

        print("Running pipeline...")

        load_info = pipeline.run(
            files, write_disposition="replace", loader_file_format="parquet"
        )
        print(load_info)

        print("Done!")
