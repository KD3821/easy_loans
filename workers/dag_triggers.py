from datetime import datetime, date

import httpx
from fastapi import Response

from settings import AF_ADMIN, AF_PASS, AF_URL
from apps.transactions.models import TransactionUpload


async def analyze_report(upload: TransactionUpload):
    dag_id = "analysis"
    date = datetime.now().strftime("%H-%M-%S_%Y-%m-%d")
    analysis_id = f"{dag_id}_{upload.customer_id}-{upload.id}_{date}"

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


async def process_loan(customer_id: int, loan_id: int, start_date: date):
    dag_id = "decision"
    decision_uid = f"{dag_id}_{customer_id}-{loan_id}_{datetime.now().strftime('%H-%M-%S_%Y-%m-%d')}"
    analysis_start_date = start_date.strftime("%Y-%m-%d")

    auth = httpx.BasicAuth(username=AF_ADMIN, password=AF_PASS)
    client = httpx.AsyncClient(auth=auth)
    try:
        res = await client.post(
            url=f"{AF_URL}/dags/{dag_id}/dagRuns",
            json={
                "conf": {
                    "customer_id": customer_id,
                    "loan_id": loan_id,
                    "decision_uid": decision_uid,
                    "analysis_start_date": analysis_start_date
                },
                "dag_run_id": decision_uid
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
