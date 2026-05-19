# SmartSave, Complete System Documentation

> This document contains every diagram required to understand the SmartSave personal finance management system:  
> **Component architecture, deployment, ER diagram, class diagram, sequence diagrams, and state machines.**  
> All diagrams use Mermaid syntax and are frozen for the project duration.

---

## 1. System Component Architecture (Logical Modules & Communication)

```mermaid
flowchart TB
    subgraph Client["Client Side"]
        MobileApp["React Native Mobile App<br/>(Expo)"]
    end

    subgraph Gateway["Gateway Layer"]
        Nginx["Nginx Reverse Proxy"]
    end

    subgraph Backend["Backend Layer (Django)"]
        API["REST API Module<br/>(DRF viewsets)"]
        Admin["Django Admin Module<br/>(Bank Dashboard)"]
        Auth["Authentication Module<br/>(djoser + JWT)"]
        Core["Finance Core Module<br/>(business logic)"]
        Notif["Notifications Module<br/>(email/SMS templates)"]
    end

    subgraph Async["Async Processing"]
        Redis["Redis Broker"]
        Celery["Celery Worker"]
    end

    subgraph Storage["Storage Layer"]
        DB[("PostgreSQL")]
        Media[("Media Storage<br/>(local or R2)")]
    end

    subgraph External["External Services"]
        SMTP["SMTP Server"]
        SMS["SMS Gateway<br/>(Twilio)"]
    end

    MobileApp -->|HTTPS / JSON| Nginx
    Nginx -->|/api/*| API
    Nginx -->|/admin/*| Admin
    MobileApp -->|JWT token| Auth
    Auth -->|Validate| API
    API -->|Business calls| Core
    Core -->|Read/Write| DB
    Core -->|Upload/Download| Media
    Core -->|Trigger| Notif
    Notif -->|Queue task| Redis
    Redis -->|Deliver| Celery
    Celery -->|Send email| SMTP
    Celery -->|Send SMS| SMS
    Admin -->|Manage institutions, confirm| Core
    Admin -->|Read/Write| DB
```

**Communication summary:**

- **Mobile ↔ Nginx:** HTTPS only.
- **Nginx ↔ Django API/Admin:** HTTP over internal Docker network.
- **Django ↔ PostgreSQL:** TCP port 5432, credentials from env.
- **Django ↔ Redis:** TCP port 6379 (message broker).
- **Celery ↔ Redis:** Same as above.
- **Celery ↔ SMTP/SMS:** Outbound connections (SMTP over TLS, Twilio API over HTTPS).

---

## 2. Deployment Diagram (Docker Containers & External)

```mermaid
flowchart TB
    subgraph Host["Server / Local Machine"]
        subgraph Docker["Docker Compose Environment"]
            Container_Nginx["Container: nginx<br/>ports: 80,443"]
            Container_Django["Container: django<br/>command: gunicorn / start"]
            Container_Celery["Container: celery_worker<br/>command: celery worker"]
            Container_Redis["Container: redis<br/>port: 6379"]
            Container_Postgres["Container: postgres<br/>port: 5432"]
            Volume_Postgres["Volume: postgres_data"]
            Volume_Media["Volume: media_volume"]
            Volume_Static["Volume: static_volume"]
        end
    end

    subgraph External["External World"]
        MobileDevice["Mobile Device"]
        EmailServer["Email Server (SMTP)"]
        TwilioAPI["Twilio API"]
    end

    MobileDevice -->|HTTP/HTTPS| Container_Nginx
    Container_Nginx -->|uWSGI/HTTP| Container_Django
    Container_Django -->|TCP 5432| Container_Postgres
    Container_Postgres --> Volume_Postgres
    Container_Django --> Volume_Media
    Container_Django --> Volume_Static
    Container_Django -->|Task| Container_Redis
    Container_Redis -->|Task| Container_Celery
    Container_Celery -->|SMTP| EmailServer
    Container_Celery -->|HTTPS| TwilioAPI
    Container_Nginx -->|Serve static/media| Volume_Static
    Container_Nginx -->|Serve media| Volume_Media
```

**Container notes:**

- All containers share the Docker network `finance_manager-network`.
- `nginx` acts as reverse proxy; it also serves static files directly.
- `django` container runs Gunicorn (production) or `runserver` (dev override).
- `celery_worker` uses same image as django, with different command.
- `redis` no persistent volume – cache/message broker only.
- `postgres` uses named volume for data persistence.

---

## 3. Entity‑Relationship (ER) Diagram, Database

```mermaid
erDiagram
    %% Existing tables from starter (abbreviated)
    users_user {
        bigint pkid PK
        uuid id UK
        varchar email UK
        varchar username
        varchar first_name
        varchar last_name
        varchar role
        boolean is_active
        boolean is_staff
        timestamp date_joined
    }

    users_profile {
        bigint pkid PK
        uuid id UK
        bigint user_id FK
        text bio
        varchar profile_photo
        varchar gender
        varchar country
        varchar phone_number
    }

    notifications_notification {
        uuid id PK
        uuid user_id FK
        varchar recipient
        varchar channel
        varchar status
        text body
        timestamp created_at
    }

    %% New finance tables
    finance_financialinstitution {
        bigint pkid PK
        uuid id UK
        varchar name
        varchar momo_number
        varchar contact_phone
        varchar contact_email
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    finance_userinstitutionaccount {
        bigint pkid PK
        uuid id UK
        bigint user_id FK
        bigint institution_id FK
        varchar account_number
        timestamp created_at
    }

    finance_deposittransaction {
        bigint pkid PK
        uuid id UK
        bigint user_id FK
        bigint institution_id FK
        decimal amount
        varchar momo_transaction_id
        varchar status
        text notes
        timestamp requested_at
        timestamp confirmed_at
        bigint confirmed_by_id FK
    }

    finance_withdrawalrequest {
        bigint pkid PK
        uuid id UK
        bigint user_id FK
        bigint institution_id FK
        decimal amount
        varchar status
        timestamp scheduled_payout_date
        timestamp completed_at
        text notes
        bigint processed_by_id FK
        timestamp created_at
    }

    finance_expense {
        bigint pkid PK
        uuid id UK
        bigint user_id FK
        varchar category
        decimal amount
        date expense_date
        text description
        timestamp created_at
    }

    %% Relationships
    users_profile ||--|| users_user : "one-to-one"
    users_user ||--o{ notifications_notification : "has"
    users_user ||--o{ finance_userinstitutionaccount : "has"
    users_user ||--o{ finance_deposittransaction : "makes"
    users_user ||--o{ finance_withdrawalrequest : "requests"
    users_user ||--o{ finance_expense : "logs"

    finance_financialinstitution ||--o{ finance_userinstitutionaccount : "belongs to"
    finance_financialinstitution ||--o{ finance_deposittransaction : "receives"
    finance_financialinstitution ||--o{ finance_withdrawalrequest : "processes"

    %% Admin foreign keys (self-reference to users_user)
    finance_deposittransaction }o--|| users_user : "confirmed_by (admin)"
    finance_withdrawalrequest }o--|| users_user : "processed_by (admin)"
```

**Index notes (for performance):**
- `finance_deposittransaction (status, institution_id)`
- `finance_withdrawalrequest (status, institution_id)`
- `finance_expense (user_id, expense_date)`

---

## 4. Class Diagram (Main Django Models)

```mermaid
classDiagram
    class TimeStampedUUIDModel {
        <<abstract>>
        +BigAutoField pkid
        +UUIDField id
        +DateTimeField created_at
        +DateTimeField updated_at
    }

    class User {
        +BigAutoField pkid
        +UUIDField id
        +EmailField email
        +CharField username
        +CharField first_name
        +CharField last_name
        +CharField role
        +BooleanField is_active
        +BooleanField is_staff
        +get_full_name()
    }

    class Profile {
        +OneToOneField user
        +TextField bio
        +ImageField profile_photo
        +CharField gender
        +CountryField country
        +CharField phone_number
    }

    class FinancialInstitution {
        +CharField name
        +CharField momo_number
        +CharField contact_phone
        +EmailField contact_email
        +BooleanField is_active
    }

    class UserInstitutionAccount {
        +ForeignKey user
        +ForeignKey institution
        +CharField account_number
    }

    class DepositTransaction {
        +ForeignKey user
        +ForeignKey institution
        +DecimalField amount
        +CharField momo_transaction_id
        +CharField status  # pending, confirmed, failed
        +TextField notes
        +DateTimeField requested_at
        +DateTimeField confirmed_at
        +ForeignKey confirmed_by (User)
    }

    class WithdrawalRequest {
        +ForeignKey user
        +ForeignKey institution
        +DecimalField amount
        +CharField status  # pending, scheduled, completed, cancelled
        +DateTimeField scheduled_payout_date
        +DateTimeField completed_at
        +TextField notes
        +ForeignKey processed_by (User)
    }

    class Expense {
        +ForeignKey user
        +CharField category
        +DecimalField amount
        +DateField expense_date
        +TextField description
    }

    TimeStampedUUIDModel <|-- FinancialInstitution
    TimeStampedUUIDModel <|-- UserInstitutionAccount
    TimeStampedUUIDModel <|-- DepositTransaction
    TimeStampedUUIDModel <|-- WithdrawalRequest
    TimeStampedUUIDModel <|-- Expense
    User "1" --> "0..*" DepositTransaction
    User "1" --> "0..*" WithdrawalRequest
    User "1" --> "0..*" Expense
    User "1" --> "0..*" UserInstitutionAccount
    FinancialInstitution "1" --> "0..*" UserInstitutionAccount
    FinancialInstitution "1" --> "0..*" DepositTransaction
    FinancialInstitution "1" --> "0..*" WithdrawalRequest
```

---

## 5. Sequence Diagrams (Key Flows)

### 5.1 Deposit Request & Confirmation

```mermaid
sequenceDiagram
    participant Mobile as Mobile App
    participant Nginx
    participant API as DRF API
    participant Core as Finance Core
    participant DB as PostgreSQL
    participant Admin as Django Admin
    participant Notif as Notifications
    participant Celery
    participant SMS as SMS Gateway

    Mobile->>Nginx: POST /deposits/ (amount, institution_id, momo_txn_id)
    Nginx->>API: forward with JWT
    API->>Core: create_deposit(user, data)
    Core->>DB: INSERT deposit (status='pending')
    DB-->>Core: deposit object
    Core-->>API: serialized deposit
    API-->>Mobile: 201 Created

    Admin->>DB: SELECT pending deposits (filter by institution)
    Admin->>Core: confirm_deposit(deposit_id, admin_user)
    Core->>DB: UPDATE status='confirmed', confirmed_at=NOW()
    Core->>Notif: send_deposit_confirmed(user, amount, institution)
    Notif->>Celery: queue_sms_task(user.phone, message)
    Celery->>SMS: send SMS
    SMS-->>User: "Your deposit of X FCFA confirmed"
```

### 5.2 Withdrawal Request & Completion

```mermaid
sequenceDiagram
    participant Mobile
    participant Nginx
    participant API
    participant Core
    participant DB
    participant Admin
    participant Notif
    participant Celery
    participant SMS

    Mobile->>Nginx: POST /withdrawals/ (amount, institution_id)
    Nginx->>API: forward
    API->>Core: create_withdrawal(user, data)
    Core->>DB: INSERT withdrawal (status='pending')
    DB-->>Core: withdrawal object
    Core-->>Mobile: 201 Created

    Admin->>DB: SELECT pending withdrawals
    Admin->>Core: schedule_withdrawal(request_id, payout_date)
    Core->>DB: UPDATE status='scheduled', scheduled_payout_date=date

    Admin->>Core: complete_withdrawal(request_id) [after manual MoMo transfer]
    Core->>DB: UPDATE status='completed', completed_at=NOW()
    Core->>Notif: send_withdrawal_completed(user, amount)
    Notif->>Celery: queue_sms_task
    Celery->>SMS: send "Your withdrawal of X FCFA has been sent to your MoMo"
```

### 5.3 Expense Logging

```mermaid
sequenceDiagram
    participant Mobile
    participant Nginx
    participant API
    participant Core
    participant DB

    Mobile->>Nginx: POST /expenses/ (category, amount, date, desc)
    Nginx->>API: forward
    API->>Core: create_expense(user, data)
    Core->>DB: INSERT expense
    DB-->>Core: expense object
    Core-->>API: serialized expense
    API-->>Mobile: 201 Created
```

---

## 6. State Machine Diagrams

### 6.1 DepositTransaction States

```mermaid
stateDiagram-v2
    [*] --> Pending : User submits deposit
    Pending --> Confirmed : Admin confirms (matches MoMo)
    Pending --> Failed : Admin rejects / timeout
    Confirmed --> [*]
    Failed --> [*]
```

**Transitions:**
- `Pending → Confirmed` – bank admin sees transaction ID and confirms.
- `Pending → Failed` – bank admin marks as fraudulent or no matching MoMo.
- No other transitions.

### 6.2 WithdrawalRequest States

```mermaid
stateDiagram-v2
    [*] --> Pending : User requests withdrawal
    Pending --> Scheduled : Admin sets payout date
    Pending --> Cancelled : Admin rejects / user cancels
    Scheduled --> Completed : Admin marks after manual MoMo send
    Scheduled --> Cancelled : Admin cancels before payout
    Completed --> [*]
    Cancelled --> [*]
```

**Transitions:**
- `Pending → Scheduled` – bank admin assigns a date.
- `Pending → Cancelled` – bank rejects (insufficient funds, etc.).
- `Scheduled → Completed` – after admin actually sends MoMo.
- `Scheduled → Cancelled` – if admin changes mind (rare).

---

## 7. Component Interface Table (APIs & Events)

| Module | Input interface | Output interface | Data format |
|--------|----------------|------------------|--------------|
| Mobile App | User touch | HTTP request | JSON (REST) |
| Nginx | HTTP request | HTTP to upstream | Plain HTTP |
| Django API | HTTP + JWT | JSON response | JSON |
| Finance Core | Python dict | Model instance | Python objects |
| Notifications | `(user, template_name, context)` | Celery task ID | JSON |
| Celery | Task payload | SMTP / Twilio API call | Python + HTTPS |
| DB | SQL query | Result set | SQL / Python rows |
| Admin (Django) | HTTP (staff user) | HTML + forms | HTTP/HTML |

---

## 8. Document Version & Freeze Notice

**Version:** 3.0 (Final for development)  
**Date:** 2026-05-19  

> This document contains **all required diagrams** for system understanding.  
> No further changes to architecture, database schema, or module interactions will be made without updating this document first.

---
