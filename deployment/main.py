# -*- coding: utf-8 -*-



from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pickle

app = FastAPI()

# -----------------------------
# Load model
# -----------------------------
model = pickle.load(open("fraud_model.sav", "rb"))

# -----------------------------
# Feature list (EXCLUDING target)
# -----------------------------
FEATURES = [
'id_01','id_02','id_03','id_04','id_05','id_06','id_09','id_10','id_11',
'id_13','id_14','id_17','id_18','id_19','id_20','id_32','TransactionAmt',
'card1','card2','card3','card5','addr1','addr2','dist2',
'C1','C2','C3','C4','C6','C7','C8','C10','C11','C12','C13','C14',
'D1','D4','D5','D6','D7','D8','D9','D10','D12','D13','D14','D15',

'V12','V13','V14','V15','V16','V17','V18','V19','V20','V21','V22','V23','V24','V26',
'V31','V32','V33','V34','V35','V36','V37','V38','V39','V40','V42','V43','V44','V45',
'V46','V47','V49','V50','V51','V52','V53','V54','V55','V56','V57','V58','V59','V60',
'V61','V62','V63','V64','V65','V66','V67','V71','V72','V73','V74','V76','V77','V78',
'V79','V80','V81','V82','V84','V85','V86','V87','V88','V92','V93','V94','V95','V96',
'V97','V99','V101','V102','V105','V114','V115','V116','V123','V124','V125','V126',
'V127','V128','V129','V130','V131','V132','V133','V134','V135','V136','V137','V138',
'V139','V140','V141','V142','V143','V144','V145','V146','V147','V148','V149','V150',
'V151','V152','V153','V154','V155','V156','V157','V158','V159','V160','V161','V162',
'V163','V164','V165','V166','V167','V168','V169','V170','V171','V172','V173','V174',
'V175','V176','V177','V178','V179','V180','V181','V182','V183','V184','V185','V186',
'V187','V188','V189','V190','V191','V192','V193','V194','V195','V196','V197','V198',
'V199','V200','V201','V202','V203','V204','V205','V206','V207','V208','V209','V210',
'V211','V212','V213','V214','V215','V216','V217','V218','V219','V220','V221','V222',
'V223','V224','V225','V226','V227','V228','V229','V230','V231','V232','V233','V234',
'V235','V236','V237','V238','V239','V242','V243','V244','V245','V246','V247','V248',
'V249','V250','V251','V252','V253','V254','V255','V256','V257','V258','V259','V260',
'V261','V262','V263','V264','V265','V266','V267','V268','V269','V270','V271','V272',
'V273','V274','V275','V276','V277','V278','V279','V280','V281','V282','V283','V284',
'V285','V286','V287','V288','V289','V290','V291','V292','V293','V294','V295','V296',
'V297','V298','V299','V300','V301','V302','V303','V304','V306','V307','V308','V309',
'V310','V311','V312','V313','V314','V315','V316','V317','V318','V319','V320','V321',
'V322','V323','V324','V326','V327','V328','V329','V330','V331','V332','V333','V334',
'V335','V336','V337','V338','V339',

'rule_high_amount','hour','rule_mobile','rule_suspicious_device',
'rule_missing_email','rule_email_medium','email_fraud_rate','card_avg_amt',
'amt_ratio','txn_count_1hr','card_txn_count_1hr','rule_email_mismatch',
'card_device_count','id_missing_count','txn_gap','rule_fast_txn','rule_high_C1',
'rule_score',

'id_03_is_missing','id_14_is_missing','V61_is_missing','V62_is_missing',
'V63_is_missing','V64_is_missing','V65_is_missing','V66_is_missing',
'V67_is_missing','V68_is_missing','V69_is_missing','V70_is_missing',
'V71_is_missing','V72_is_missing','V73_is_missing','V74_is_missing',
'V75_is_missing','V76_is_missing','V77_is_missing','V78_is_missing',
'V79_is_missing','V80_is_missing','V81_is_missing','V82_is_missing',
'V83_is_missing','V84_is_missing','V85_is_missing','V86_is_missing',
'V87_is_missing','V88_is_missing','V89_is_missing','V90_is_missing',
'V91_is_missing','V92_is_missing','V93_is_missing','V94_is_missing',

'V138_is_missing','V139_is_missing','V140_is_missing','V141_is_missing',
'V142_is_missing','V143_is_missing','V144_is_missing','V145_is_missing',
'V146_is_missing','V147_is_missing','V148_is_missing','V149_is_missing',
'V150_is_missing','V151_is_missing','V152_is_missing','V153_is_missing',
'V154_is_missing','V155_is_missing','V156_is_missing','V157_is_missing',
'V158_is_missing','V159_is_missing','V160_is_missing','V161_is_missing',
'V162_is_missing','V163_is_missing','V164_is_missing','V165_is_missing',
'V166_is_missing',

'V217_is_missing','V218_is_missing','V219_is_missing','V223_is_missing',
'V224_is_missing','V225_is_missing','V226_is_missing','V228_is_missing',
'V229_is_missing','V230_is_missing','V231_is_missing','V232_is_missing',
'V233_is_missing','V235_is_missing','V236_is_missing','V237_is_missing',
'V240_is_missing','V241_is_missing','V242_is_missing','V243_is_missing',
'V244_is_missing','V246_is_missing','V247_is_missing','V248_is_missing',
'V249_is_missing','V252_is_missing','V253_is_missing','V254_is_missing',
'V257_is_missing','V258_is_missing','V260_is_missing',

'V322_is_missing','V323_is_missing','V324_is_missing','V325_is_missing',
'V326_is_missing','V327_is_missing','V328_is_missing','V329_is_missing',
'V330_is_missing','V331_is_missing','V332_is_missing','V336_is_missing',
'V339_is_missing',

'email_fraud_rate_is_missing','txn_count_1hr_is_missing',

'id_12_freq','id_15_freq','id_16_freq','id_28_freq','id_29_freq','id_30_freq',
'id_31_freq','id_33_freq','id_34_freq','id_35_freq','id_36_freq','id_37_freq',
'id_38_freq','DeviceType_freq','DeviceInfo_freq','ProductCD_freq',
'card4_freq','card6_freq','P_emaildomain_freq','R_emaildomain_freq',
'M4_freq',

'ae_score','very_high_ae','iso_score'
]

# -----------------------------
# Input Schema
# -----------------------------
class FraudInput(BaseModel):
    data: dict

# -----------------------------
# Root
# -----------------------------
@app.get("/")
def home():
    return {"message": "Fraud Detection API Running"}

# -----------------------------
# Prediction Endpoint
# -----------------------------
@app.post("/predict")
def predict(input_data: FraudInput):

    try:
        import pandas as pd

        # -----------------------------
        # Custom Threshold
        # -----------------------------
        THRESHOLD = 0.715

        data_dict = input_data.data

        # -----------------------------
        # Missing Features Check
        # -----------------------------
        missing = [f for f in FEATURES if f not in data_dict]

        if missing:
            return {
                "error": "Missing features",
                "missing_count": len(missing),
                "first_10_missing": missing[:10]
            }

        # -----------------------------
        # Create DataFrame
        # -----------------------------
        X = pd.DataFrame([data_dict])

        # exact feature order
        X = X.reindex(columns=FEATURES, fill_value=-1)

        # numeric conversion
        X = X.apply(pd.to_numeric, errors="coerce")

        # fill null values
        X = X.fillna(-1)

        # -----------------------------
        # Predict Probability
        # -----------------------------
        prob = float(model.predict_proba(X)[0][1])

        # -----------------------------
        # Apply Custom Threshold
        # -----------------------------
        prediction = 1 if prob >= THRESHOLD else 0

        # -----------------------------
        # Return Output
        # -----------------------------
        return {
            "prediction": int(prediction),
            "fraud": bool(prediction),
            "probability": prob,
            "threshold": THRESHOLD,
            "status": "success"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }