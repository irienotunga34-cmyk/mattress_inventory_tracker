import streamlit as st
from utils.supabase_client import client

st.set_page_config(page_title="Products", layout="wide")

st.title("📦 Products")
st.write("Manage your mattress products.")

st.divider()

# ======================================
# ADD PRODUCT
# ======================================

st.subheader("➕ Add New Product")

with st.form("add_product"):

    product_name = st.text_input("Product Name")
    brand = st.text_input("Brand")
    material = st.text_input("Material")
    specification = st.text_input("Specification")

    cost_price = st.number_input(
        "Cost Price",
        min_value=0.0,
        step=1.0
    )

    selling_price = st.number_input(
        "Selling Price",
        min_value=0.0,
        step=1.0
    )

    quantity_in_stock = st.number_input(
        "Stock Quantity",
        min_value=0,
        step=1
    )

    save = st.form_submit_button("💾 Save Product")

if save:

    if product_name.strip() == "":
        st.error("Please enter a product name.")

    else:

        try:

            client.table("products").insert(
                {
                    "product_name": product_name,
                    "brand": brand,
                    "material": material,
                    "specification": specification,
                    "cost_price": cost_price,
                    "selling_price": selling_price,
                    "quantity_in_stock": quantity_in_stock,
                }
            ).execute()

            st.success("✅ Product saved successfully!")

        except Exception as e:

            st.error(f"Error: {e}")

st.divider()

# ======================================
# VIEW PRODUCTS
# ======================================

st.subheader("📋 All Products")

try:

    response = (
        client
        .table("products")
        .select("*")
        .order("id")
        .execute()
    )

    products = response.data

    if products:

        st.dataframe(
            products,
            use_container_width=True
        )

    else:

        st.info("No products found.")

except Exception as e:

    st.error(f"Error: {e}")

st.divider()

# ======================================
# UPDATE STOCK
# ======================================

st.subheader("🔄 Update Stock")

try:

    response = (
        client
        .table("products")
        .select("*")
        .order("id")
        .execute()
    )

    products = response.data

    if products:

        selected_product = st.selectbox(
            "Select Product",
            options=products,
            format_func=lambda x: x["product_name"]
        )

        st.info(
            f"Current Stock: {selected_product['quantity_in_stock']}"
        )

        new_stock = st.number_input(
            "New Stock Quantity",
            min_value=0,
            value=int(selected_product["quantity_in_stock"]),
            step=1
        )

        if st.button("Update Stock"):

            client.table("products").update(
                {
                    "quantity_in_stock": new_stock
                }
            ).eq(
                "id",
                selected_product["id"]
            ).execute()

            st.success("✅ Stock updated successfully!")

except Exception as e:

    st.error(f"Error: {e}")