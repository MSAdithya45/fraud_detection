import pandas as pd

from sqlalchemy import text

from src.llm.prompt_builder import (
    build_prompt
)

from src.llm.gemini_client import (
    generate_explanation
)

from database.transactions import engine


# ============================================================
# FETCH TRANSACTION
# ============================================================

def fetch_transaction(
    transaction_id
):

    query = text("""
        SELECT *
        FROM transaction_analysis
        WHERE TransactionID = :transaction_id
    """)

    return pd.read_sql(

        query,

        engine,

        params={
            "transaction_id": transaction_id
        }
    )


# ============================================================
# FETCH SHAP
# ============================================================

def fetch_shap(
    transaction_id
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

    return pd.read_sql(

        query,

        engine,

        params={
            "transaction_id": transaction_id
        }
    )


# ============================================================
# SAVE LLM EXPLANATION
# ============================================================

def save_explanation(

    transaction_id,

    explanation
):

    query = text("""
        INSERT INTO llm_explanations
        (
            transaction_id,
            explanation
        )
        VALUES
        (
            :transaction_id,
            :explanation
        )
    """)

    with engine.begin() as conn:

        conn.execute(

            query,

            {
                "transaction_id":
                transaction_id,

                "explanation":
                explanation
            }
        )


# ============================================================
# GENERATE EXPLANATION
# ============================================================

def explain_transaction(
    transaction_id
):

    txn = fetch_transaction(
        transaction_id
    )

    if txn.empty:

        return {

            "error":
            "Transaction not found"
        }

    shap = fetch_shap(
        transaction_id
    )

    prompt = build_prompt(

        txn.to_dict("records")[0],

        shap.to_dict("records")
    )

    explanation = generate_explanation(
        prompt
    )

    # ========================================================
    # SAVE GENERATED EXPLANATION
    # ========================================================

    save_explanation(

        transaction_id,

        explanation
    )

    return {

        "transaction_id":
        transaction_id,

        "explanation":
        explanation
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        explain_transaction(
            2987004
        )
    )