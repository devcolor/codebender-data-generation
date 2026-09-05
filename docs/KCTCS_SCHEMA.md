# KCTCS Schema (Example School)

This documents the Kentucky Community and Technical College System (`KCTCS`) database as an example of how a school extends the base [PDP schema](PDP_SCHEMA.md) with analysis-ready (`ar_kctcs`) and ML prediction data. The same pattern applies to `AL`, `CSUSB`, `KY`, and `OH` (see their respective `ar_*` tables).

Source schema definitions live in `data/predictions/`:
- `kctcs_merged_with_predictions_schema.json` — course-enrollment level
- `kctcs_student_level_with_predictions_schema.json` — student level

## Merged Dataset (Course-Enrollment Level)

Combines cohort data, achievement records, course enrollments, and ML predictions into one row per course enrollment. Includes every field from the [Cohort File](PDP_SCHEMA.md#cohort-file), plus:

- `id` — unique record identifier
- `school` — school identifier (`KCTCS`)
- `dataset_type` — `R` (real) or `S` (synthetic)
- `created_at` — record creation timestamp

## Student-Level Dataset (Aggregated + Predictions)

One row per student, aggregating all of that student's course records plus cohort attributes. Includes the core [Cohort File](PDP_SCHEMA.md#cohort-file) fields, plus:

- `id`, `Student_GUID`, `ar_id` (achievement record ID)

**Aggregated Course Statistics** (computed from the Course File)
- `total_courses_enrolled`, `unique_course_prefixes`
- `total_credits_attempted`, `total_credits_earned`, `avg_credits_per_course`, `course_completion_rate`
- `courses_with_grades`, `average_grade`, `min_grade`, `max_grade`, `grade_std_dev`
- `failing_grades_count`, `passing_rate`
- `core_courses_taken`, `gateway_math_courses`, `gateway_english_courses`, `corequisite_courses`

**Delivery Mix**
- `online_courses`, `face_to_face_courses`, `hybrid_courses`, `pct_online`

**Term Coverage**
- `unique_academic_years`, `unique_academic_terms`, `fall_courses`, `spring_courses`, `summer_courses`

**Instructor Mix**
- `courses_with_fulltime_instructors`, `courses_with_parttime_instructors`

**Cross-Institution**
- `enrolled_other_institutions`

**Achievement Record (`ar_`) Enrichment**
- `ar_naspa_first_gen`
- `ar_years_to_bachelors_cohort`, `ar_years_to_bachelor_other`
- `ar_first_year_bachelors_cohort`, `ar_first_year_bachelor_other`
- `ar_years_to_assoc_cert_cohort`, `ar_years_to_assoc_cert_other`
- `ar_first_year_assoc_cert_cohort`, `ar_first_year_assoc_cert_other`

## Getting the Live Schema

To pull the actual, current schema (columns, types, indexes, record counts) directly from the database instead of relying on this doc:

```bash
# General-purpose viewer for any configured database
python dboperations/view_schema.py --database KCTCS

# KCTCS-specific schema export scripts
python dboperations/testing/get_kctcs_complete_schema.py
python dboperations/testing/export_kctcs_schema.py
```

## Related Docs

- [`PDP_SCHEMA.md`](PDP_SCHEMA.md) — the base Cohort/Course/Financial Aid structure shared by all schools
- [Main README](../README.md#database-operations) — database setup and generation commands
