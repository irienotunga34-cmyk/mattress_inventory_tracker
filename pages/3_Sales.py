import streamlit as st
from datetime import date
from utils.supabase_client import client

st.set_page_config(page_title="Sales", layout="wide")

st.title("💰 Record Sale")

# ---------------------------------------
# Load Products
# ---------------------------------------

response = (
    client.table("products")
    .select("*")
    .order("product_name")
    .execute()
)

products = response.data

if not products:
    st.warning("No products available.")
    st.stop()

selected_product = st.selectbox(
    "Select Product",
    products,
    format_func=lambda x: x["product_name"]
)

current_stock = int(selected_product["quantity_in_stock"])
st.info(f"Current Stock: {current_stock}")

# ---------------------------------------
# Customer Details
# ---------------------------------------

customer_name = st.text_input("Customer Name")
phone_number = st.text_input("Phone Number")

payment_method = st.selectbox(
    "Payment Method",
    ["Cash", "M-Pesa", "Bank", "Credit"]
)

sale_date = st.date_input(
    "Sale Date",
    value=date.today()
)

# ---------------------------------------
# Sale Details
# ---------------------------------------

quantity = st.number_input(
    "Quantity Sold",
    min_value=1,
    max_value=max(current_stock, 1),
    step=1
)

selling_price = st.number_input(
    "Selling Price",
    min_value=0.0,
    value=float(selected_product["selling_price"]),
    step=100.0
)

total_amount = quantity * selling_price
st.metric("Total Amount", f"KSh {total_amount:,.2f}")

amount_paid = st.number_input(
    "Amount Paid",
    min_value=0.0,
    value=float(total_amount),
    step=100.0
)

balance = total_amount - amount_paid
st.metric("Balance", f"KSh {balance:,.2f}")

notes = st.text_area("Notes")

# ---------------------------------------
# Save Sale
# ---------------------------------------

if st.button("✅ Complete Sale"):

    if quantity > current_stock:
        st.error("Not enough stock available.")

    else:
        client.table("sales_items").insert(
            {
                "product_id": selected_product["id"],
                "product_name": selected_product["product_name"],
                "sale_date": str(sale_date),
                "customer_name": customer_name,
                "phone_number": phone_number,
                "payment_method": payment_method,
                "quantity": quantity,
                "selling_price": selling_price,
                "total_amount": total_amount,
                "amount_paid": amount_paid,
                "balance": balance,
                "notes": notes,
            }
        ).execute()

        client.table("products").update(
            {
                "quantity_in_stock": current_stock - quantity
            }
        ).eq("id", selected_product["id"]).execute()

        st.success("✅ Sale recorded successfully!")
        st.balloons()