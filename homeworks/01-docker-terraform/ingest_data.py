#! /usr/bin/env python

import argparse
import pandas as pd
import subprocess
import time

from sqlalchemy import create_engine


def main(args: argparse.Namespace) -> None:
    if args.url.endswith(".csv.gz"):
        csv_name = f"output-{args.data_kind}.csv.gz"
    else:
        csv_name = f"output-{args.data_kind}.csv"

    return_code = subprocess.call(["wget", "-O", csv_name, args.url])

    if return_code != 0:
        print("Error downloading the file!")
        return

    engine = create_engine(
        f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.db}"
    )
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100_000)

    for i, df in enumerate(df_iter, start=1):
        if args.data_kind == "taxi":
            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        if i == 1:
            df.head(n=0).to_sql(name=args.table_name, con=engine, if_exists="replace")

        start = time.perf_counter()
        df.to_sql(name=args.table_name, con=engine, if_exists="append")
        print(f"Inserted chunk {i:03}; took {time.perf_counter() - start:.3f} seconds")

    print("Finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--table_name", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--data-kind", required=True, choices=["taxi", "zones"])

    main(parser.parse_args())
