from fastapi import FastAPI
from pydantic import BaseModel
from oai_utils import extract_order_info
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


class Order(BaseModel):
    text: str


class OrderInfo(BaseModel):
    order_number: int
    burgers: int
    fries: int
    drinks: int


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


order_history = {}


@app.post("/place_order")
def place_order(order: Order):
    order_info = extract_order_info(order.text)
    if order_info is None:
        raise HTTPException(status_code=400, detail="Invalid order")
    if order_info["is_creating_order"]:
        order_number = len(order_history) + 1
        order_history[order_number] = OrderInfo(
            order_number=order_number,
            burgers=order_info["burger_delta"],
            fries=order_info["fries_delta"],
            drinks=order_info["drinks_delta"],
        )
    elif order_info["is_deleting_order"]:
        order_number = order_info["order_number"]
        if order_number not in order_history:
            raise HTTPException(status_code=404, detail="Order not found")

        del order_history[order_number]
    else:
        order_number = order_info["order_number"]
        if order_number not in order_history:
            raise HTTPException(status_code=404, detail="Order not found")

        current_order = order_history[order_number]

        burger_delta = order_info["burger_delta"]
        fries_delta = order_info["fries_delta"]
        drinks_delta = order_info["drinks_delta"]

        new_burgers = current_order.burgers + burger_delta
        new_fries = current_order.fries + fries_delta
        new_drinks = current_order.drinks + drinks_delta

        if new_burgers < 0 or new_fries < 0 or new_drinks < 0:
            raise HTTPException(
                status_code=400, detail="Order cannot have negative items"
            )

        current_order.burgers = new_burgers
        current_order.fries = new_fries
        current_order.drinks = new_drinks


@app.get("/order_history")
def get_order_history():
    return list(order_history.values())[::-1]


@app.get("/total_orders")
def get_total_orders():
    return {
        "total_burger_orders": sum(order.burgers for order in order_history.values()),
        "total_drink_orders": sum(order.drinks for order in order_history.values()),
        "total_fry_orders": sum(order.fries for order in order_history.values()),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
