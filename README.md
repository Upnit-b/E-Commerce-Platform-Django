# 🛍️ Django eCommerce

A production-ready e-commerce platform built with Django, supporting full product management, shopping cart, secure checkout using the **PayPal REST API**, user accounts, email verification, and a powerful admin dashboard. This project is suitable for learning, extending into real-world deployments, or using as a base for SaaS products.

---

## 📦 Features

- 🔐 **User Authentication**: Registration, login, logout, profile management
- ✅ **Email Verification**: Activation emails on registration, password reset emails, order confirmation emails
- 🛒 **Shopping Cart**: Add, update, and remove products from cart
- 📦 **Order Management**: Order placement and tracking system
- 💳 **Secure Payments**: Integrated with **PayPal Orders API**
- 🌟 **Reviews and Ratings**: Users can rate and review products
- 🖼️ **Multiple Product Images**: Products support multiple image uploads
- 📊 **Advanced Admin Dashboard**: Customized admin interface with full control
- 📂 **Modular App Structure**: Clean separation of concerns for scalability
- 💻 **Responsive Frontend**: Bootstrap-powered responsive UI

---

## 🧰 Tech Stack

| Layer        | Technology           |
| ------------ | -------------------- |
| Backend      | Django (Python)      |
| Frontend     | HTML, CSS, Bootstrap |
| Payments     | PayPal Orders API    |
| Email        | SMTP / Django Email  |
| Auth         | Django Auth          |
| Database     | SQLite (default)     |
| Static Files | Django Staticfiles   |

---

## 🚀 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Upnit-b/django_eCommerce.git
   cd django_eCommerce/src
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv env
   source env/bin/activate  # Windows: env\Scripts\activate
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

---

## 📧 Email Verification

This app sends emails for:

- 🔐 **Account Activation** after registration
- 🔁 **Password Reset** when forgotten
- ✅ **Order Confirmation** after a purchase

---

## 💳 PayPal Integration (REST API)

This app uses the **PayPal Orders API** to handle secure payment transactions:

- `POST /v2/checkout/orders` to create a new order
- `POST /v2/checkout/orders/{id}/capture` to finalize the payment

---

## 🗂️ Project Structure

```
src/
├── accounts/           # User profiles, email features, reviews/ratings
├── carts/              # Cart management
├── category/           # Product categories
├── orders/             # Order processing, PayPal integration
├── store/              # Product listings, product views
├── templates/          # HTML templates (Bootstrap)
├── static/             # Static files (CSS, JS, fonts)
├── static_collected/   # Collected static files (for deployment)
├── media/              # Uploaded images (products, users)
├── e_commerce/         # Main project settings
├── manage.py
└── requirements.txt
```

---

## 🛠 Admin Dashboard

The admin panel is fully customized:

- Filtered list views for orders, users, products
- Inline product image support
- Editable order status, user activity, product details

---

## 📬 Contact

Built by [@Upnit-b](https://github.com/Upnit-b) — feel free to reach out via GitHub Issues for any suggestions or bugs.

---
