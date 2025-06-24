# Regulations API

This module provides functionality for managing and distributing building/community regulations to stakeholders.

## Features

- Upload and publish regulation documents
- List and filter regulations by property and type
- Download regulation documents
- Send regulations to tenants, co-hosts, or visitors
- Track acknowledgment of regulations by recipients

## Models

### Regulation
- Represents a regulation document with metadata
- Fields: title, description, document, document_type, status, effective_date, expiration_date, property, created_by, etc.

### RegulationRecipient
- Tracks which users have received which regulations
- Fields: regulation, user, sent_at, viewed_at, acknowledged, acknowledged_at

## API Endpoints

### List/Create Regulations
- **URL**: `/api/regulations/`
- **Method**: `GET`, `POST`
- **Authentication**: Required
- **Permissions**: Admin users can create, all authenticated users can list
- **Query Parameters**:
  - `property_id`: Filter by property
  - `document_type`: Filter by document type
  - `status`: Filter by status (defaults to 'published' for non-staff)

### Retrieve/Update/Delete Regulation
- **URL**: `/api/regulations/{id}/`
- **Method**: `GET`, `PUT`, `PATCH`, `DELETE`
- **Authentication**: Required
- **Permissions**: Admin users can update/delete, all authenticated users can view

### Download Regulation Document
- **URL**: `/api/regulations/{id}/download/`
- **Method**: `GET`
- **Authentication**: Required
- **Permissions**: Same as retrieve

### Send Regulation to Users
- **URL**: `/api/regulations/{id}/send/`
- **Method**: `POST`
- **Authentication**: Required
- **Permissions**: Admin only
- **Request Body**:
  ```json
  {
    "user_ids": [1, 2, 3],
    "message": "Please review the updated community guidelines."
  }
  ```

### List Received Regulations (for recipients)
- **URL**: `/api/regulation-recipients/`
- **Method**: `GET`
- **Authentication**: Required
- **Permissions**: Users can only see their own received regulations

### Acknowledge/View Regulation (for recipients)
- **URL**: `/api/regulation-recipients/{id}/acknowledge/`
- **URL**: `/api/regulation-recipients/{id}/view/`
- **Method**: `POST`
- **Authentication**: Required
- **Permissions**: Only the recipient can acknowledge/view their own regulations

## Configuration

1. Add 'regulations' to INSTALLED_APPS in settings.py
2. Configure MEDIA_URL and MEDIA_ROOT for file storage
3. Run migrations: `python manage.py migrate`

## File Storage

Uploaded regulation documents are stored in the media directory under `regulations/{regulation_id}/`.
