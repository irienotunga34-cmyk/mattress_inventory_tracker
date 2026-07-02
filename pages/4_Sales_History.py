import streamlit as st
from utils.supabase_client import client

st.set_page_config(page_title="Sales History", layout="wide")

st.title("📋 Sales History")

# ---------------------------------------
# Load Sales Data
# ---------------------------------------

response = (
    client.table("sales_items")
    .select("*")
    .order("created_at", desc=True)
    .execute()
)

sales = response.data

if not sales:
    st.warning("No sales recorded yet.")
    st.stop()

# ---------------------------------------
# Search Bar
# ---------------------------------------

search = st.text_input("🔍 Search by customer or product")

if search:
    sales = [
        s for s in sales
        if search.lower() in (s.get("customer_name") or "").lower()
        or search.lower() in (s.get("product_name") or "").lower()
        or search.lower() in (s.get("phone_number") or "")
    ]

# ---------------------------------------
# Summary Metrics
# ---------------------------------------

total_sales = len(sales)
total_revenue = sum(s.get("total_amount", 0) or 0 for s in sales)
total_balance = sum(s.get("balance", 0) or 0 for s in sales)

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", total_sales)
col2.metric("Total Revenue", f"KSh {total_revenue:,.2f}")
col3.metric("Outstanding Balance", f"KSh {total_balance:,.2f}")

st.divider()

# ---------------------------------------
# Sales Table
# ---------------------------------------

for sale in sales:

    with st.container(border=True):

        col1, col2, col3 = st.columns(3)

        col1.write(f"**Product:** {sale.get('product_name')}")
        col1.write(f"**Customer:** {sale.get('customer_name')}")
        col1.write(f"**Phone:** {sale.get('phone_number')}")

        col2.write(f"**Quantity:** {sale.get('quantity')}")
        col2.write(f"**Price:** KSh {sale.get('selling_price')}")

        col3.write(f"**Total:** KSh {sale.get('total_amount')}")
        col3.write(f"**Paid:** KSh {sale.get('amount_paid')}")
        col3.write(f"**Balance:** KSh {sale.get('balance')}")

        st.caption(f"Date: {sale.get('sale_date')} | Notes: {sale.get('notes')}")