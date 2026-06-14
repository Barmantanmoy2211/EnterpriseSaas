# MongoDB Collections — Phase 2 (HR Platform)

## employees

HR employee records linked optionally to platform users and org nodes.

| Field | Type | Description |
|-------|------|-------------|
| user_id | ObjectId | Optional link to auth user |
| employee_code | string | Unique per tenant |
| first_name, last_name, email | string | Identity |
| org_node_id | ObjectId | Department/team placement |
| job_title, department | string | Role info |
| employment_type | string | full_time, part_time, contract |
| status | string | active, on_leave, terminated |
| manager_id | ObjectId | Reporting manager |

## job_postings, candidates, job_applications

Recruitment ATS collections for hiring pipeline management.

## attendance_records, leave_types, leave_requests

Time tracking and leave management with workflow integration on leave requests.

## performance_reviews, performance_goals

Performance management cycle and individual goal tracking.

## training_courses, training_enrollments

Learning management and course completion tracking.

## onboarding_templates, onboarding_plans

Configurable onboarding checklists assigned to new employees.

## exit_requests

Offboarding and exit workflow with employee status updates on approval.
