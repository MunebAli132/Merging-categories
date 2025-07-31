# 🧩 Category Merger Service

A Flask-based service to manage and intelligently merge a tree of fashion item categories to reduce the overhead of deploying per-category machine learning models.

---

## 🚀 Features

- Create, delete, and query hierarchical fashion categories
- Merge categories into **tree nodes** under item count constraints
- Dynamic, deterministic merging logic (respects current state)
- API endpoints to query tree node structure
- Lightweight and extensible implementation

---

## 📦 Requirements

- Python 3.11
- Dependencies listed in `requirements.txt`

Install using:

```bash
pip install -r requirements.txt
