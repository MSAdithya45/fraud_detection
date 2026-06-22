import io
import json
import zipfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, Response

import pandas as pd

from sqlalchemy import text, inspect

from database.transactions import engine, read_processed


router = APIRouter()


@router.get("/transactions")
def get_transactions():

    df = read_processed(
        '"TransactionID", probability, label, prediction',
        order='ORDER BY "TransactionID" DESC',
    )

    return df.to_dict(
        orient="records"
    )


@router.get("/shap")
def get_all_shap():

    query = text("""

        SELECT

            transaction_id,

            feature,

            impact,

            absolute_impact
                 

        FROM developer_explanations

        ORDER BY transaction_id DESC

    """)

    df = pd.read_sql(

        query,

        engine
    )

    return df.to_dict(
        orient="records"
    )


@router.get("/transaction/{transaction_id}")
def get_transaction(
    transaction_id: int
):

    df = read_processed(
        '"TransactionID", probability, label, prediction',
        where='WHERE "TransactionID" = :tid',
        params={"tid": transaction_id},
    )

    if df.empty:

        return {
            "error":
            "Transaction not found"
        }

    return df.to_dict(
        orient="records"
    )[0]



@router.get("/shap/{transaction_id}")
def get_transaction_shap(
    transaction_id: int
):

    query = text("""

        SELECT

            feature,

            impact,

            absolute_impact

        FROM developer_explanations

        WHERE transaction_id = :transaction_id

        ORDER BY absolute_impact DESC

    """)

    df = pd.read_sql(

        query,

        engine,

        params={
            "transaction_id":
            transaction_id
        }
    )

    if df.empty:

        return {
            "error":
            "No SHAP explanation found"
        }

    return {

        "transaction_id":
        transaction_id,

        "shap":
        df.to_dict(
            orient="records"
        )
    }




from src.llm.explanation_service import (
    explain_transaction
)


@router.get(
    "/llm/{transaction_id}"
)
def get_llm_explanation(
    transaction_id: int
):

    explanation = explain_transaction(
        transaction_id
    )

    return explanation



from src.api.pipeline_loader import pipeline
from src.model_pipeline.pipeline import DRIFT_BATCH_SIZE


def _staging_count():
    """Current number of buffered processed transactions (0 if table absent)."""
    try:
        if not inspect(engine).has_table("processed_transactions_staging"):
            return 0
        with engine.connect() as conn:
            return conn.execute(
                text('SELECT COUNT(*) FROM processed_transactions_staging')
            ).scalar() or 0
    except Exception:
        return 0


@router.post("/predict")
def predict_csv(
    file: UploadFile = File(...)
):
    """Score a CSV and STREAM one NDJSON line per transaction as it
    finishes, then a final 'done' line. Streaming avoids request timeouts
    on large/slow batches and lets the UI show live progress.
    """

    df = pd.read_csv(file.file)

    total = len(df)

    has_id = "TransactionID" in df.columns

    def generate():

        yield json.dumps({"type": "start", "total": total}) + "\n"

        for idx in range(total):

            row = df.iloc[[idx]]

            try:
                transaction_id = (
                    int(row["TransactionID"].iloc[0]) if has_id else None
                )
            except Exception:
                transaction_id = None

            # Will THIS row push the buffer to the drift threshold?
            triggers_drift = (_staging_count() + 1) >= DRIFT_BATCH_SIZE

            if triggers_drift:
                yield json.dumps({
                    "type": "drift",
                    "status": "start",
                    "index": idx + 1,
                    "message": f"Drift limit ({DRIFT_BATCH_SIZE}) reached — running drift analysis…",
                }) + "\n"

            try:

                result = pipeline.predict(row)

                first = (
                    result[0]
                    if isinstance(result, list) and result
                    else {}
                )

                yield json.dumps({
                    "type": "progress",
                    "index": idx + 1,
                    "total": total,
                    "transaction_id": transaction_id,
                    "prediction": first.get("prediction"),
                    "probability": first.get("probability"),
                    "label": first.get("label"),
                }) + "\n"

            except Exception as exc:

                yield json.dumps({
                    "type": "error",
                    "index": idx + 1,
                    "total": total,
                    "transaction_id": transaction_id,
                    "message": str(exc),
                }) + "\n"

            if triggers_drift:
                yield json.dumps({
                    "type": "drift",
                    "status": "done",
                    "index": idx + 1,
                    "message": "Drift analysis complete.",
                }) + "\n"

        yield json.dumps({
            "type": "done",
            "total": total,
            "message": "All transactions processed. You can now check your dashboard.",
        }) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
    )


# ============================================================
# DRIFT ANALYSIS  +  HISTORY EXPORTS
# ============================================================

_DRIFT_TABLES = {
    "low": "drift_low_severity",
    "medium": "drift_medium_severity",
    "high": "drift_high_severity",
}


def _csv_download(table, filename):
    """Stream an entire table as a CSV file download (empty CSV if absent)."""
    if not inspect(engine).has_table(table):
        body = ""
    else:
        df = pd.read_sql(f'SELECT * FROM "{table}"', engine)
        body = df.to_csv(index=False)
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/history/raw")
def download_raw_history():
    return _csv_download("raw_transactions_history", "raw_transactions_history.csv")


@router.get("/history/processed")
def download_processed_history():
    return _csv_download(
        "processed_transactions_history", "processed_transactions_history.csv"
    )


@router.get("/drift/{severity}")
def get_drift(severity: str):

    table = _DRIFT_TABLES.get(severity)
    if not table:
        raise HTTPException(status_code=404, detail="invalid severity")

    if not inspect(engine).has_table(table):
        return []

    query = text(f"""
        SELECT
            id,
            iso_drift_score,
            ae_drift_score,
            rules_drift_score,
            feature_drift_score,
            final_drift_score,
            created_at
        FROM {table}
        ORDER BY created_at DESC
    """)

    df = pd.read_sql(query, engine)

    if "created_at" in df.columns:
        df["created_at"] = df["created_at"].astype(str)

    return df.to_dict(orient="records")


@router.get("/drift/{severity}/{row_id}/download")
def download_drift_dataset(severity: str, row_id: int):

    table = _DRIFT_TABLES.get(severity)
    if not table:
        raise HTTPException(status_code=404, detail="invalid severity")

    row = pd.read_sql(
        text(f"SELECT transaction_ids FROM {table} WHERE id = :rid"),
        engine,
        params={"rid": row_id},
    )

    if row.empty:
        raise HTTPException(status_code=404, detail="drift record not found")

    # transaction_ids is JSONB -> usually a Python list; tolerate a JSON string too
    raw_ids = row["transaction_ids"].iloc[0]
    if isinstance(raw_ids, str):
        raw_ids = json.loads(raw_ids)
    ids = [int(i) for i in (raw_ids or [])]

    if not ids:
        raise HTTPException(status_code=404, detail="no transactions in this chunk")

    id_list = ",".join(str(i) for i in ids)

    def _fetch(history_table):
        if not inspect(engine).has_table(history_table):
            return pd.DataFrame()
        return pd.read_sql(
            text(f'SELECT * FROM "{history_table}" WHERE "TransactionID" IN ({id_list})'),
            engine,
        )

    raw_df = _fetch("raw_transactions_history")
    processed_df = _fetch("processed_transactions_history")

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"raw_{severity}_{row_id}.csv", raw_df.to_csv(index=False))
        zf.writestr(f"processed_{severity}_{row_id}.csv", processed_df.to_csv(index=False))
    mem.seek(0)

    return Response(
        content=mem.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="drift_{severity}_{row_id}.zip"'
        },
    )