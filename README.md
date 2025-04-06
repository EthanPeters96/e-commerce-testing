# E-Commerce Store

A modern e-commerce platform built with Django, featuring a responsive design and Stripe integration for secure payments.

## Features

-   🛍️ Product catalog with categories
-   🛒 Shopping cart functionality
-   💳 Secure payment processing with Stripe
-   👤 User authentication and profiles
-   📱 Responsive design for all devices
-   🔍 Product search functionality
-   🏷️ Order management system
-   🎨 Modern and clean UI

## Technologies Used

-   Django 5.0.2
-   Python 3.11+
-   Bootstrap 5
-   Stripe API
-   SQLite (Development)
-   WhiteNoise (Static Files)
-   Pillow (Image Processing)

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd e-commerce
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following:

```
SECRET_KEY=your_django_secret_key
DEBUG=True
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Run the development server:

```bash
python manage.py runserver
```

## Project Structure

```
e-commerce/
├── ecommerce/          # Project configuration
├── store/              # Main application
│   ├── static/        # Static files (CSS, JS)
│   ├── templates/     # HTML templates
│   ├── models.py      # Database models
│   └── views.py       # View logic
├── media/             # User-uploaded files
├── staticfiles/       # Collected static files
├── manage.py          # Django management script
└── requirements.txt   # Project dependencies
```

## Configuration

### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard
3. Add them to your `.env` file

### Static/Media Files

-   Static files are served using WhiteNoise
-   Media files are stored in the `media/` directory
-   Run `python manage.py collectstatic` to collect static files

## Features in Detail

### Product Management

-   Add/edit products through Django admin
-   Upload product images
-   Set prices and stock levels
-   Organize products by categories

### Shopping Cart

-   Add/remove products
-   Update quantities
-   Persistent cart across sessions

### Checkout Process

-   Secure payment processing
-   Order confirmation
-   Email notifications
-   Order history

### User Management

-   User registration and authentication
-   Profile management
-   Order history viewing

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project follows PEP 8 style guide. Run flake8 to check:

```bash
flake8
```

## Production Deployment

1. Set DEBUG=False in production
2. Configure a production-ready database
3. Set up proper email backend
4. Configure proper static/media file serving
5. Set up SSL certificate
6. Configure proper security settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email [your-email] or create an issue in the repository.
