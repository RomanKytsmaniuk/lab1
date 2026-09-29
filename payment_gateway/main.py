from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

STUDENT_N = 4

app = FastAPI(title=f"Payment Gateway Service N{STUDENT_N}")

# Початкова база даних транзакцій (ID починаються з 100 * N)
TRANSACTIONS = {
    STUDENT_N * 100 + 1: {
        "tx_id": STUDENT_N * 100 + 1,
        "account_id": 1001,
        "amount": 250.0,
        "status": "Completed"
    }
}


class PaymentRequest(BaseModel):
    account_id: int
    amount: float


@app.post("/process-payment")
def process_payment(payment: PaymentRequest):
    if payment.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid payment amount")

    new_tx_id = (STUDENT_N * 100) + len(TRANSACTIONS) + 1
    tx_record = {
        "tx_id": new_tx_id,
        "account_id": payment.account_id,
        "amount": payment.amount,
        "status": "Success"
    }
    TRANSACTIONS[new_tx_id] = tx_record
    return {
        "student_id": STUDENT_N,
        "message": "Payment processed successfully",
        "transaction": tx_record
    }


@app.get("/status/{tx_id}")
def get_payment_status(tx_id: int):
    if tx_id not in TRANSACTIONS:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "student_id": STUDENT_N,
        "transaction": TRANSACTIONS[tx_id]
    }
