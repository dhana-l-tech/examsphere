# ⬡ ExamSphere – Smart Online Examination System

A full-stack online examination platform built with Flask + SQLite.

## 🚀 Quick Start

```bash
cd examsphere
pip install flask
python app.py
```
Then open: **http://localhost:5000**

## 🔐 Login Credentials

| Role    | Email              | Password |
|---------|--------------------|----------|
| Admin   | admin@exam.com     | admin123 |
| Student | dhan@exam.com      | 1234     |
| Student | priya@exam.com     | 1234     |
| Student | karthik@exam.com   | 1234     |
| ...     | [name]@exam.com    | 1234     |

All 15 students share password: **1234**

## 📁 Project Structure

```
examsphere/
├── app.py              # Flask backend + all routes
├── examsphere.db       # SQLite database (auto-created)
├── requirements.txt
└── templates/
    ├── index.html          # Landing page
    ├── login.html          # Role-based login
    ├── student_dashboard.html
    ├── admin_dashboard.html
    └── exam_page.html
```

## 🗄️ Database Schema

- **students** — id, name, email, password, department, year
- **exams** — exam_id, subject, duration, total_marks, description
- **questions** — question_id, exam_id, question_text, options A-D, correct_answer
- **results** — result_id, student_id, exam_id, score, total_marks, date
- **announcements** — id, title, message, created_at

## ✨ Features

### Student
- Dashboard with stats
- Browse & take timed exams
- MCQ with navigation sidebar
- Instant score + grade on submit
- Result history & progress charts
- Profile page

### Admin
- Full overview dashboard
- Analytics & grade distribution
- Leaderboard (top students)
- CRUD: Students, Exams, Questions
- View all results
- Post announcements
