from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

STUDENT_N = 4

app = FastAPI(title=f"Checkout Service N{STUDENT_N}")

# Внутрішнє звернення до сервісу-залежності через DNS Docker Compose
PAYMENT_GATEWAY_URL = "http://payment-gateway-04:8000"

CHECKOUT_OPERATIONS = []


class CheckoutRequest(BaseModel):
    account_id: int
    item_name: str
    amount: float


@app.post("/checkout")
def process_checkout(order: CheckoutRequest):
    # 1. Синхронне звернення до Payment Gateway для здійснення транзакції
    try:
        payment_payload = {
            "account_id": order.account_id,
            "amount": order.amount
        }
        response = requests.post(
            f"{PAYMENT_GATEWAY_URL}/process-payment",
            json=payment_payload,
            timeout=5
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Payment Gateway is unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Payment rejected: {response.text}"
        )

    payment_data = response.json().get("transaction", {})

    # 2. Формування та збереження підсумкового запису чекауту
    checkout_entry = {
        "checkout_id": (STUDENT_N * 100) + len(CHECKOUT_OPERATIONS) + 1,
        "item_name": order.item_name,
        "amount": order.amount,
        "tx_id": payment_data.get("tx_id"),
        "status": "Paid"
    }
    CHECKOUT_OPERATIONS.append(checkout_entry)

    return {
        "student_id": STUDENT_N,
        "message": "Checkout completed successfully",
        "order": checkout_entry
    }


@app.get("/summary")
def get_summary():
    return {
        "student_id": STUDENT_N,
        "total_operations": len(CHECKOUT_OPERATIONS),
        "records": CHECKOUT_OPERATIONS
    }
