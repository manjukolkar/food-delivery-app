# 🍔 FoodieHub — Food Delivery Web App

A Swiggy/Zomato-inspired food delivery web app built with **Flask + SQLite**.

## ✨ Features

- 👤 User registration, login, logout (password hashing)
- 🍕 Browse food items (Swiggy-style cards)
- 🔍 Live search by food name
- 🏷️ Filter by category (Pizza, Burger, Biryani, etc.)
- 🛒 Add to cart with `− n +` counter
- 💾 Cart persists per user (SQLite)
- 🎨 Responsive, styled UI

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3, Flask |
| Database | SQLite (via Flask-SQLAlchemy) |
| Auth | Flask-Login |
| Frontend | Jinja2 + HTML + CSS |
| Version | Git / GitHub |

## 📁 Project Structure


## 🚀 Quick Start

See [SETUP.md](SETUP.md) for detailed setup instructions.

```bash
git clone <your-repo-url>
cd food-delivery-app
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
# or: venv\Scripts\activate.bat   # Windows CMD
pip install -r requirements.txt
python app.py
