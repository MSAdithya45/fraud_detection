from fastapi import APIRouter, UploadFile, File

import pandas as pd

from sqlalchemy import text

from database.transactions import engine


router = APIRouter()


@router.get("/transactions")
def get_transactions():

    query = text("""

        SELECT

            TransactionID,
            probability,
            label,
            prediction

        FROM transaction_analysis

        ORDER BY TransactionID DESC

    """)

    df = pd.read_sql(

        query,

        engine
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

    query = text("""

        SELECT

            TransactionID,

            probability,

            label,

            prediction

        FROM transaction_analysis

        WHERE TransactionID = :transaction_id

    """)

    df = pd.read_sql(

        query,

        engine,

        params={
            "transaction_id": transaction_id
        }
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



@router.post("/predict")
async def predict_csv(
    file: UploadFile = File(...)
):

    df = pd.read_csv(file.file)

    total_transactions = len(df)

    for idx in range(total_transactions):

        row = df.iloc[[idx]]

        pipeline.predict(row)

    return {

        "message":
            "File uploaded and predictions generated successfully",

        "total_transactions":
            int(total_transactions)
    }