# 🌱 PlantCareSystem (Grovana)

> A full-featured Django REST Framework backend for an all-in-one plant care platform — combining an e-commerce store, an AI-powered plant disease diagnosis engine, and a plant-lovers community.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.15-red?logo=django&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.6-EE4C2C?logo=pytorch&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-black?logo=jsonwebtokens)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

**PlantCareSystem** is a graduation project built as a production-style REST API that helps plant owners buy plants and gardening supplies, diagnose plant diseases from a photo using a deep-learning model, get personalized care guides, and share experiences with a community of fellow plant lovers.

The backend is organized into clean, modular Django apps — each responsible for a single domain — and exposes a fully documented JSON API secured with JWT authentication.

---

## ✨ Features

### 🔐 Account & Authentication
- User registration and login with **JWT** (access + refresh tokens)
- Email OTP verification and password reset flow
- Profile management with avatar upload, bio, gender, date of birth
- Custom `User` model with unique email & phone number validation

### 🧠 AI Plant Disease Detection
- Upload a photo of a plant leaf and get an instant diagnosis
- Powered by a custom **CNN (PyTorch)** model trained on 39 plant disease classes
- Returns disease name, description, prevention steps, a care guide, and recommended supplements

### 🛒 Shop (E-commerce)
- Product catalog (Plants, Seeds, Pots) with search & filtering
- Product reviews and ratings
- Wishlist and shopping cart
- Checkout flow and order history/status tracking

### 👥 Community
- Create posts with images
- Comment on posts
- Full CRUD for posts and comments, scoped per user

### 🏠 Home
- Client testimonials/reviews
- Contact-us form endpoint

### ⚙️ Platform
- Interactive HTML **API documentation** page served at the root route
- Custom 404 / 500 error handlers
- CORS support for frontend integration
- Django Admin customized with **django-unfold**
- Dockerized for easy deployment (Gunicorn + WSGI)

---

## 🛠️ Tech Stack

| Layer            | Technology                                                        |
|-------------------|---------------------------------------------------------------------|
| Language          | Python 3.12                                                        |
| Framework         | Django 5.1 + Django REST Framework                                 |
| Authentication    | djangorestframework-simplejwt (JWT)                                |
| Database          | PostgreSQL                                                          |
| AI / ML           | PyTorch, Torchvision, NumPy, Pandas (CNN disease classifier)       |
| Filtering         | django-filter                                                      |
| Admin UI          | django-unfold                                                      |
| Media/Images      | Pillow                                                              |
| Deployment        | Docker, Gunicorn, WhiteNoise, Heroku-ready (`django-heroku`)       |
| CORS              | django-cors-headers                                                 |

---

## 📁 Project Structure

```
PlantCareSystem/
├── Backend/
│   └── project/
│       ├── project/          # Core settings, root URLs, WSGI/ASGI
│       ├── account/          # Auth, users, profiles, OTP
│       ├── ai/                # Plant disease detection (CNN model)
│       ├── shop/              # Products, cart, wishlist, orders
│       ├── community/         # Posts & comments
│       ├── home/              # Reviews & contact form
│       ├── frontend/           # API docs landing page
│       ├── utils/              # Shared helpers (error handlers, etc.)
│       ├── templates/          # index.html (API docs)
│       ├── static/             # Endpoint screenshots for docs
│       ├── media/              # User-uploaded content
│       ├── requirements.txt
│       └── Dockerfile
├── Database/                  # Database backup
├── test images/                # Sample images for AI model testing
└── requirements.txt
```

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api/`.

### Authentication (`account`)
| Method | Endpoint                  | Description                  |
|--------|----------------------------|-------------------------------|
| POST   | `/api/token/`               | Obtain JWT access/refresh pair |
| POST   | `/api/token/refresh/`       | Refresh JWT access token       |
| POST   | `/api/register/`            | Register a new user            |
| POST   | `/api/login/`                | Log in                         |
| GET    | `/api/profile/`              | Get current user profile       |
| PUT    | `/api/update/`               | Update profile                 |
| POST   | `/api/change_password/`      | Change password                |
| POST   | `/api/get_otp/`              | Request OTP                    |
| POST   | `/api/verify_otp/`           | Verify OTP                     |
| POST   | `/api/reset_password/`       | Reset password                 |

### AI Diagnosis (`ai`)
| Method | Endpoint          | Description                              |
|--------|--------------------|--------------------------------------------|
| POST   | `/api/predict/`    | Upload a leaf image and get a diagnosis     |

### Shop (`shop`)
| Method | Endpoint                                        | Description              |
|--------|---------------------------------------------------|----------------------------|
| GET    | `/api/products/`                                    | List products               |
| GET    | `/api/products/<slug>/`                             | Product detail               |
| POST   | `/api/products/<slug>/rate/`                        | Add a review/rating          |
| GET/POST | `/api/wishlist/`                                  | View/add to wishlist         |
| DELETE | `/api/wishlist/delete/<slug>/`                     | Remove from wishlist         |
| GET/POST | `/api/cart/`                                      | View/add to cart              |
| PATCH/DELETE | `/api/cart/reduce-delete/<slug>/`             | Update/remove cart item       |
| POST   | `/api/checkout/`                                    | Checkout                     |
| GET    | `/api/orders/`                                       | Order history                 |

### Community (`community`)
| Method | Endpoint                                     | Description        |
|--------|-------------------------------------------------|-----------------------|
| GET/POST | `/api/posts/`                                  | List/create posts       |
| GET/PUT/DELETE | `/api/posts/<id>/`                        | Manage a single post     |
| GET/POST | `/api/posts/<post_id>/comments/`              | List/create comments     |
| GET/PUT/DELETE | `/api/comments/<id>/`                    | Manage a single comment  |

### Home (`home`)
| Method | Endpoint          | Description               |
|--------|--------------------|------------------------------|
| GET/POST | `/api/reviews/`  | List/add client testimonials  |
| POST   | `/api/contact/`     | Submit a contact-us message   |

> 💡 A full interactive API documentation page (with request/response examples) is also served on the root route `/` of the deployed app.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL
- pip / virtualenv

### 1. Clone the repository
```bash
git clone https://github.com/EngMohamedNowar/PlantCareSystem.git
cd PlantCareSystem/Backend/project
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file (or export these as environment variables) and update `settings.py` to read from it instead of hardcoded values:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

> ⚠️ **Security note:** the current `settings.py` in this repo contains hardcoded database and email credentials. Before deploying or open-sourcing this project further, move all secrets to environment variables and rotate any exposed credentials.

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

### Running with Docker
```bash
cd Backend/project
docker build -t plant-care-system .
docker run -p 8000:8000 plant-care-system
```

---

## 🤖 AI Model

The disease-detection engine (`ai/CNN.py` + `ai/ai_model.py`) uses a custom Convolutional Neural Network trained to classify **39 plant disease categories**. Given an uploaded leaf image, the model returns:
- Disease name & description
- Prevention steps
- A tailored care guide
- Recommended supplement

Sample test images are provided in the `test images/` directory for quick verification.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is available under the **MIT License**. Feel free to use it for learning purposes.

---

## 👤 Author

**Mohamed Nowar**
- GitHub: [@EngMohamedNowar](https://github.com/EngMohamedNowar)

*Originally forked from [HabibaElbehairy1/PlantCareSystem](https://github.com/HabibaElbehairy1/PlantCareSystem).*
