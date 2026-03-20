"""
Data Loader
-----------
Fetches NZ housing data and loads it into MySQL:
  1. RBNZ Official Cash Rate (historical)
  2. NZ Median House Prices by region (REINZ-style estimates)
  3. Housing Deprivation data (Stats NZ 2023 Census)
"""

import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

conn = mysql.connector.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)
cursor = conn.cursor()

# ── 1. RBNZ Official Cash Rate (historical) ───────────────────────────────────
# Source: Reserve Bank of New Zealand — rbnz.govt.nz
ocr_data = [
    ("2015-01-29", 3.50), ("2015-03-12", 3.50), ("2015-04-30", 3.50),
    ("2015-06-11", 3.25), ("2015-07-23", 3.00), ("2015-09-10", 2.75),
    ("2015-10-29", 2.75), ("2015-12-10", 2.50), ("2016-01-28", 2.50),
    ("2016-03-10", 2.25), ("2016-04-28", 2.25), ("2016-06-09", 2.25),
    ("2016-08-11", 2.00), ("2016-09-22", 2.00), ("2016-11-10", 1.75),
    ("2017-02-09", 1.75), ("2017-03-23", 1.75), ("2017-05-11", 1.75),
    ("2017-06-22", 1.75), ("2017-08-10", 1.75), ("2017-09-28", 1.75),
    ("2017-11-09", 1.75), ("2018-02-08", 1.75), ("2018-03-22", 1.75),
    ("2018-05-10", 1.75), ("2018-06-28", 1.75), ("2018-08-09", 1.75),
    ("2018-09-27", 1.75), ("2018-11-08", 1.75), ("2019-02-13", 1.75),
    ("2019-03-27", 1.75), ("2019-05-08", 1.50), ("2019-06-26", 1.50),
    ("2019-08-07", 1.00), ("2019-09-25", 1.00), ("2019-11-13", 1.00),
    ("2020-02-12", 1.00), ("2020-03-16", 0.25), ("2020-05-13", 0.25),
    ("2020-06-24", 0.25), ("2020-08-12", 0.25), ("2020-09-23", 0.25),
    ("2020-11-11", 0.25), ("2021-02-24", 0.25), ("2021-04-14", 0.25),
    ("2021-05-26", 0.25), ("2021-07-14", 0.25), ("2021-08-18", 0.25),
    ("2021-10-06", 0.50), ("2021-11-24", 0.75), ("2022-02-23", 1.00),
    ("2022-04-13", 1.50), ("2022-05-25", 2.00), ("2022-07-13", 2.50),
    ("2022-08-17", 3.00), ("2022-10-05", 3.50), ("2022-11-23", 4.25),
    ("2023-02-22", 4.75), ("2023-04-05", 5.00), ("2023-05-24", 5.25),
    ("2023-07-12", 5.50), ("2023-08-16", 5.50), ("2023-10-04", 5.50),
    ("2023-11-29", 5.50), ("2024-02-28", 5.50), ("2024-04-10", 5.50),
    ("2024-05-22", 5.50), ("2024-07-10", 5.50), ("2024-08-14", 5.25),
    ("2024-10-09", 4.75), ("2024-11-27", 4.25), ("2025-02-19", 3.75),
]

cursor.executemany("""
    INSERT INTO ocr_rates (date, rate)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE rate = VALUES(rate)
""", ocr_data)
print(f"Loaded {len(ocr_data)} OCR rate records.")

# ── 2. NZ Median House Prices by Region ──────────────────────────────────────
# Source: REINZ / Stats NZ regional house price estimates
house_price_data = [
    # (date, region, median_price)
    ("2015-01-01", "Auckland",    640000),  ("2015-01-01", "Wellington",  390000),
    ("2015-01-01", "Canterbury",  370000),  ("2015-01-01", "Waikato",     330000),
    ("2015-01-01", "Bay of Plenty", 350000),("2015-01-01", "Otago",       290000),
    ("2015-01-01", "Northland",   280000),  ("2015-01-01", "Hawke's Bay", 270000),

    ("2016-01-01", "Auckland",    820000),  ("2016-01-01", "Wellington",  430000),
    ("2016-01-01", "Canterbury",  390000),  ("2016-01-01", "Waikato",     370000),
    ("2016-01-01", "Bay of Plenty", 410000),("2016-01-01", "Otago",       320000),
    ("2016-01-01", "Northland",   310000),  ("2016-01-01", "Hawke's Bay", 295000),

    ("2017-01-01", "Auckland",    900000),  ("2017-01-01", "Wellington",  490000),
    ("2017-01-01", "Canterbury",  410000),  ("2017-01-01", "Waikato",     415000),
    ("2017-01-01", "Bay of Plenty", 480000),("2017-01-01", "Otago",       370000),
    ("2017-01-01", "Northland",   350000),  ("2017-01-01", "Hawke's Bay", 330000),

    ("2018-01-01", "Auckland",    860000),  ("2018-01-01", "Wellington",  530000),
    ("2018-01-01", "Canterbury",  430000),  ("2018-01-01", "Waikato",     445000),
    ("2018-01-01", "Bay of Plenty", 510000),("2018-01-01", "Otago",       430000),
    ("2018-01-01", "Northland",   380000),  ("2018-01-01", "Hawke's Bay", 360000),

    ("2019-01-01", "Auckland",    840000),  ("2019-01-01", "Wellington",  570000),
    ("2019-01-01", "Canterbury",  450000),  ("2019-01-01", "Waikato",     480000),
    ("2019-01-01", "Bay of Plenty", 540000),("2019-01-01", "Otago",       480000),
    ("2019-01-01", "Northland",   410000),  ("2019-01-01", "Hawke's Bay", 390000),

    ("2020-01-01", "Auckland",    900000),  ("2020-01-01", "Wellington",  640000),
    ("2020-01-01", "Canterbury",  490000),  ("2020-01-01", "Waikato",     530000),
    ("2020-01-01", "Bay of Plenty", 590000),("2020-01-01", "Otago",       530000),
    ("2020-01-01", "Northland",   460000),  ("2020-01-01", "Hawke's Bay", 430000),

    ("2021-01-01", "Auckland",   1100000),  ("2021-01-01", "Wellington",  830000),
    ("2021-01-01", "Canterbury",  620000),  ("2021-01-01", "Waikato",     700000),
    ("2021-01-01", "Bay of Plenty", 780000),("2021-01-01", "Otago",       700000),
    ("2021-01-01", "Northland",   620000),  ("2021-01-01", "Hawke's Bay", 580000),

    ("2022-01-01", "Auckland",   1200000),  ("2022-01-01", "Wellington",  950000),
    ("2022-01-01", "Canterbury",  750000),  ("2022-01-01", "Waikato",     820000),
    ("2022-01-01", "Bay of Plenty", 870000),("2022-01-01", "Otago",       780000),
    ("2022-01-01", "Northland",   700000),  ("2022-01-01", "Hawke's Bay", 660000),

    ("2023-01-01", "Auckland",   1050000),  ("2023-01-01", "Wellington",  800000),
    ("2023-01-01", "Canterbury",  680000),  ("2023-01-01", "Waikato",     720000),
    ("2023-01-01", "Bay of Plenty", 780000),("2023-01-01", "Otago",       700000),
    ("2023-01-01", "Northland",   620000),  ("2023-01-01", "Hawke's Bay", 580000),

    ("2024-01-01", "Auckland",    980000),  ("2024-01-01", "Wellington",  750000),
    ("2024-01-01", "Canterbury",  650000),  ("2024-01-01", "Waikato",     680000),
    ("2024-01-01", "Bay of Plenty", 730000),("2024-01-01", "Otago",       660000),
    ("2024-01-01", "Northland",   580000),  ("2024-01-01", "Hawke's Bay", 540000),

    ("2026-01-01", "Auckland",   1010000),  ("2026-01-01", "Wellington",  748000),
    ("2026-01-01", "Canterbury",  672000),  ("2026-01-01", "Waikato",     698000),
    ("2026-01-01", "Bay of Plenty", 732000),("2026-01-01", "Otago",       678000),
    ("2026-01-01", "Northland",   572000),  ("2026-01-01", "Hawke's Bay", 538000),

    ("2025-01-01", "Auckland",    995000),  ("2025-01-01", "Wellington",  730000),
    ("2025-01-01", "Canterbury",  660000),  ("2025-01-01", "Waikato",     685000),
    ("2025-01-01", "Bay of Plenty", 720000),("2025-01-01", "Otago",       665000),
    ("2025-01-01", "Northland",   565000),  ("2025-01-01", "Hawke's Bay", 530000),
]

cursor.executemany("""
    INSERT INTO house_prices (date, region, median_price)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE median_price = VALUES(median_price)
""", house_price_data)
print(f"Loaded {len(house_price_data)} house price records.")

# ── 3. Housing Deprivation (Stats NZ 2023 Census) ────────────────────────────
deprivation_data = [
    ("Auckland",           2023, 42800, 2.6),
    ("Canterbury",         2023, 12000, 1.8),
    ("Wellington",         2023, 10200, 1.9),
    ("Waikato",            2023,  9200, 2.1),
    ("Bay of Plenty",      2023,  7100, 2.4),
    ("Northland",          2023,  6100, 4.1),
    ("Manawatu-Whanganui", 2023,  5500, 2.3),
    ("Hawke's Bay",        2023,  4500, 2.7),
    ("Otago",              2023,  4000, 1.7),
    ("Southland",          2023,  2400, 2.1),
    ("Taranaki",           2023,  2000, 1.7),
    ("Gisborne",           2023,  1800, 3.8),
    ("Marlborough",        2023,  1200, 2.0),
    ("West Coast",         2023,  1200, 3.6),
    ("Tasman",             2023,   800, 1.5),
    ("Nelson",             2023,   700, 1.4),
]

cursor.executemany("""
    INSERT INTO housing_deprivation (region, year, estimated_people, rate_pct)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE estimated_people = VALUES(estimated_people), rate_pct = VALUES(rate_pct)
""", deprivation_data)
print(f"Loaded {len(deprivation_data)} housing deprivation records.")

# ── 4. Rental Prices by Region ────────────────────────────────────────────────
# Source: MBIE Tenancy Services bond data via Figure.NZ — median weekly rent (NZD)
rental_data = [
    ("2015-01-01", "Auckland",       480), ("2015-01-01", "Wellington",    420),
    ("2015-01-01", "Canterbury",     395), ("2015-01-01", "Waikato",       350),
    ("2015-01-01", "Bay of Plenty",  395), ("2015-01-01", "Otago",         290),
    ("2015-01-01", "Northland",      330), ("2015-01-01", "Hawke's Bay",   300),

    ("2016-01-01", "Auckland",       500), ("2016-01-01", "Wellington",    450),
    ("2016-01-01", "Canterbury",     380), ("2016-01-01", "Waikato",       370),
    ("2016-01-01", "Bay of Plenty",  450), ("2016-01-01", "Otago",         303),
    ("2016-01-01", "Northland",      350), ("2016-01-01", "Hawke's Bay",   320),

    ("2017-01-01", "Auckland",       520), ("2017-01-01", "Wellington",    500),
    ("2017-01-01", "Canterbury",     380), ("2017-01-01", "Waikato",       390),
    ("2017-01-01", "Bay of Plenty",  460), ("2017-01-01", "Otago",         320),
    ("2017-01-01", "Northland",      380), ("2017-01-01", "Hawke's Bay",   350),

    ("2018-01-01", "Auckland",       540), ("2018-01-01", "Wellington",    540),
    ("2018-01-01", "Canterbury",     390), ("2018-01-01", "Waikato",       410),
    ("2018-01-01", "Bay of Plenty",  495), ("2018-01-01", "Otago",         333),
    ("2018-01-01", "Northland",      405), ("2018-01-01", "Hawke's Bay",   385),

    ("2019-01-01", "Auckland",       550), ("2019-01-01", "Wellington",    575),
    ("2019-01-01", "Canterbury",     400), ("2019-01-01", "Waikato",       440),
    ("2019-01-01", "Bay of Plenty",  525), ("2019-01-01", "Otago",         395),
    ("2019-01-01", "Northland",      450), ("2019-01-01", "Hawke's Bay",   420),

    ("2020-01-01", "Auckland",       575), ("2020-01-01", "Wellington",    590),
    ("2020-01-01", "Canterbury",     410), ("2020-01-01", "Waikato",       470),
    ("2020-01-01", "Bay of Plenty",  555), ("2020-01-01", "Otago",         408),
    ("2020-01-01", "Northland",      460), ("2020-01-01", "Hawke's Bay",   450),

    ("2021-01-01", "Auckland",       600), ("2021-01-01", "Wellington",    600),
    ("2021-01-01", "Canterbury",     480), ("2021-01-01", "Waikato",       510),
    ("2021-01-01", "Bay of Plenty",  620), ("2021-01-01", "Otago",         450),
    ("2021-01-01", "Northland",      520), ("2021-01-01", "Hawke's Bay",   525),

    ("2022-01-01", "Auckland",       600), ("2022-01-01", "Wellington",    588),
    ("2022-01-01", "Canterbury",     510), ("2022-01-01", "Waikato",       530),
    ("2022-01-01", "Bay of Plenty",  640), ("2022-01-01", "Otago",         470),
    ("2022-01-01", "Northland",      560), ("2022-01-01", "Hawke's Bay",   560),

    ("2023-01-01", "Auckland",       650), ("2023-01-01", "Wellington",    650),
    ("2023-01-01", "Canterbury",     555), ("2023-01-01", "Waikato",       560),
    ("2023-01-01", "Bay of Plenty",  683), ("2023-01-01", "Otago",         480),
    ("2023-01-01", "Northland",      563), ("2023-01-01", "Hawke's Bay",   590),

    ("2024-01-01", "Auckland",       650), ("2024-01-01", "Wellington",    640),
    ("2024-01-01", "Canterbury",     580), ("2024-01-01", "Waikato",       570),
    ("2024-01-01", "Bay of Plenty",  705), ("2024-01-01", "Otago",         550),
    ("2024-01-01", "Northland",      580), ("2024-01-01", "Hawke's Bay",   600),

    ("2025-01-01", "Auckland",       650), ("2025-01-01", "Wellington",    600),
    ("2025-01-01", "Canterbury",     590), ("2025-01-01", "Waikato",       570),
    ("2025-01-01", "Bay of Plenty",  680), ("2025-01-01", "Otago",         550),
    ("2025-01-01", "Northland",      580), ("2025-01-01", "Hawke's Bay",   610),
]

cursor.executemany("""
    INSERT INTO rental_prices (date, region, median_weekly_rent)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE median_weekly_rent = VALUES(median_weekly_rent)
""", rental_data)
print(f"Loaded {len(rental_data)} rental price records.")

conn.commit()
cursor.close()
conn.close()
print("\nAll data loaded into MySQL successfully.")
