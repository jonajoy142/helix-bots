"""Run once to populate demo orders + FAQ knowledge base: `python -m app.seed_data`"""
from app.db import get_conn, init_db

FAQS = [
    ("What are your business hours?", "We're available Monday to Saturday, 9 AM to 7 PM IST."),
    ("How do I track my order?", "Share your order ID (e.g. ORD1001) and I'll fetch the live status for you."),
    ("What is your return policy?", "Items can be returned within 7 days of delivery if unused and in original packaging."),
    ("Do you offer Cash on Delivery?", "Yes, COD is available for orders under ₹5000 across India."),
    ("How long does shipping take?", "Standard shipping takes 3-5 business days; express shipping takes 1-2 days."),
    ("How do I cancel my order?", "Orders can be cancelled within 2 hours of placing them. Share your order ID and I can check eligibility."),
    ("Do you ship internationally?", "Currently we ship only within India."),
    ("What payment methods do you accept?", "We accept UPI, credit/debit cards, net banking, and Cash on Delivery."),
]

ORDERS = [
    ("ORD1001", "+919999900001", "Wireless Earbuds Pro", "Shipped", "2 days"),
    ("ORD1002", "+919999900002", "Smart Fitness Band", "Processing", "4 days"),
    ("ORD1003", "+919999900003", "Bluetooth Speaker Mini", "Delivered", "-"),
    ("ORD1004", "+919999900004", "Laptop Stand Aluminium", "Out for Delivery", "Today"),
]


def seed():
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM faqs")
        conn.executemany("INSERT INTO faqs (question, answer) VALUES (?, ?)", FAQS)

        conn.execute("DELETE FROM orders")
        conn.executemany(
            "INSERT INTO orders (order_id, customer_phone, product_name, status, eta) VALUES (?,?,?,?,?)",
            ORDERS,
        )
    print(f"Seeded {len(FAQS)} FAQs and {len(ORDERS)} orders into support_bot.db")


if __name__ == "__main__":
    seed()
