# Coderr Backend

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/YOUR_USERNAME/YOUR_REPO)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)

## Overview

Coderr is a Django-based backend for a Fiverr-like platform, designed to connect customers with business users offering services. Built with **Django REST Framework (DRF)** and **SQLite** (for development), this backend powers a mentor-provided frontend, emphasizing robust API design and Test-Driven Development (TDD) best practices. The project showcases user authentication, profile management, service offers, order processing, reviews, and platform statistics, all implemented with a focus on scalability, security, and maintainability.

## Tech Stack

- **Python 3.13**: Core programming language for backend logic.
- **Django 5.2**: Web framework for rapid development and ORM.
- **Django REST Framework (DRF)**: Toolkit for building RESTful APIs with authentication, serialization, and filtering.
- **SQLite**: Lightweight database for development (configurable for PostgreSQL in production).
- **Django Authentication System**: Handles user registration, login, and token-based authentication.
- **django-cors-headers**: Enables CORS for frontend-backend communication (e.g., localhost:5500).
- **REST Framework Authtoken**: Provides token-based authentication for secure API access.
- **django-filters**: Supports dynamic query filtering for review listings.

## Features

- **User Authentication**: Register and log in as either a customer or business user, with token-based authentication (`/api/registration/`, `/api/login/`).
- **Profile Management**: CRUD operations for user profiles, including detailed fields like first name, last name, location, phone, description, working hours, and profile pictures (`/api/profile/{pk}/`).
- **Service Offers**: Business users can create and manage service offers, with customers able to browse and filter them.
- **Order Processing**: Facilitates order creation and management between customers and business users.
- **Reviews System**: Customers can post, update, and delete reviews for business users, with validation to prevent duplicates and ensure ratings are 1-5 (`/api/reviews/`, `/api/reviews/{id}/`).
- **Platform Statistics**: Aggregates data like review count, average rating, business profile count, and offer count (`/api/base-info/`).
- **Test-Driven Development**: Comprehensive test suite using Django’s `APITestCase`, covering happy and unhappy paths for all endpoints to ensure reliability.
- **CORS Support**: Configured for seamless integration with a frontend running on a different origin.
- **File Uploads**: Handles profile picture uploads via `multipart/form-data` with validation for image types.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/DomuStyle/Coderr_BE.git
   cd Coderr_BE
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   - Copy `core/settings.py` to set `DATABASES` (SQLite by default; update for PostgreSQL if needed).
   - Ensure `MEDIA_ROOT` and `MEDIA_URL` are set for profile picture uploads (e.g., `media/profile_pics/`).

5. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Run Tests**:
   ```bash
   python manage.py test
   ```

7. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   - API is accessible at `http://127.0.0.1:8000/api/`.
   - Use Postman or the mentor-provided frontend (configured for `http://127.0.0.1:5500`) to interact.

## API Endpoints

- **Authentication**:
  - `POST /api/registration/`: Register a new user (customer or business).
  - `POST /api/login/`: Obtain an authentication token.
- **Profiles**:
  - `GET/PATCH /api/profile/{pk}/`: Retrieve or update user profile details.
  - `GET /api/profiles/business/`: List business profiles.
  - `GET /api/profiles/customer/`: List customer profiles.
- **Reviews**:
  - `GET/POST /api/reviews/`: List or create reviews (customer-only for creation).
  - `PATCH/DELETE /api/reviews/{id}/`: Update or delete a review (owner-only).
- **Statistics**:
  - `GET /api/base-info/`: Retrieve platform statistics (e.g., review count, average rating).

## Testing

The project follows TDD principles with a robust test suite in `reviews_app/tests/` and `profiles_app/tests/`. Tests cover:
- Happy paths: Successful API calls for all endpoints.
- Unhappy paths: Error cases like invalid data, unauthorized access, and duplicate entries.
- Run tests with:
  ```bash
  python manage.py test
  ```

## Contributing

This is a portfolio project for learning TDD with Django DRF. Contributions are welcome for bug fixes or test improvements. Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/xyz`).
3. Write tests for new functionality.
4. Submit a pull request.

## License

This project is licensed under the MIT License.