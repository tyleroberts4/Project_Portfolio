-- Create database schema
DROP SCHEMA IF EXISTS `GSB_520_Project_DB`;
CREATE SCHEMA `GSB_520_Project_DB`;
USE `GSB_520_Project_DB`;

-- LOCATION table - stores geographical and road information
CREATE TABLE `LOCATION` (
  `location_id` INT NOT NULL AUTO_INCREMENT,
  `latitude` DECIMAL(10,6) NOT NULL,
  `longitude` DECIMAL(10,6) NOT NULL,
  `area_type` VARCHAR(45) NOT NULL ,
  `local_authority` VARCHAR(75) NOT NULL,
  `junction_type` TEXT NULL ,
  `junction_control` TEXT NOT NULL,
  PRIMARY KEY (`location_id`),
  INDEX `idx_area_type` (`area_type`),
  INDEX `idx_lat_long` (`latitude`, `longitude`)
);

-- OCCUPATION table - reference table for customer occupations
CREATE TABLE `OCCUPATION` (
  `occupation_id` INT NOT NULL AUTO_INCREMENT,
  `occupation_name` VARCHAR(45) NOT NULL,
  `avg_salary` DECIMAL(10,2) NULL,
  PRIMARY KEY (`occupation_id`),
  INDEX `idx_occupation_name` (`occupation_name`) 
) ;

-- POSTAL_CODE table - stores geographic region information
CREATE TABLE `POSTAL_CODE` (
  `postal_code` INT NOT NULL AUTO_INCREMENT,
  `city` VARCHAR(45) NOT NULL,
  `state` VARCHAR(45) NOT NULL,
  `county` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`postal_code`),
  INDEX `idx_state_city` (`state`, `city`) 
);

-- DRIVING_RECORD table - tracks customer driving history
CREATE TABLE `DRIVING_RECORD` (
  `driving_record_id` INT NOT NULL AUTO_INCREMENT,
  `driving_years` VARCHAR(45) NOT NULL ,
  `speeding_count` INT NOT NULL DEFAULT 0,
  `dui_count` INT NOT NULL DEFAULT 0,
  `accident_count` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`driving_record_id`)
);

-- CUSTOMER table - core customer information
CREATE TABLE `CUSTOMER` (
  `customer_id` INT NOT NULL AUTO_INCREMENT,
  `full_name` VARCHAR(120) NOT NULL,
  `phone_number` VARCHAR(20) NOT NULL,
  `email` VARCHAR(100) NULL,
  `credit_score` INT NOT NULL,
  `children_count` INT NOT NULL DEFAULT 0,
  `household_income` DECIMAL(10,2) NOT NULL,
  `gender` VARCHAR(10) NOT NULL,
  `race` VARCHAR(45) NULL,
  `age_group` VARCHAR(45) NOT NULL ,
  `marital_status` VARCHAR(20) NOT NULL,
  `income_level` VARCHAR(45) NULL,
  `occupation_id` INT NOT NULL,
  `POSTAL_Postal_Code` INT NOT NULL,
  `DRIVING_RECORD_driving_record_id` INT NOT NULL,
  PRIMARY KEY (`customer_id`),
  INDEX `fk_CUSTOMER_OCCUPATION_idx` (`occupation_id`),
  INDEX `idx_credit_score` (`credit_score`),
  INDEX `fk_CUSTOMER_POSTAL_CODE1_idx` (`POSTAL_Postal_Code`),
  INDEX `fk_CUSTOMER_DRIVING_RECORD1_idx` (`DRIVING_RECORD_driving_record_id`),
  CONSTRAINT `fk_CUSTOMER_OCCUPATION`
    FOREIGN KEY (`occupation_id`)
    REFERENCES `OCCUPATION` (`occupation_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_CUSTOMER_POSTAL_CODE1`
    FOREIGN KEY (`POSTAL_Postal_Code`)
    REFERENCES `POSTAL_CODE` (`postal_code`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_CUSTOMER_DRIVING_RECORD1`
    FOREIGN KEY (`DRIVING_RECORD_driving_record_id`)
    REFERENCES `DRIVING_RECORD` (`driving_record_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

-- ACCIDENT_RECORD table - details of accidents involving customers
CREATE TABLE `ACCIDENT_RECORD` (
  `accident_id` INT NOT NULL AUTO_INCREMENT,
  `accident_date` DATE NOT NULL,
  `accident_time` TIME NOT NULL,
  `severity_level` VARCHAR(45) NOT NULL,
  `casualties_count` INT NOT NULL DEFAULT 0,
  `vehicles_count` INT NOT NULL DEFAULT 0,
  `police_dept` VARCHAR(45) NULL,
  `road_conditions` VARCHAR(45) NOT NULL ,
  `speed_limit` INT NOT NULL ,
  `carriageway_hazards` TEXT NULL,
  `road_type` VARCHAR(45) NULL,
  `day_of_week` VARCHAR(45) NULL,
  `light_condition` TEXT NULL ,
  `weather_condition` TEXT NULL ,
  `location_id` INT NOT NULL,
  `CUSTOMER_customer_id` INT NOT NULL,
  PRIMARY KEY (`accident_id`),
  INDEX `fk_ACCIDENT_LOCATION_idx` (`location_id`),
  INDEX `idx_accident_date` (`accident_date`),
  INDEX `idx_severity` (`severity_level`),
  INDEX `fk_ACCIDENT_RECORD_CUSTOMER1_idx` (`CUSTOMER_customer_id`),
  CONSTRAINT `fk_ACCIDENT_LOCATION`
    FOREIGN KEY (`location_id`)
    REFERENCES `LOCATION` (`location_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_ACCIDENT_RECORD_CUSTOMER1`
    FOREIGN KEY (`CUSTOMER_customer_id`)
    REFERENCES `CUSTOMER` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


-- VEHICLE table - detailed vehicle information

CREATE TABLE `VEHICLE` (
  `vin` VARCHAR(17) NOT NULL ,
  `make` VARCHAR(45) NOT NULL,
  `model` VARCHAR(45) NOT NULL,
  `year` YEAR NOT NULL,
  `mileage` INT NOT NULL DEFAULT 0,
  `price` DECIMAL(10,2) NOT NULL,
  `vehicle_type` VARCHAR(45) NOT NULL,
  `door_count` INT NOT NULL,
  `color` VARCHAR(45) NOT NULL,
  `clean_title` VARCHAR(45) NOT NULL,
  `engine_type` VARCHAR(45) NOT NULL ,
  `warranty_years` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`vin`),
  INDEX `idx_make_model` (`make`, `model`),
  INDEX `idx_year` (`year`),
  INDEX `idx_price` (`price`) 
);

-- CUSTOMER_HAS_VEHICLE relationship table
CREATE TABLE `CUSTOMER_HAS_VEHICLE` (
  `customer_id` INT NOT NULL,
  `vin` VARCHAR(17) NOT NULL,
  PRIMARY KEY (`customer_id`, `vin`),
  INDEX `fk_CUSTOMER_HAS_VEHICLE_VEHICLE_idx` (`vin`),
  CONSTRAINT `fk_CUSTOMER_HAS_VEHICLE_CUSTOMER`
    FOREIGN KEY (`customer_id`)
    REFERENCES `CUSTOMER` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_CUSTOMER_HAS_VEHICLE_VEHICLE`
    FOREIGN KEY (`vin`)
    REFERENCES `VEHICLE` (`vin`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


-- LOAN table - financial loan information
CREATE TABLE `LOAN` (
  `loan_id` INT NOT NULL AUTO_INCREMENT,
  `risk_score` DECIMAL(7,2) NOT NULL,
  `loan_term_months` INT NOT NULL,
  `loan_amount` DECIMAL(10,2) NOT NULL,
  `status` VARCHAR(20) NOT NULL ,
  PRIMARY KEY (`loan_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_risk_score` (`risk_score`) 
);

-- CUSTOMER_has_LOAN relationship table
CREATE TABLE `CUSTOMER_has_LOAN` (
  `loan_id` INT NOT NULL,
  `CUSTOMER_customer_id` INT NOT NULL,
  PRIMARY KEY (`loan_id`, `CUSTOMER_customer_id`),
  INDEX `fk_LOAN_has_CUSTOMER_CUSTOMER1_idx` (`CUSTOMER_customer_id`),
  INDEX `fk_LOAN_has_CUSTOMER_LOAN1_idx` (`loan_id`),
  CONSTRAINT `fk_LOAN_has_CUSTOMER_LOAN1`
    FOREIGN KEY (`loan_id`)
    REFERENCES `LOAN` (`loan_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_LOAN_has_CUSTOMER_CUSTOMER1`
    FOREIGN KEY (`CUSTOMER_customer_id`)
    REFERENCES `CUSTOMER` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ;

-- Load The Data 

-- Adding a new column
ALTER TABLE VEHICLE
ADD COLUMN risk_flag VARCHAR(20) DEFAULT 'Normal';

-- Updating the Risk_Flag column for the table
SET SQL_SAFE_UPDATES = 0;

UPDATE VEHICLE
SET risk_flag = 
  CASE
    WHEN year < YEAR(CURDATE()) - 10 THEN 'High Risk'
    ELSE 'Normal'
  END;

SET SQL_SAFE_UPDATES = 1;

-- Adding CHECK Constraints
ALTER TABLE CUSTOMER
ADD CONSTRAINT chk_email CHECK (email LIKE '%_@_%._%'),
ADD CONSTRAINT chk_credit_score_range CHECK (credit_score > 0);

ALTER TABLE VEHICLE
ADD CONSTRAINT chk_year CHECK (year > 1900),
ADD CONSTRAINT chk_mileage_non_negative CHECK (mileage >= 0),
ADD CONSTRAINT chk_price_non_negative CHECK (price >= 0),
ADD CONSTRAINT chk_door_count CHECK (door_count BETWEEN 1 AND 6),
ADD CONSTRAINT chk_clean_title CHECK (clean_title IN ('Yes', 'No')),
ADD CONSTRAINT chk_engine_type CHECK (engine_type IN ('V4', 'V6', 'V8', 'V12'));

ALTER TABLE LOCATION 
ADD CONSTRAINT chk_latitude CHECK (latitude BETWEEN -90 AND 90),
ADD CONSTRAINT chk_longitude CHECK (longitude BETWEEN -180 AND 180);

ALTER TABLE LOAN
ADD CONSTRAINT chk_loan_amount CHECK (loan_amount > 0),
ADD CONSTRAINT chk_loan_term CHECK (loan_term_months > 0);

-- Adding the Triggers

-- Updating the customer's credit score if a new loan is added with a high risk score
DELIMITER //
CREATE TRIGGER update_credit_score_on_high_risk_loan
AFTER INSERT ON CUSTOMER_has_LOAN
FOR EACH ROW
BEGIN
  DECLARE risk DECIMAL(7,2);
  SELECT risk_score INTO risk FROM LOAN WHERE loan_id = NEW.loan_id;
  
  IF risk > 70 THEN
    UPDATE CUSTOMER
    SET credit_score = credit_score - 20
    WHERE customer_id = NEW.CUSTOMER_customer_id;
  END IF;
END;
//
DELIMITER;

-- Adding the accident_count in DRIVING_RECORD when new accident is added
DELIMITER //
CREATE TRIGGER accident_record_after_insert
AFTER INSERT ON ACCIDENT_RECORD
FOR EACH ROW
BEGIN
  UPDATE DRIVING_RECORD dr
  JOIN CUSTOMER c ON c.DRIVING_RECORD_driving_record_id = dr.driving_record_id
  SET dr.accident_count = dr.accident_count + 1
  WHERE c.customer_id = NEW.CUSTOMER_customer_id;
END;
//
DELIMITER ;


-- Trigger to validate loan data before insert
DELIMITER //

CREATE TRIGGER loan_before_insert
BEFORE INSERT ON LOAN
FOR EACH ROW
BEGIN
  IF NEW.loan_amount <= 0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Loan amount must be greater than zero';
  END IF;

  IF NEW.loan_term_months <= 0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Loan term must be greater than zero months';
  END IF;
END;
//

DELIMITER ;

-- Flagging the vehicle risk trigger
DELIMITER //

CREATE TRIGGER vehicle_risk_flag_before_insert
BEFORE INSERT ON VEHICLE
FOR EACH ROW
BEGIN
  DECLARE currentYear INT;
  SET currentYear = YEAR(CURDATE());

  IF NEW.year < currentYear - 10 THEN
    SET NEW.risk_flag = 'High Risk';
  ELSE
    SET NEW.risk_flag = 'Normal';
  END IF;
END;
//

DELIMITER ;

-- Adding Stored Views

-- Viewing the Customer with approved loan status
CREATE VIEW vw_active_customer_loans AS
SELECT c.customer_id, c.full_name, l.loan_id, l.status
FROM CUSTOMER c
JOIN CUSTOMER_has_LOAN chl ON c.customer_id = chl.CUSTOMER_customer_id
JOIN LOAN l ON chl.loan_id = l.loan_id
WHERE l.status = 'Approved';

-- Viewing the accidents record from last 3 years

CREATE VIEW vw_recent_accidents AS
SELECT ar.accident_id, ar.accident_date, ar.severity_level, 
		c.customer_id, c.full_name
FROM ACCIDENT_RECORD ar
JOIN CUSTOMER c ON ar.CUSTOMER_customer_id = c.customer_id
WHERE ar.accident_date > CURDATE() - INTERVAL 3 YEAR;

-- Adding a Procedure
-- Procedure to get a summary of loan by customer ID

DELIMITER //
CREATE PROCEDURE GetCustomerLoanSummary(IN input_customer_id INT)
BEGIN
  SELECT 
    c.customer_id,
    c.full_name,
    COUNT(l.loan_id) AS total_loans,
    SUM(l.loan_amount) AS total_loan_amount,
    AVG(l.loan_term_months) AS average_loan_term
  FROM CUSTOMER c
  JOIN CUSTOMER_has_LOAN ch ON c.customer_id = ch.CUSTOMER_customer_id
  JOIN LOAN l ON ch.loan_id = l.loan_id
  WHERE c.customer_id = input_customer_id
  GROUP BY c.customer_id;
END;
//
DELIMITER ;


CALL GetCustomerLoanSummary(101);