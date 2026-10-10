from datetime import timedelta

import pandas as pd
import requests


BASE_URL = "https://api.raporty.pse.pl/api"


def get_pse_data(
    table: str,
    start_date: str,
    end_date: str,
    columns: list[str] | None = None,
    days_per_request: int = 31,
    timeout: int = 60,
    row_limit: int = 100_000,
    verify_ssl: bool | str = True,
) -> pd.DataFrame:
    """
    Download data from a PSE API endpoint.

    Parameters
    ----------
    table : str
        PSE API endpoint name, e.g. "csdac-pln" or "his-wlk-cal".
    start_date : str
        Start date in YYYY-MM-DD format.
    end_date : str
        End date in YYYY-MM-DD format, inclusive.
    columns : list[str] | None
        Columns to download.
        If None, all available columns are returned.
    days_per_request : int
        Number of days downloaded in a single API request.
    timeout : int
        Request timeout in seconds.
    row_limit : int
        Maximum number of rows returned by a single request.
    verify_ssl : bool | str
        SSL certificate verification or path to a CA certificate file.

    Returns
    -------
    pd.DataFrame
        Data downloaded from the PSE API.
    """

    start = pd.Timestamp(start_date).normalize()
    end = pd.Timestamp(end_date).normalize()

    if end < start:
        raise ValueError("end_date cannot be earlier than start_date.")

    if days_per_request < 1:
        raise ValueError("days_per_request must be greater than 0.")

    frames = []
    chunk_start = start

    while chunk_start <= end:

        chunk_end = min(
            chunk_start + timedelta(days=days_per_request - 1),
            end,
        )

        # PSE uses dtime as the end of the delivery period.
        next_midnight = chunk_end + timedelta(days=1)

        date_filter = (
            f"dtime gt '{chunk_start:%Y-%m-%d} 00:00:00' and "
            f"dtime le '{next_midnight:%Y-%m-%d} 00:00:00'"
        )

        params = {
            "$filter": date_filter,
            "$orderby": "dtime asc",
            "$first": row_limit,
        }

        if columns:
            params["$select"] = ",".join(columns)

        response = requests.get(
            f"{BASE_URL}/{table}",
            params=params,
            timeout=timeout,
            verify=verify_ssl,
        )

        response.raise_for_status()

        payload = response.json()
        rows = payload.get("value")

        if not isinstance(rows, list):
            raise ValueError(
                f"Unexpected response from endpoint {table!r}."
            )

        # Prevent silently truncated data.
        if len(rows) >= row_limit:
            raise RuntimeError(
                f"{table}: row limit of {row_limit} reached. "
                "Reduce days_per_request."
            )

        frames.append(pd.DataFrame.from_records(rows))

        chunk_start = chunk_end + timedelta(days=1)

    if not frames:
        return pd.DataFrame(columns=columns)

    return pd.concat(frames, ignore_index=True)