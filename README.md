# Inorental: New Rental Backend

## 1. Introduction
This project is the backend for an InoRental Project, built using Django and Django REST Framework. The platform aims to facilitate property listings, search, booking, and communication between guests and hosts. This README provides an overview of the project's core features, technology stack, data models, and setup instructions.

## 2. Core Features (MVP)
The Minimum Viable Product (MVP) focuses on the following essential functionalities:
*   **User Authentication**: User registration, login, and logout.
*   **Property Listings**: Hosts can create, update, and delete property listings with detailed information, including photos and availability.
*   **Search and Discovery**: Users can search for properties based on location, dates, number of guests, property type, and amenities.
*   **Property Details Page**: Dedicated page for each property with all details, photos, host information, availability, and reviews.
*   **Booking System**: Users can select dates and book properties with availability checks and booking confirmation. (Simplified payment processing for MVP).
*   **Reviews and Ratings**: Guests can leave reviews and ratings for completed stays.
*   **User Profiles**: Basic user profile pages showing personal information, booking history, and listed properties.
*   **Host Dashboard (Simplified)**: Hosts can manage listings and view upcoming bookings.
*   **Guest-Host Messaging**: Dedicated messaging interface for communication between users.

## 3. Technology Stack
*   **Backend**: Python with Django and Django REST Framework (DRF)
*   **Real-time Features**: Django Channels (for future messaging enhancements)
*   **Database**: MySQL (for production), SQLite (for development/testing)
*   **API Documentation**: `drf-yasg` (Swagger/OpenAPI)
*   **Image Handling**: Pillow (for `ImageField` in Django models)

## 4. Data Models
The application uses the following primary data models:
*   **User**: Extends Django's `AbstractUser` for authentication and profile information.
*   **Property**: Details about listed accommodations (title, description, address, price, capacity, etc.).
*   **Photo**: Stores images associated with properties.
*   **Availability**: Manages available and blocked dates for properties.
*   **Amenity**, **Facility**, **HouseRule**: Lookup tables for property features and rules.
*   **PropertyAmenity**, **PropertyFacility**, **PropertyHouseRule**: Join tables linking properties to their amenities, facilities, and house rules.
*   **Booking**: Records guest bookings for properties.
*   **Review**: Stores guest reviews and ratings for properties.
*   **Conversation**, **ConversationParticipant**, **Message**: Models for the guest-host messaging system.

## 5. Setup and Installation

### Prerequisites
*   Python 3.8+
*   pip (Python package installer)

### Steps
1.  **Clone the repository (if applicable):**
    ```bash
    git clone [repository_url]
    cd inorental/backend
    ```
    (Assuming you are already in the `inorental/backend` directory)

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate # On Windows: `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you plan to run with MySQL locally (without Docker), you might need to install `mysqlclient` system dependencies first (e.g., `sudo apt-get install default-libmysqlclient-dev` on Debian/Ubuntu).*

4.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations account core
    python manage.py migrate
    ```
    *Note: If you encounter `InconsistentMigrationHistory` errors, it might be due to previous partial migrations. You can resolve this by deleting the `db.sqlite3` file and then re-running `python manage.py migrate`. This will reset your database.*

5.  **Create a superuser (for admin panel access):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.

## 6. Running the Application

### Running with Docker Compose (Recommended for Production/Development)
To build and run the backend and MySQL database using Docker Compose:
```bash
docker-compose up --build
```
The API will be accessible at `http://127.0.0.1:8000/api/`. The backend service is configured to use MySQL when run via Docker Compose.

### Running Locally (Development with SQLite)
To start the Django development server using SQLite:
```bash
python manage.py runserver 8000
```
The API will be accessible at `http://127.0.0.1:8000/api/`.

## 7. Populating Initial Data
After setting up the database (either with Docker Compose or locally), you can populate initial data for amenities, facilities, and house rules:
```bash
python manage.py populate_data
```

## 8. API Endpoints and Documentation

## 9. API Endpoints and Documentation

The API documentation is available via Swagger UI and ReDoc:
*   **Swagger UI**: `http://127.0.0.1:8000/swagger/`
*   **ReDoc**: `http://127.0.0.1:8000/redoc/`

You can interact with the API endpoints directly from the Swagger UI.

## 10. Admin Panel Access

The Django administration panel is available at:
*   `http://127.0.0.1:8000/admin/`

Log in with the superuser credentials you created to manage models.

## 11. Future Enhancements (Potential)
*   Social login integration (Google, Facebook).
*   Real payment gateway integration.
*   Advanced search filters and sorting.
*   Map integration with interactive property markers.
*   Real-time messaging using WebSockets (Django Channels).
*   Image optimization and CDN integration.
*   User notifications.
*   Wishlist functionality.
*   Comprehensive host dashboard with analytics.
