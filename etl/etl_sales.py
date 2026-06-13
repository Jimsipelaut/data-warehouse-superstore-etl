import pandas as pd

from sqlalchemy import create_engine
from urllib.parse import quote_plus

# =====================================================
# KONFIGURASI DATABASE
# =====================================================

DB_USER = "postgres"
DB_PASSWORD = "porto123@(_)"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "sales_dw"

encoded_password = quote_plus(DB_PASSWORD)

connection_string = (
    f"postgresql+psycopg2://{DB_USER}:{encoded_password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(connection_string)
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE dw.dim_customer RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dw.dim_product RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dw.dim_location RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dw.dim_ship_mode RESTART IDENTITY CASCADE"))
    conn.execute(text("TRUNCATE TABLE dw.dim_date CASCADE"))

print("Semua dimensi berhasil dikosongkan")

# =====================================================
# LOAD DATASET
# =====================================================

csv_file = r"C:\DataWarehousePortfolio\dataset\Sample - Superstore.csv"

df = pd.read_csv(
    csv_file,
    encoding="latin1",
    engine="python"
)

# =====================================================
# DIM CUSTOMER
# =====================================================

dim_customer = (
    df[
        [
            "Customer ID",
            "Customer Name",
            "Segment"
        ]
    ]
    .drop_duplicates()
)

# Rename kolom agar sesuai DW
dim_customer.columns = [
    "customer_id",
    "customer_name",
    "segment"
]

print("Jumlah Customer Unik:", len(dim_customer))

# =====================================================
# LOAD KE POSTGRESQL
# =====================================================

dim_customer.to_sql(
    "dim_customer",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Load dim_customer BERHASIL")

# =====================================================
# DIM PRODUCT
# =====================================================

dim_product = (
    df[
        [
            "Product ID",
            "Product Name",
            "Category",
            "Sub-Category"
        ]
    ]
    .drop_duplicates()
)

# Rename kolom sesuai DW
dim_product.columns = [
    "product_id",
    "product_name",
    "category",
    "sub_category"
]

print("Jumlah Product Unik:", len(dim_product))

# =====================================================
# LOAD KE POSTGRESQL
# =====================================================

dim_product.to_sql(
    "dim_product",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Load dim_product BERHASIL")

# =====================================================
# DIM LOCATION
# =====================================================

dim_location = (
    df[
        [
            "Country",
            "Region",
            "State",
            "City",
            "Postal Code"
        ]
    ]
    .drop_duplicates()
)

# Rename kolom sesuai DW
dim_location.columns = [
    "country",
    "region",
    "state",
    "city",
    "postal_code"
]

print("Jumlah Location Unik:", len(dim_location))

# =====================================================
# LOAD KE POSTGRESQL
# =====================================================

dim_location.to_sql(
    "dim_location",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Load dim_location BERHASIL")

# =====================================================
# DIM SHIP MODE
# =====================================================

dim_ship_mode = (
    df[
        [
            "Ship Mode"
        ]
    ]
    .drop_duplicates()
)

# Rename kolom sesuai DW
dim_ship_mode.columns = [
    "ship_mode"
]

print("Jumlah Ship Mode Unik:", len(dim_ship_mode))

# =====================================================
# LOAD KE POSTGRESQL
# =====================================================

dim_ship_mode.to_sql(
    "dim_ship_mode",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Load dim_ship_mode BERHASIL")

# =====================================================
# DIM DATE
# =====================================================

# Konversi ke datetime
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])

# Ambil seluruh tanggal unik
order_dates = df["Order Date"]
ship_dates = df["Ship Date"]

all_dates = pd.concat([
    order_dates,
    ship_dates
]).drop_duplicates()

# Buat DataFrame dim_date
dim_date = pd.DataFrame({
    "full_date": all_dates
})

dim_date = dim_date.sort_values(
    by="full_date"
).reset_index(drop=True)

# Generate atribut tanggal
dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
dim_date["day"] = dim_date["full_date"].dt.day
dim_date["month"] = dim_date["full_date"].dt.month
dim_date["month_name"] = dim_date["full_date"].dt.strftime("%B")
dim_date["quarter"] = dim_date["full_date"].dt.quarter
dim_date["year"] = dim_date["full_date"].dt.year

# Susun urutan kolom sesuai tabel DW
dim_date = dim_date[
    [
        "date_key",
        "full_date",
        "day",
        "month",
        "month_name",
        "quarter",
        "year"
    ]
]

print("Jumlah Date Unik:", len(dim_date))

# =====================================================
# LOAD KE POSTGRESQL
# =====================================================

dim_date.to_sql(
    "dim_date",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Load dim_date BERHASIL")

# =====================================================
# LOAD DIMENSIONS FOR LOOKUP
# =====================================================

dim_customer_db = pd.read_sql(
    "SELECT customer_key, customer_id FROM dw.dim_customer",
    engine
)

dim_product_db = pd.read_sql(
    "SELECT product_key, product_id FROM dw.dim_product",
    engine
)

dim_location_db = pd.read_sql(
    """
    SELECT
        location_key,
        country,
        region,
        state,
        city,
        postal_code
    FROM dw.dim_location
    """,
    engine
)

dim_ship_mode_db = pd.read_sql(
    """
    SELECT
        ship_mode_key,
        ship_mode
    FROM dw.dim_ship_mode
    """,
    engine
)

dim_date_db = pd.read_sql(
    """
    SELECT
        date_key,
        full_date
    FROM dw.dim_date
    """,
    engine
)

print("Lookup Dimensions BERHASIL")

print("Customer :", len(dim_customer_db))
print("Product  :", len(dim_product_db))
print("Location :", len(dim_location_db))
print("ShipMode :", len(dim_ship_mode_db))
print("Date     :", len(dim_date_db))

# =====================================================
# CUSTOMER LOOKUP
# =====================================================

fact_df = df.copy()

fact_df = fact_df.merge(
    dim_customer_db,
    how="left",
    left_on="Customer ID",
    right_on="customer_id"
)

print("Customer Lookup BERHASIL")

print(
    "Customer Key Null:",
    fact_df["customer_key"].isnull().sum()
)

print(
    "Jumlah Record Fact:",
    len(fact_df)
)

# =====================================================
# PRODUCT LOOKUP
# =====================================================

fact_df = fact_df.merge(
    dim_product_db,
    how="left",
    left_on="Product ID",
    right_on="product_id"
)

print("Product Lookup BERHASIL")

print(
    "Product Key Null:",
    fact_df["product_key"].isnull().sum()
)

# =====================================================
# SHIP MODE LOOKUP
# =====================================================

fact_df = fact_df.merge(
    dim_ship_mode_db,
    how="left",
    left_on="Ship Mode",
    right_on="ship_mode"
)

print("Ship Mode Lookup BERHASIL")

print(
    "Ship Mode Key Null:",
    fact_df["ship_mode_key"].isnull().sum()
)

# Samakan tipe data Postal Code

fact_df["Postal Code"] = (
    fact_df["Postal Code"]
    .astype(str)
)

dim_location_db["postal_code"] = (
    dim_location_db["postal_code"]
    .astype(str)
)

# =====================================================
# LOCATION LOOKUP
# =====================================================

fact_df = fact_df.merge(
    dim_location_db,
    how="left",
    left_on=[
        "Country",
        "Region",
        "State",
        "City",
        "Postal Code"
    ],
    right_on=[
        "country",
        "region",
        "state",
        "city",
        "postal_code"
    ]
)

print("Location Lookup BERHASIL")

print(
    "Location Key Null:",
    fact_df["location_key"].isnull().sum()
)

# =====================================================
# ORDER DATE LOOKUP
# =====================================================

# Samakan tipe datetime
fact_df["Order Date"] = pd.to_datetime(
    fact_df["Order Date"]
)

dim_date_db["full_date"] = pd.to_datetime(
    dim_date_db["full_date"]
)

fact_df = fact_df.merge(
    dim_date_db,
    how="left",
    left_on="Order Date",
    right_on="full_date"
)

fact_df.rename(
    columns={
        "date_key": "order_date_key"
    },
    inplace=True
)

print("Order Date Lookup BERHASIL")

print(
    "Order Date Key Null:",
    fact_df["order_date_key"].isnull().sum()
)

# =====================================================
# SHIP DATE LOOKUP
# =====================================================

ship_date_lookup = dim_date_db.copy()

fact_df["Ship Date"] = pd.to_datetime(
    fact_df["Ship Date"]
)

fact_df = fact_df.merge(
    ship_date_lookup,
    how="left",
    left_on="Ship Date",
    right_on="full_date"
)

fact_df.rename(
    columns={
        "date_key": "ship_date_key"
    },
    inplace=True
)

print("Ship Date Lookup BERHASIL")

print(
    "Ship Date Key Null:",
    fact_df["ship_date_key"].isnull().sum()
)

# =====================================================
# BUILD FACT SALES
# =====================================================

# Hapus duplikasi baris transaksi yang tidak disengaja akibat proses join
fact_df = fact_df.drop_duplicates(subset=["Row ID"], keep="first")

fact_sales = fact_df[
    [
        "order_date_key",
        "ship_date_key",
        "customer_key",
        "product_key",
        "location_key",
        "ship_mode_key",
        "Sales",
        "Quantity",
        "Discount",
        "Profit"
    ]
].copy()

# Rename measure columns
fact_sales.columns = [
    "order_date_key",
    "ship_date_key",
    "customer_key",
    "product_key",
    "location_key",
    "ship_mode_key",
    "sales_amount",
    "quantity",
    "discount",
    "profit"
]

print("\nFACT SALES BERHASIL DIBENTUK")
print("Jumlah Record Fact:", len(fact_sales))

print("\n5 Data Pertama:")
print(fact_sales.head())

# =====================================================
# LOAD FACT SALES KE POSTGRESQL
# =====================================================

print("\nMulai Load Fact Sales ke PostgreSQL...")

# Kita HANYA me-load fact_sales karena semua dimensi 
# SUDAH berhasil di-load di baris-baris atas.
# Kita gunakan 'engine' utama yang sudah terkoneksi ke sales_dw
fact_sales.to_sql(
    'fact_sales',
    engine,
    schema='dw',
    if_exists='replace', # Gunakan replace untuk tabel fakta jika struktur DDL-nya belum dibuat manual
    index=False
)

print("Load Fact Sales BERHASIL")
print("\n=====================================================")
print("PROSES ETL SELESAI 100%! DATA WAREHOUSE SIAP 🎉")
print("=====================================================")