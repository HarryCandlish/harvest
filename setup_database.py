"""
Database Setup
--------------
Creates the new_harvest database and tables for:
  - NZ Official Cash Rate (RBNZ)
  - NZ Median House Prices by region
  - NZ Housing Deprivation estimates
"""

import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Connect without specifying a database first
conn = mysql.connector.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD
)
cursor = conn.cursor()

# Create database
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")
print(f"Database '{DB_NAME}' ready.")

# ── Table 1: Official Cash Rate ───────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS ocr_rates (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    rate        DECIMAL(5,2) NOT NULL,
    UNIQUE KEY unique_date (date)
)
""")
print("Table 'ocr_rates' ready.")

# ── Table 2: House Prices by Region ──────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS house_prices (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    region      VARCHAR(100) NOT NULL,
    median_price INT NOT NULL,
    UNIQUE KEY unique_region_date (date, region)
)
""")
print("Table 'house_prices' ready.")

# ── Table 3: Housing Deprivation ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS housing_deprivation (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    region      VARCHAR(100) NOT NULL,
    year        INT NOT NULL,
    estimated_people INT NOT NULL,
    rate_pct    DECIMAL(4,2) NOT NULL,
    UNIQUE KEY unique_region_year (region, year)
)
""")
print("Table 'housing_deprivation' ready.")

# ── Table 4: Rental Prices by Region ─────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS rental_prices (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE NOT NULL,
    region      VARCHAR(100) NOT NULL,
    median_weekly_rent INT NOT NULL,
    UNIQUE KEY unique_region_date (date, region)
)
""")
print("Table 'rental_prices' ready.")

conn.commit()
cursor.close()
conn.close()
print("\nAll tables created successfully.")
