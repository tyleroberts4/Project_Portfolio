# SQL Auto Loan Database

A MySQL database project for managing auto loan portfolios with customer, vehicle, accident, and location data. Built for risk analysis, portfolio reporting, and driving-behavior insights.

## Overview

This project defines a relational schema and analytical queries for an auto-loan and accident-reporting system. It includes:

- **Schema** – Tables for customers, vehicles, loans, driving records, accident records, locations, and occupations
- **Constraints & triggers** – Data validation, risk-flag logic, and automatic credit/accident counters
- **Views & stored procedure** – Active loans, recent accidents, and customer loan summary
- **Analytical queries** – State-level exposure, driver risk ranking, high-balance customers, accident hotspots, and low-risk/high-risk segments

## Tech Stack

- **Database:** MySQL (5.7+ / 8.x)
- **Tools:** MySQL Workbench (optional, for ERD)

## Project Structure

| File | Description |
|------|-------------|
| `Schema.sql` | Creates database `GSB_520_Project_DB`, all tables, indexes, constraints, triggers, views, and stored procedure |
| `DB_Data.sql` | Sample/seed data (INSERTs) for all tables (~19 MB) |
| `Database_Queries.sql` | Analytical queries for portfolio and risk reporting |
| `ERD_Image.png` | Entity-relationship diagram |
| `DB_ERD.mwb` | MySQL Workbench model (optional) |
| `Kaggle_Data.xlsx` | Source dataset reference (if applicable) |

## Setup

### Prerequisites

- MySQL Server (5.7+ or 8.x)
- MySQL client or MySQL Workbench

### Run Order

Execute scripts in this order:

1. **Schema** – creates database and objects  
   ```bash
   mysql -u your_user -p < Schema.sql
   ```
2. **Data** – loads seed data  
   ```bash
   mysql -u your_user -p GSB_520_Project_DB < DB_Data.sql
   ```
3. **Queries** – run analytical queries as needed  
   ```bash
   mysql -u your_user -p GSB_520_Project_DB < Database_Queries.sql
   ```

Or open each file in MySQL Workbench and run in the same order.

### Notes

- `DB_Data.sql` is large (~19 MB). GitHub allows files up to 100 MB, so the push will succeed. If you prefer a smaller repo, you can replace it with a smaller sample and document the full dataset elsewhere.
- The schema uses `GSB_520_Project_DB` as the database name; change it in `Schema.sql` if you need a different name.

## Database Highlights

### Main Tables

- **CUSTOMER** – Demographics, credit score, income, occupation, postal code, driving record
- **VEHICLE** – VIN, make, model, year, price, mileage, engine type, risk flag
- **LOAN** – Loan amount, term, risk score, status
- **DRIVING_RECORD** – Years driving, speeding/DUI/accident counts
- **ACCIDENT_RECORD** – Date, severity, location, conditions, linked to customer
- **LOCATION** – Lat/long, area type, junction info, local authority
- **OCCUPATION** – Reference table for occupation names and average salary
- **POSTAL_CODE** – City, state, county

### Features

- CHECK constraints on email, credit score, vehicle year/mileage/price, loan amount/term, coordinates
- Triggers: high-risk loan → credit score adjustment; new accident → driving record accident count; loan/vehicle validation and risk-flag assignment
- Views: `vw_active_customer_loans`, `vw_recent_accidents`
- Stored procedure: `GetCustomerLoanSummary(customer_id)`

## Analytical Queries (Database_Queries.sql)

1. **State loan exposure** – Approved loan volume and average risk by state  
2. **Driver risk ranking** – Customers by accidents, DUI, and speeding  
3. **High-balance customers** – Total loan balance above portfolio average  
4. **Accident hotspots** – Locations with above-average accident counts  
5. **Low-risk customers** – Clean driving, no accidents, with loans (e.g. for marketing)  
6. **High-risk with exposure** – Approved loans + accidents (e.g. for risk review)

## License

This project is for portfolio and educational use. Add a `LICENSE` file if you want to specify terms (e.g. MIT).
