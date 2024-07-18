from datetime import datetime

import httpx
from fastapi import Response

from settings import AF_ADMIN, AF_PASS, AF_URL
from apps.transactions.models import TransactionUpload


async def analyze_report(upload: TransactionUpload):
    dag_id = "analysis"
    date = datetime.now().strftime("%H-%M-%S_%Y-%m-%d")
    analysis_id = f"analysis_{upload.customer_id}-{upload.id}_{date}"

    auth = httpx.BasicAuth(username=AF_ADMIN, password=AF_PASS)
    client = httpx.AsyncClient(auth=auth)
    try:
        res = await client.post(
            url=f"{AF_URL}/dags/{dag_id}/dagRuns",
            json={
                "conf": {
                    "customer_id": upload.customer_id,
                    "upload_id": upload.id,
                    "upload_start_date": upload.start_date.strftime("%Y-%m-%d"),
                    "upload_finish_date": upload.finish_date.strftime("%Y-%m-%d"),
                    "analysis_id": analysis_id
                },
                "dag_run_id": analysis_id
            },
        )
    finally:
        await client.aclose()

    try:
        res.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return Response(
            content=exc.response.content, status_code=exc.response.status_code
        )

    return res.json().get("dag_run_id")
