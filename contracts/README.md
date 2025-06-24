# Contracts Management API

This module provides API endpoints for managing contracts, including creation, sending for signature, and tracking contract status.

## Features

- Create and manage contracts
- Send contracts for e-signature
- Track contract status (draft, sent, signed, expired, declined)
- Send reminders for pending signatures
- Download signed contracts
- Customer number tracking

## API Endpoints

### Contracts

- `POST /api/contracts/` - Create a new contract
- `GET /api/contracts/` - List all contracts
- `GET /api/contracts/{id}/` - Retrieve a specific contract
- `PUT /api/contracts/{id}/` - Update a contract
- `DELETE /api/contracts/{id}/` - Delete a contract
- `POST /api/contracts/{id}/send/` - Send contract for signature
- `GET /api/contracts/{id}/signed/` - Download signed contract
- `POST /api/contracts/{id}/remind/` - Send reminder to sign
- `POST /api/contracts/{id}/sign/` - Sign a contract (for demo purposes)

## Models

### Contract
- `title` - Title of the contract
- `content` - Contract content (HTML or plain text)
- `customer_name` - Name of the customer
- `customer_email` - Email of the customer
- `customer_phone` - Phone number of the customer (optional)
- `customer_number` - Unique identifier for the customer
- `status` - Current status of the contract
- `created_at` - When the contract was created
- `updated_at` - When the contract was last updated
- `sent_at` - When the contract was sent for signature
- `signed_at` - When the contract was signed
- `signed_document` - Reference to the signed document
- `created_by` - User who created the contract
- `expiration_date` - When the contract offer expires

### ContractReminder
- `contract` - Reference to the contract
- `sent_at` - When the reminder was sent
- `sent_by` - User who sent the reminder
- `notes` - Additional notes about the reminder

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Example Usage

### Create a new contract

```http
POST /api/contracts/
Content-Type: application/json
Authorization: Bearer <your_token>

{
  "title": "Rental Agreement",
  "content": "This is a sample rental agreement...",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "customer_number": "CUST12345"
}
```

### Send contract for signature

```http
POST /api/contracts/1/send/
Content-Type: application/json
Authorization: Bearer <your_token>

{
  "expiration_days": 7,
  "message": "Please sign this contract at your earliest convenience."
}
```

### Sign a contract

```http
POST /api/contracts/1/sign/
Content-Type: application/json
Authorization: Bearer <your_token>

{
  "signature_data": "base64_encoded_signature",
  "signer_name": "John Doe"
}
```

### Send a reminder

```http
POST /api/contracts/1/remind/
Content-Type: application/json
Authorization: Bearer <your_token>

{
  "message": "Friendly reminder to sign the contract"
}
```

## Setup

1. Make sure you have Python 3.8+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Start the development server: `python manage.py runserver`

## Testing

To run the tests:

```bash
python manage.py test contracts
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
