# SmartSave API Routes – Complete curl Documentation

Base URL: `http://localhost:80/api/v1/`

All endpoints except registration and login require a JWT token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## 1. Authentication (djoser + JWT)

### 1.1 Register a new user

```bash
curl -X POST http://localhost:80/api/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123"
  }'
```

**Response:** 201 Created with user details (no token yet).

---

### 1.2 Obtain JWT token pair

```bash
curl -X POST http://localhost:80/api/v1/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```
```
{
    "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4MDkwODEyNiwiaWF0IjoxNzc5MTgwMTI2LCJqdGkiOiI1YjI1MjY3YmM4NGU0OTM2ODFmZjZkMjk1M2FkNTE0OCIsInVzZXJfaWQiOiI0NzcyZTc2MS00MDNhLTQzNzMtODljMS0zMjNiNTJmZWU2ZmMifQ.n471_g79CtoZWqmg9W_odQh6uvlooWI4h8DHFr_N1ao",
    "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwMDQ0MTI2LCJpYXQiOjE3NzkxODAxMjYsImp0aSI6Ijc5MDQ0ZTJiNTI2ZjQwMjE4NjgzOTk2NjMzNjExY2Q1IiwidXNlcl9pZCI6IjQ3NzJlNzYxLTQwM2EtNDM3My04OWMxLTMyM2I1MmZlZTZmYyJ9.NNZl35aYEijrUEaYxAY6IJ83Ybq1WeH1AVrUyVgTMhE"}%  
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```

---

### 1.3 Refresh access token

```bash
curl -X POST http://localhost:80/api/v1/auth/jwt/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

**Response:** `{"access": "new_access_token"}`

---

### 1.4 Logout (blacklist refresh token – requires blacklist app)

```bash
curl -X POST http://localhost:80/api/v1/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

---

## 2. Finance Core Endpoints

All endpoints require authentication (`Authorization: Bearer <token>`).

### 2.1 List available financial institutions

```bash
curl -X GET http://localhost:80/api/v1/finance/institutions/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.2 Link an institution to your profile

```bash
curl -X POST http://localhost:80/api/v1/finance/my-institutions/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "550e8400-e29b-41d4-a716-446655440000",
    "account_number": "MF12345"
  }'
```

---

### 2.3 List your linked institutions

```bash
curl -X GET http://localhost:80/api/v1/finance/my-institutions/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.4 Create a deposit request

```bash
curl -X POST http://localhost:80/api/v1/finance/deposits/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 5000,
    "momo_transaction_id": "TX123456789",
    "notes": "From MTN MoMo"
  }'
```

---

### 2.5 List your deposits

```bash
curl -X GET http://localhost:80/api/v1/finance/deposits/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.6 (Bank staff) Confirm a deposit

```bash
curl -X PATCH http://localhost:80/api/v1/finance/deposits/<uuid>/confirm/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 2.7 Create a withdrawal request

```bash
curl -X POST http://localhost:80/api/v1/finance/withdrawals/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 2000,
    "notes": "Need cash for school fees"
  }'
```

---

### 2.8 List your withdrawals

```bash
curl -X GET http://localhost:80/api/v1/finance/withdrawals/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.9 (Bank staff) Schedule a withdrawal

```bash
curl -X PATCH http://localhost:80/api/v1/finance/withdrawals/<uuid>/schedule/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"scheduled_payout_date": "2026-05-25T14:30:00Z"}'
```

---

### 2.10 (Bank staff) Complete a withdrawal

```bash
curl -X PATCH http://localhost:80/api/v1/finance/withdrawals/<uuid>/complete/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 2.11 Add an expense

```bash
curl -X POST http://localhost:80/api/v1/finance/expenses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "food",
    "amount": 1500,
    "expense_date": "2026-05-19",
    "description": "Lunch at restaurant"
  }'
```

---

### 2.12 List expenses

```bash
curl -X GET http://localhost:80/api/v1/finance/expenses/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.13 Get spending summary (by category)

```bash
curl -X GET "http://localhost:80/api/v1/finance/expenses/summary/?period=week" \
  -H "Authorization: Bearer <access_token>"
```

**Query parameters:** `period` = `week`, `month`, `year`

---

## 3. User Profile Endpoints (existing from `users` app)

### 3.1 Get own profile

```bash
curl -X GET http://localhost:80/api/v1/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### 3.2 Update own profile

```bash
curl -X PATCH http://localhost:80/api/v1/users/update_me/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Johnny",
    "phone_number": "+237612345678"
  }'
```

---

## 4. Admin‑Only Endpoints (for bank dashboard)

These are used by the Django admin interface, but you can also call them via API with staff JWT.

### 4.1 List all deposits (bank staff sees all)

```bash
curl -X GET http://localhost:80/api/v1/finance/deposits/ \
  -H "Authorization: Bearer <staff_token>"
```

### 4.2 List all withdrawals

```bash
curl -X GET http://localhost:80/api/v1/finance/withdrawals/ \
  -H "Authorization: Bearer <staff_token>"
```

---

## Notes

- Replace `<uuid>` with the actual resource ID (UUID format).
- Replace `<access_token>` and `<admin_token>` with valid tokens.
- All amounts are in CFA francs (integer, no decimals).
- For production, use HTTPS.
```

---

## Final Step: Save the Routes File

I will now output the `API_ROUTES.md` file content as requested. You can save it in your project root.

```markdown
# SmartSave API Routes – Complete curl Documentation

Base URL: `http://localhost:80/api/v1/`

All endpoints except registration and login require a JWT token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## 1. Authentication (djoser + JWT)

### 1.1 Register a new user

```bash
curl -X POST http://localhost:80/api/v1/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123"
  }'
```

**Response:** 201 Created with user details (no token yet).

---

### 1.2 Obtain JWT token pair

```bash
curl -X POST http://localhost:80/api/v1/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```

---

### 1.3 Refresh access token

```bash
curl -X POST http://localhost:80/api/v1/auth/jwt/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

**Response:** `{"access": "new_access_token"}`

---

### 1.4 Logout (blacklist refresh token – requires blacklist app)

```bash
curl -X POST http://localhost:80/api/v1/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your_refresh_token"}'
```

---

## 2. Finance Core Endpoints

All endpoints require authentication (`Authorization: Bearer <token>`).

### 2.1 List available financial institutions

```bash
curl -X GET http://localhost:80/api/v1/finance/institutions/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.2 Link an institution to your profile

```bash
curl -X POST http://localhost:80/api/v1/finance/my-institutions/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "550e8400-e29b-41d4-a716-446655440000",
    "account_number": "MF12345"
  }'
```

---

### 2.3 List your linked institutions

```bash
curl -X GET http://localhost:80/api/v1/finance/my-institutions/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.4 Create a deposit request

```bash
curl -X POST http://localhost:80/api/v1/finance/deposits/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 5000,
    "momo_transaction_id": "TX123456789",
    "notes": "From MTN MoMo"
  }'
```

---

### 2.5 List your deposits

```bash
curl -X GET http://localhost:80/api/v1/finance/deposits/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.6 (Bank staff) Confirm a deposit

```bash
curl -X PATCH http://localhost:80/api/v1/finance/deposits/<uuid>/confirm/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 2.7 Create a withdrawal request

```bash
curl -X POST http://localhost:80/api/v1/finance/withdrawals/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "institution": "550e8400-e29b-41d4-a716-446655440000",
    "amount": 2000,
    "notes": "Need cash for school fees"
  }'
```

---

### 2.8 List your withdrawals

```bash
curl -X GET http://localhost:80/api/v1/finance/withdrawals/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.9 (Bank staff) Schedule a withdrawal

```bash
curl -X PATCH http://localhost:80/api/v1/finance/withdrawals/<uuid>/schedule/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"scheduled_payout_date": "2026-05-25T14:30:00Z"}'
```

---

### 2.10 (Bank staff) Complete a withdrawal

```bash
curl -X PATCH http://localhost:80/api/v1/finance/withdrawals/<uuid>/complete/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

### 2.11 Add an expense

```bash
curl -X POST http://localhost:80/api/v1/finance/expenses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "food",
    "amount": 1500,
    "expense_date": "2026-05-19",
    "description": "Lunch at restaurant"
  }'
```

---

### 2.12 List expenses

```bash
curl -X GET http://localhost:80/api/v1/finance/expenses/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 2.13 Get spending summary (by category)

```bash
curl -X GET "http://localhost:80/api/v1/finance/expenses/summary/?period=week" \
  -H "Authorization: Bearer <access_token>"
```

**Query parameters:** `period` = `week`, `month`, `year`

---

## 3. User Profile Endpoints (existing from `users` app)

### 3.1 Get own profile

```bash
curl -X GET http://localhost:80/api/v1/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### 3.2 Update own profile

```bash
curl -X PATCH http://localhost:80/api/v1/users/update_me/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Johnny",
    "phone_number": "+237612345678"
  }'
```

---

## 4. Admin‑Only Endpoints (for bank dashboard)

These are used by the Django admin interface, but you can also call them via API with staff JWT.

### 4.1 List all deposits (bank staff sees all)

```bash
curl -X GET http://localhost:80/api/v1/finance/deposits/ \
  -H "Authorization: Bearer <staff_token>"
```

### 4.2 List all withdrawals

```bash
curl -X GET http://localhost:80/api/v1/finance/withdrawals/ \
  -H "Authorization: Bearer <staff_token>"
```

---

## Notes

- Replace `<uuid>` with the actual resource ID (UUID format).
- Replace `<access_token>` and `<admin_token>` with valid tokens.
- All amounts are in CFA francs (integer, no decimals).
- For production, use HTTPS.
```

---

**Summary of what was delivered:**

- ✅ Signals for deposit confirmation and withdrawal completion (using existing `notifications` app).
- ✅ Updated `apps.py` to load signals.
- ✅ Complete `API_ROUTES.md` with all routes + `curl` examples.

Now you can test the API with the provided commands.