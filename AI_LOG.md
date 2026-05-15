# AI Assistance Log

This file documents all instances of Generative AI assistance used in this project, as required by the course AI policy.

---

## Entry 1

**Tool:** Claude (Anthropic)

**Prompt:**
"Help me with my database assignment. I need to build a Gym & Fitness Management System database with DDL, DML, and DQL files for MySQL."

**AI Output Summary:**
Claude helped design the database schema with 5 tables (trainers, members, equipment, classes, class_enrollments), generated DDL with proper data types, constraints, primary keys and foreign keys, DML with sample data and required operations, and DQL with 9 retrieval queries using GROUP BY, HAVING, MAX, JOIN, UPPER, EXTRACT, COUNT, DISTINCT, AVG, ORDER BY, LIMIT, WHERE NOT IN, and NOT NULL.

**My Modification:**
I replaced all sample data (names, emails, phone numbers) with my own custom data. I also manually typed all SQL into the ZyBook lab environment and fixed several typos that occurred during manual entry. I verified all outputs matched the expected results before submitting.

---

## Entry 2

**Tool:** Claude (Anthropic)

**Prompt:**
"Help me with Project 3 — normalization to 3NF and building a Flask web app for my Gym Management System."

**AI Output Summary:**
Claude analyzed the existing schema for 1NF, 2NF, and 3NF compliance, identified that `membership_duration_days` violated 3NF as a derived column, generated the NORMALIZATION.md report, the final 3NF schema.sql, the complete Flask app.py with all routes, all HTML templates using Bootstrap 5, and the README.md.

**My Modification:**
I reviewed all routes in app.py and verified the database column names matched my actual schema (especially `speciality` spelling). I updated the database credentials in `get_db()` to match my local MySQL setup. I tested each page individually and confirmed all CRUD operations worked correctly.

---
