# Normalization Report — Gym & Fitness Management System

## Original Schema Overview

The database consists of 5 tables:
- `trainers` — gym staff and their specialities
- `members` — gym members and membership details
- `equipment` — gym equipment inventory
- `classes` — fitness classes offered
- `class_enrollments` — junction table linking members to classes

---

## Original Functional Dependencies

### trainers
- trainer_id → first_name, last_name, email, phone, speciality, hourly_rate, created_at

### members
- member_id → first_name, last_name, email, phone, date_of_birth, membership_type, membership_start_date, membership_end_date, trainer_id, created_at
- **membership_start_date + membership_end_date → membership_duration_days** ⚠️ (transitive)

### equipment
- equipment_id → equipment_name, category, quantity, condition_status, purchase_date, last_updated

### classes
- class_id → class_name, trainer_id, class_date, start_time, duration_mins, max_capacity, room, created_at

### class_enrollments
- enrollment_id → member_id, class_id, attendance, enrolled_at
- (member_id, class_id) → attendance, enrolled_at

---

## First Normal Form (1NF) Analysis

**Definition:** Every column must contain atomic (indivisible) values, no repeating groups, and a primary key must exist.

| Table | Atomic Values | No Repeating Groups | Primary Key | 1NF Status |
|-------|--------------|--------------------:|-------------|------------|
| trainers | ✅ | ✅ | trainer_id | ✅ PASS |
| members | ✅ | ✅ | member_id | ✅ PASS |
| equipment | ✅ | ✅ | equipment_id | ✅ PASS |
| classes | ✅ | ✅ | class_id | ✅ PASS |
| class_enrollments | ✅ | ✅ | enrollment_id | ✅ PASS |

**All tables pass 1NF.**

---

## Second Normal Form (2NF) Analysis

**Definition:** Must be in 1NF and every non-key attribute must depend on the WHOLE primary key (no partial dependencies). Only applies to tables with composite keys.

The only table with a meaningful composite candidate key is `class_enrollments` (member_id + class_id).

- `attendance` depends on the full (member_id + class_id) combination ✅
- `enrolled_at` depends on the full (member_id + class_id) combination ✅

No partial dependencies exist anywhere.

**All tables pass 2NF.**

---

## Third Normal Form (3NF) Analysis

**Definition:** Must be in 2NF and no non-key attribute should depend on another non-key attribute (no transitive dependencies).

### Violation Found — members table

The column `membership_duration_days` is calculated directly from two other non-key columns:

```
membership_duration_days = DATEDIFF(membership_end_date, membership_start_date)
```

This is a **transitive dependency**:
```
member_id → membership_start_date → membership_duration_days
member_id → membership_end_date  → membership_duration_days
```

Storing a value that is fully derivable from other columns violates 3NF because:
- It creates **update anomalies** — if membership_end_date changes, duration_days must also be manually updated
- It creates **insertion anomalies** — new members need duration calculated before insert
- It creates **redundant data** — the information already exists in the two date columns

### Fix — Remove the derived column

`membership_duration_days` is dropped from the `members` table. It will be calculated dynamically in queries using `DATEDIFF(membership_end_date, membership_start_date)` wherever needed.

---

## Anomaly Identification

### Update Anomaly (members table)
If a member's `membership_end_date` is extended, `membership_duration_days` must also be manually updated. Forgetting to do so leaves stale/incorrect data in the database.

### Insertion Anomaly (members table)
When inserting a new member, the application must pre-calculate `membership_duration_days` before inserting, which creates unnecessary application-layer complexity.

### Deletion Anomaly
No deletion anomalies were found. Deleting a member's enrollment does not accidentally lose trainer or class data since those are in separate tables.

---

## Decomposition Steps

Only one change is required to achieve full 3NF:

**Step 1:** Remove `membership_duration_days` column from `members` table.

**Before (violates 3NF):**
```sql
members (
    member_id PK,
    first_name, last_name, email, phone,
    date_of_birth,
    membership_type,
    membership_start_date,
    membership_end_date,
    trainer_id FK,
    created_at,
    membership_duration_days  -- ⚠️ derived column, violates 3NF
)
```

**After (3NF compliant):**
```sql
members (
    member_id PK,
    first_name, last_name, email, phone,
    date_of_birth,
    membership_type,
    membership_start_date,
    membership_end_date,
    trainer_id FK,
    created_at
)
```

Duration is now always calculated dynamically:
```sql
SELECT DATEDIFF(membership_end_date, membership_start_date) AS membership_duration_days
FROM members;
```

---

## Final Relational Schema (3NF Compliant)

```
trainers (trainer_id PK, first_name, last_name, email, phone, speciality, hourly_rate, created_at)

members (member_id PK, first_name, last_name, email UNIQUE, phone, date_of_birth,
         membership_type, membership_start_date, membership_end_date,
         trainer_id FK → trainers, created_at)

equipment (equipment_id PK, equipment_name, category, quantity,
           condition_status, purchase_date, last_updated)

classes (class_id PK, class_name, trainer_id FK → trainers,
         class_date, start_time, duration_mins, max_capacity, room, created_at)

class_enrollments (enrollment_id PK, member_id FK → members,
                   class_id FK → classes, attendance, enrolled_at)
```

### Relationships
- `trainers` ||--o{ `members` — one trainer can be assigned to many members
- `trainers` ||--o{ `classes` — one trainer leads many classes
- `members`  ||--o{ `class_enrollments` — one member can enroll in many classes
- `classes`  ||--o{ `class_enrollments` — one class can have many enrollments

---

## Summary of Changes

| Change | Reason |
|--------|--------|
| Removed `membership_duration_days` from `members` | Transitive dependency — derived from two other columns, violates 3NF |

All other tables were already in 3NF and required no changes.
