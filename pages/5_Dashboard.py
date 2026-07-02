import streamlit as st
import pandas as pd
from io import BytesIO
from utils.supabase_client import client
from datetime import date

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 Business Dashboard")

# ---------------------------------------
# EXCEL EXPORT FUNCTION
# ---------------------------------------

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sales Report")
    return output.getvalue()

# ---------------------------------------
# LOAD DATA
# ---------------------------------------

sales = client.table("sales_items").select("*").execute().data or []
products = client.table("products").select("*").execute().data or []

# ---------------------------------------
# KPIs
# ---------------------------------------

total_sales = len(sales)
total_revenue = sum(s.get("total_amount") or 0 for s in sales)
total_paid = sum(s.get("amount_paid") or 0 for s in sales)
total_balance = sum(s.get("balance") or 0 for s in sales)

low_stock = [p for p in products if (p.get("quantity_in_stock") or 0) <= 5]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", total_sales)
col2.metric("Revenue", f"KSh {total_revenue:,.2f}")
col3.metric("Paid", f"KSh {total_paid:,.2f}")
col4.metric("Balance", f"KSh {total_balance:,.2f}")

st.divider()

# ---------------------------------------
# STOCK OVERVIEW
# ---------------------------------------

st.subheader("📦 Stock Overview")

col1, col2 = st.columns(2)

col1.metric("Products", len(products))
col2.metric("Low Stock", len(low_stock))

if low_stock:
    st.warning("⚠️ Low stock items")
    for p in low_stock:
        st.write(f"• {p.get('product_name')} → {p.get('quantity_in_stock')} left")

st.divider()

# ---------------------------------------
# TODAY SUMMARY
# ---------------------------------------

st.subheader("📅 Today Summary")

today = str(date.today())

today_sales = [s for s in sales if s.get("sale_date") == today]
today_revenue = sum(s.get("total_amount") or 0 for s in today_sales)

col1, col2 = st.columns(2)

col1.metric("Today's Sales", len(today_sales))
col2.metric("Today's Revenue", f"KSh {today_revenue:,.2f}")

st.divider()

# ---------------------------------------
# REVENUE TREND
# ---------------------------------------

st.subheader("📈 Revenue Trend")

daily_revenue = {}

for s in sales:
    day = s.get("sale_date")
    if not day:
        continue
    daily_revenue[day] = daily_revenue.get(day, 0) + (s.get("total_amount") or 0)

revenue_data = [{"date": k, "revenue": v} for k, v in sorted(daily_revenue.items())]

if revenue_data:
    st.line_chart(revenue_data, x="date", y="revenue")

st.divider()

# ---------------------------------------
# PROFIT TREND
# ---------------------------------------

st.subheader("💰 Profit Trend")

daily_profit = {}

for s in sales:
    day = s.get("sale_date")
    if not day:
        continue

    selling = s.get("selling_price") or 0
    cost = s.get("cost_price") or 0
    qty = s.get("quantity") or 0

    profit = (selling - cost) * qty if selling > 0 and cost > 0 else 0

    daily_profit[day] = daily_profit.get(day, 0) + profit

profit_data = [{"date": k, "profit": v} for k, v in sorted(daily_profit.items())]

if profit_data:
    st.line_chart(profit_data, x="date", y="profit")

st.divider()

# ---------------------------------------
# TOP PRODUCTS
# ---------------------------------------

st.subheader("🔥 Top Products")

product_sales = {}

for s in sales:
    name = s.get("product_name")
    if not name:
        continue
    qty = s.get("quantity") or 0
    product_sales[name] = product_sales.get(name, 0) + qty

top = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]

top_data = [{"product": k, "quantity": v} for k, v in top]

if top_data:
    st.bar_chart(top_data, x="product", y="quantity")

st.divider()

# ---------------------------------------
# PAYMENT METHODS
# ---------------------------------------

st.subheader("💳 Payment Methods")

payment_counts = {}

for s in sales:
    method = s.get("payment_method")
    if not method:
        continue
    payment_counts[method] = payment_counts.get(method, 0) + 1

payment_data = [{"method": k, "count": v} for k, v in payment_counts.items()]

if payment_data:
    st.bar_chart(payment_data, x="method", y="count")

st.divider()

# ---------------------------------------
# EXPORT REPORT
# ---------------------------------------

st.subheader("📤 Export Reports")

export_data = []

for s in sales:
    selling = s.get("selling_price") or 0
    cost = s.get("cost_price") or 0
    qty = s.get("quantity") or 0

    profit = (selling - cost) * qty if selling > 0 and cost > 0 else 0

    export_data.append({
        "Date": s.get("sale_date"),
        "Product": s.get("product_name"),
        "Customer": s.get("customer_name"),
        "Phone": s.get("phone_number"),
        "Quantity": qty,
        "Selling Price": selling,
        "Cost Price": cost,
        "Revenue": s.get("total_amount") or 0,
        "Profit": profit,
        "Paid": s.get("amount_paid") or 0,
        "Balance": s.get("balance") or 0,
        "Payment Method": s.get("payment_method"),
    })

df = pd.DataFrame(export_data)

excel_file = convert_df_to_excel(df)

st.download_button(
    label="📥 Download Sales Report (Excel)",
    data=excel_file,
    file_name="sales_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# ---------------------------------------
# CREDIT SYSTEM
# ---------------------------------------

st.subheader("💳 Credit Overview")

credit_sales = [s for s in sales if (s.get("balance") or 0) > 0]

total_credit = sum(s.get("balance") or 0 for s in credit_sales)

col1, col2 = st.columns(2)

col1.metric("Customers on Credit", len(credit_sales))
col2.metric("Total Outstanding Debt", f"KSh {total_credit:,.2f}")

st.subheader("👥 Customer Debt List")

debt_map = {}

for s in credit_sales:
    name = s.get("customer_name") or "Unknown"
    phone = s.get("phone_number") or ""
    key = f"{name} ({phone})"

    debt_map[key] = debt_map.get(key, 0) + (s.get("balance") or 0)

sorted_debt = sorted(debt_map.items(), key=lambda x: x[1], reverse=True)

for customer, debt in sorted_debt:
    st.write(f"• {customer} → KSh {debt:,.2f}")
    st.divider()

st.subheader("📅 Monthly Profit Summary")

monthly_profit = {}
monthly_revenue = {}
monthly_sales = {}

for s in sales:
    date_str = s.get("sale_date")
    if not date_str:
        continue

    # extract YYYY-MM
    month = str(date_str)[:7]

    selling = s.get("selling_price") or 0
    cost = s.get("cost_price") or 0
    qty = s.get("quantity") or 0

    revenue = s.get("total_amount") or 0
    profit = (selling - cost) * qty if selling > 0 and cost > 0 else 0

    monthly_revenue[month] = monthly_revenue.get(month, 0) + revenue
    monthly_profit[month] = monthly_profit.get(month, 0) + profit
    monthly_sales[month] = monthly_sales.get(month, 0) + 1

# build chart data
monthly_data = []

for m in sorted(monthly_revenue.keys()):
    monthly_data.append({
        "month": m,
        "revenue": monthly_revenue.get(m, 0),
        "profit": monthly_profit.get(m, 0),
        "sales": monthly_sales.get(m, 0)
    })

if monthly_data:
    col1, col2 = st.columns(2)

    col1.metric("Best Month Revenue", max(monthly_revenue.values()) if monthly_revenue else 0)
    col2.metric("Best Month Profit", max(monthly_profit.values()) if monthly_profit else 0)

    st.line_chart(monthly_data, x="month", y="profit")