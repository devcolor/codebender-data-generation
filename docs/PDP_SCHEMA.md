# PDP Analysis-Ready File Schema

This describes the standardized **Postsecondary Data Partnership (PDP)** Analysis-Ready (AR) file structure used across all five institutions (`AL`, `CSUSB`, `KCTCS`, `KY`, `OH`). Every school's database follows this same base structure for `cohort`, `course`, and `financial_aid`, which is why data generation, uploads, and querying can treat them consistently across schools.

Field templates live in `data/seed_data00/`, `data/seed_data01/`, and `data/seed_ar/`.

## Cohort File

One row per student per cohort. Captures a student's entry characteristics and multi-year outcomes.

**Identifiers**
- `Institution_ID`, `Cohort` (e.g. `2019-20`), `Cohort_Term` (`FALL`/`SPRING`/`SUMMER`), `Student_GUID`

**Demographics**
- `Student_Age`, `Race`, `Ethnicity`, `Gender`, `First_Gen`, `NASPA_First_Generation`, `Incarcerated_Status`, `Military_Status`, `Employment_Status`, `Disability_Status`

**Enrollment**
- `Enrollment_Type` (First-Time, Transfer-In, Re-admit, ...), `Enrollment_Intensity_First_Term` (Full-Time/Part-Time), `Attendance_Status_Term_1`, `Dual_and_Summer_Enrollment`, `Special_Program`

**Placement**
- `Math_Placement`, `English_Placement`, `Reading_Placement`

**Program & Credential**
- `Credential_Type_Sought_Year_1`, `Program_of_Study_Term_1`, `Program_of_Study_Year_1` (CIP codes)

**Academic Performance**
- `GPA_Group_Term_1`, `GPA_Group_Year_1`
- `Number_of_Credits_Attempted_Year_1`..`_Year_4`, `Number_of_Credits_Earned_Year_1`..`_Year_4`

**Gateway & Developmental Coursework**
- `Gateway_Math_Status`, `Gateway_English_Status`
- `AttemptedGatewayMathYear1`, `AttemptedGatewayEnglishYear1`, `CompletedGatewayMathYear1`, `CompletedGatewayEnglishYear1`
- `GatewayMathGradeY1`, `GatewayEnglishGradeY1`
- `AttemptedDevMathY1`, `AttemptedDevEnglishY1`, `CompletedDevMathY1`, `CompletedDevEnglishY1`

**Outcomes**
- `Retention`, `Persistence` (0/1 indicators)
- `Years_to_Bachelors_at_cohort_inst.`, `Years_to_Bachelor_at_other_inst.`
- `Years_to_Associates_or_Certificate_at_cohort_inst.`, `Years_to_Associates_or_Certificate_at_other_inst.`
- `First_Year_to_Bachelors_at_cohort_inst.`, `First_Year_to_Bachelor_at_other_inst.`
- `Years_of_Last_Enrollment_at_cohort_institution`, `Years_of_Last_Enrollment_at_other_institution`
- `Time_to_Credential`

**Transfer Institution Details** (repeated for "Most Recent" and "First" Bachelor's / Associate's-Certificate / Last Enrollment at another institution)
- `..._STATE`, `..._CARNEGIE` (Carnegie classification), `..._LOCALE` (Urban/Suburb/Town-Rural)

## Course File

One row per student per course enrollment.

**Identifiers**
- `Student_GUID`, `Institution_ID`, `Cohort`, `Cohort_Term`

**Demographics** (denormalized onto each course row)
- `Student_Age`, `Race`, `Ethnicity`, `Gender`

**Term**
- `Academic_Year`, `Academic_Term`

**Course Details**
- `Course_Prefix`, `Course_Number`, `Section_ID`, `Course_Name`, `Course_CIP`, `Course_Type` (`CU` = credit/university, `CC` = developmental/co-req, etc.)
- `Math_or_English_Gateway`, `Co-requisite_Course`
- `Course_Begin_Date`, `Course_End_Date`

**Performance**
- `Grade`, `Number_of_Credits_Attempted`, `Number_of_Credits_Earned`

**Delivery & Classification**
- `Delivery_Method` (`O` online, `H` hybrid, `F` face-to-face, ...)
- `Core_Course`, `Core_Course_Type`, `Core_Competency_Completed`

**Instructor**
- `Course_Instructor_Employment_Status`, `Course_Instructor_Rank`

**Cross-Institution**
- `Enrolled_at_Other_Institution(s)`
- `Enrollment_Record_at_Other_Institution(s)_STATE(s)`, `..._CARNEGIE(s)`, `..._LOCALE(s)`

**Other**
- `Credential_Engine_Identifier`, `Term_Program_of_Study`

## Financial Aid File

Captures financial aid and cost-of-attendance data per student per year (Pell/loan/grant amounts, cost of attendance, need/merit aid, etc.). See the `financialaid_analysis_ready_file_template.xlsx` template in `data/seed_data00/` (and `data/seed_data01/`) for the exact field list, since it wasn't included inline here.

## How This Maps to the Databases

Each school's `cohort`, `course`, and `financial_aid` tables mirror this structure, with an added `school` column and shared keys (`Student_GUID`, `Institution_ID`, `Cohort`, `Academic_Year`) for cross-table and cross-school joins. See the main [README](../README.md#database-operations) for setup/generation commands and [`KCTCS_SCHEMA.md`](KCTCS_SCHEMA.md) for an example of how one school extends this base structure with analysis-ready and ML prediction fields.
