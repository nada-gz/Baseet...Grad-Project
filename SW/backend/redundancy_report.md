# Database Redundancy Report

After auditing your database, I have identified several tables and records that are no longer part of the primary teacher-driven content flow.

## 1. Redundant Legacy Tables
These tables were used in the old system and have been replaced by the `content_` prefixed tables. Since your frontend is now updated to fetch from the new endpoints, these are safe to remove **after** you ensure all student progress is linked.

*   `courses`: Replaced by `content_courses`.
*   `milestones`: Replaced by `milestone_number` field in `content_lessons`.
*   `materials`: Replaced by `content_materials`.

## 2. Redundant Columns in "Instance" Tables
In the `lessons` and `assignments` tables (where student progress is kept), some columns are now duplicates of what exists in the templates:
*   `lessons.title` and `lessons.description`: These are now optional because the dashboard fetches them from the `content_lessons` template.
*   `assignments.title`, `assignments.description`, and `assignments.file_url`: Now fetched from `content_assignments`.

## 3. Orphaned Student Lessons
You have **7** lesson records in your `lessons` table, but only **4** are currently linked to the new teacher templates. 
- **Matched**: "الشمس", "النباتات", "الزراعة", "القمر".
- **Orphaned (Legacy)**: "الهضاب", "البناء الضوئي", "الطاقة".

## Recommendation

Since you want to avoid any risk to your current working result, **you do not need to do anything right now.** The system is designed to "fall back" to legacy data if needed.

However, if you want a cleaner structure, run this SQL script in pgAdmin:

```sql
-- 1. Link orphaned lessons to their new templates
UPDATE lessons SET content_lesson_id = 2 WHERE title = 'البناء الضوئي' AND content_lesson_id IS NULL;
UPDATE lessons SET content_lesson_id = 1 WHERE title = 'الطاقة' AND content_lesson_id IS NULL;

-- 2. Once linkage is done, these legacy tables are Truly Dead
-- (Optional: only run if you want to save space/clutter)
-- DROP TABLE materials;
-- DROP TABLE courses CASCADE;
-- DROP TABLE milestones CASCADE;
```

> [!NOTE]
> The lesson "الهضاب" has no template in your new content. If you want to keep it, do not delete the legacy data yet.
