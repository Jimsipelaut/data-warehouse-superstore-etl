# Superstore Data Warehouse & Business Intelligence Pipeline

An end-to-end Data Engineering and Business Intelligence project transforming raw sales data into a structured Star Schema and interactive executive dashboard.

# Tech Stack
* **Language:** Python (Pandas, SQLAlchemy)
* **Database:** PostgreSQL
* **Visualization:** Power BI

#  Project Architecture
1. **Extract:** Read raw data from `Sample - Superstore.csv` (9,994 records).
2. **Transform:** Cleaned data, handled duplicates, and modeled a Star Schema consisting of 5 Dimension tables (`dim_customer`, `dim_product`, `dim_location`, `dim_ship_mode`, `dim_date`) and 1 Fact table (`fact_sales`). Generated surrogate keys for data integrity.
3. **Load:** Automated the ingestion of the transformed DataFrames into a PostgreSQL database.
4. **Report:** Connected Power BI to PostgreSQL via Direct Import, established relationships, and utilized DAX for core business metrics.

# Dashboard Preview
<img width="807" height="525" alt="Screenshot (1163)" src="https://github.com/user-attachments/assets/19316a29-f2c6-4a96-bd0b-9db1e7641faa" />
 
# How to Run the ETL
1. Setup a local PostgreSQL database named `sales_dw`.
2. Install dependencies: `pip install pandas sqlalchemy psycopg2-binary`
3. Run the script: `python etl/etl_sales.py`
