from fastapi import Depends, FastAPI
from pydantic import BaseModel
from oai_utils import extract_order_info
from db_utils import get_db, init_db, Order
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session


init_db()


class OrderRequest(BaseModel):
    text: str


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/place_order")
def place_order(order: OrderRequest, db: Session = Depends(get_db)):
    order_info = extract_order_info(order.text)
    if order_info is None:
        raise HTTPException(status_code=400, detail="Invalid order")
    if order_info["is_creating_order"]:
        order_number = db.query(Order).count() + 1
        new_order = Order(
            order_number=order_number,
            burgers=order_info["burger_delta"],
            fries=order_info["fries_delta"],
            drinks=order_info["drinks_delta"],
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

    elif order_info["is_deleting_order"]:
        order_number = order_info["order_number"]
        order_to_delete = _get_order_by_number(order_number, db)
        if not order_to_delete:
            raise HTTPException(status_code=404, detail="Order not found")
        db.delete(order_to_delete)
        db.commit()

    else:
        order_number = order_info["order_number"]
        current_order = _get_order_by_number(order_number, db)
        if not current_order:
            raise HTTPException(status_code=404, detail="Order not found")

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

        db.commit()
        db.refresh(current_order)


@app.get("/order_history")
def get_order_history(db: Session = Depends(get_db)):
    return db.query(Order).all()


# NB: this isn't as efficient for large datasets
@app.get("/total_orders")
def get_total_orders(db: Session = Depends(get_db)):
    return {
        "total_burger_orders": sum(order.burgers for order in db.query(Order).all()),
        "total_drink_orders": sum(order.drinks for order in db.query(Order).all()),
        "total_fry_orders": sum(order.fries for order in db.query(Order).all()),
    }


def _get_order_by_number(order_number: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.order_number == order_number).first()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
