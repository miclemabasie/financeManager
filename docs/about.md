# About the Project – SmartSave: Mobile‑First Personal Finance Manager for Cameroon

## 1. Project Overview

**Project Title:** SmartSave – A Mobile Application for Personal Finance Management with Microfinance & Mobile Money Integration

**Type:** Academic Research & Development Project (School Project)

**Target Region:** Cameroon (Bamenda and beyond) – where physical banking queues, limited digital infrastructure, and mobile money (MoMo) dominance shape financial behavior.

**Main Goal:**  
Develop a secure, easy‑to‑use mobile application that helps individuals manage their personal finances, save money via Mobile Money, and interact with multiple banks / microfinance institutions – **without requiring complex bank APIs or physical bank visits**.

---

## 2. The Problem We Are Solving

### 2.1 Real‑World Problem

Many people in Cameroon and other developing economies face three major barriers to good financial management:

1. **Physical banking friction** – Long queues, distance to bank branches, and limited operating hours discourage regular saving and account monitoring.
2. **Lack of integration** – Existing personal finance apps are designed for Western banking systems (direct API connections, credit scores, automated sync) which do not exist or are not accessible in Cameroon.
3. **Financial illiteracy** – Many users do not know how to budget, track expenses, or set savings goals. Even when they want to save, the process is inconvenient.

### 2.2 Specific Issues Addressed

| Issue | How It Manifests |
|-------|------------------|
| Saving is difficult | To put money into a microfinance account, a user must go to the branch or use Mobile Money – but there is no unified dashboard to track those savings. |
| Withdrawals take days | Users request cash, but there is no transparent tracking of withdrawal requests. |
| Multiple banks / MFs | A person may have accounts at two different microfinance institutions, but no single app shows all balances. |
| No expense tracking | Users spend cash or MoMo without knowing where money goes. |

Our solution removes the need to visit a bank hall for routine transactions, while keeping the process **secure, transparent, and compatible with existing Mobile Money infrastructure**.

---

## 3. The Proposed Solution – SmartSave

### 3.1 Core Idea

SmartSave is a **mobile‑first application** (React Native / Expo) backed by a **Django REST API**. It acts as an **intermediary layer** between the user and their chosen financial institutions (banks / microfinance houses).  

Instead of trying to connect directly to each bank’s core system (impossible in Cameroon), we use a **manual confirmation workflow** that mirrors how microfinance institutions already work with Mobile Money.

### 3.2 Key Features

| Feature | Description |
|---------|-------------|
| **User registration & profiles** | Email/password, JWT authentication, role‑based access (user / bank admin). |
| **Multi‑institution support** | Users can add multiple banks or microfinance institutions to their profile. |
| **Deposit via Mobile Money** | App shows the institution’s MoMo number → user sends money from their own MoMo app → enters transaction ID → institution confirms receipt manually. |
| **Withdrawal request** | User requests cash withdrawal → institution schedules a payout date → sends MoMo to user’s phone → marks as completed. |
| **Expense tracking** | Users can log daily expenses (category, amount, date) to understand spending patterns. |
| **Bank dashboard** (web) | Each institution has a simple dashboard (Django admin) to see deposits, confirm them, and manage withdrawal requests. |
| **Notifications** | Email/SMS alerts when a deposit is confirmed or a withdrawal is processed. |

### 3.3 Why This Works in Cameroon

- **No bank API required** – We never attempt to read a user’s real bank balance or initiate transfers automatically.  
- **Leverages existing Mobile Money** – Users already know how to send MoMo. We just give them the destination number and a way to prove payment.  
- **Manual confirmation = trust** – Banks/microfinance institutions retain full control over their money; we only record what they confirm.  
- **Low technical barrier** – The system can be operated by a single clerk at the MF.  
- **Transparency for users** – Users see a complete history of deposits, withdrawals, and expenses in one place.

---

## 4. How It Works – Step by Step

### 4.1 Deposit Flow (Saving Money)

1. **User selects an institution** (e.g., “Bamenda MF”) inside SmartSave.  
2. **App displays** the institution’s registered Mobile Money number and instructs the user to send the desired amount using their own MoMo app.  
3. **User sends money** via MoMo and copies the transaction ID / reference.  
4. **User enters** that reference into SmartSave and submits a deposit request.  
5. **Backend creates** a `DepositTransaction` with status `pending`.  
6. **Institution admin** logs into the dashboard, sees the pending deposit, matches it with their MoMo statement, and clicks **Confirm**.  
7. **User receives** an SMS/email notification: “Your deposit of X FCFA to Bamenda MF has been confirmed.”  
8. **Deposit appears** in the user’s transaction history.

### 4.2 Withdrawal Flow (Getting Money Back)

1. **User requests** a withdrawal (amount, institution).  
2. **Institution admin** sees the request, checks available funds, and sets a **payout date** (e.g., “tomorrow by 2 PM”).  
3. **Admin sends** the money to the user’s phone number via MoMo.  
4. **Admin marks** the request as `completed` in the dashboard.  
5. **User receives** notification and the money on their MoMo account.

> 🛡️ **Security note:** User identity for withdrawal can be verified via fingerprint/biometric on the device + the fact that the user is logged in with JWT. The institution can also call the user before sending large amounts.

### 4.3 Expense Tracking (Simple)

- User adds manual expenses (coffee, transport, etc.) with a category and date.  
- The mobile app shows spending summaries (daily/weekly/monthly) to encourage better budgeting.

---

## 5. Technical Architecture

### 5.1 Overview

[React Native Mobile App] 
       │
       │ HTTPS / JWT
       ▼
[Django REST API (backend)]
       │
       ├── PostgreSQL (database)
       ├── Redis + Celery (async tasks, notifications)
       ├── Django Admin (bank dashboard)
       └── Email / SMS gateways


### 5.2 Why Django + DRF?

- DRF allows rapid creation of REST endpoints for the mobile app.  
- Django admin provides an instant, secure dashboard for bank staff – no need to build a separate web frontend.

### 5.3 Mobile App (React Native / Expo)

- Cross‑platform (iOS + Android) from one codebase.  
- Will consume the Django REST API.  
- Features: registration/login, list institutions, deposit form, withdrawal form, expense logging, transaction history.

### 5.4 Data Models (Simplified)

| Model | Purpose |
|-------|---------|
| `FinancialInstitution` | Name, MoMo deposit number, contact info, active flag. |
| `UserInstitutionAccount` | Links a user to an institution (e.g., “John’s account at Bamenda MF”, with account number if any). |
| `DepositTransaction` | Amount, reference (MoMo transaction ID), status (pending/confirmed), user, institution, timestamp. |
| `WithdrawalRequest` | Amount, status (pending/scheduled/completed), scheduled payout date, user, institution. |
| `Expense` | Category, amount, date, note, user. |

All models inherit from `TimeStampedUUIDModel` (created_at, updated_at, UUID primary key).

---

## 6. Tools & Technologies

| Layer | Technologies |
|-------|--------------|
| **Backend Framework** | Django 5.2, Django REST Framework (DRF) |
| **Database** | PostgreSQL (development: SQLite optional) |
| **Authentication** | JWT (Simple JWT), djoser for registration/password management |
| **Async Tasks** | Celery + Redis (for sending SMS/email notifications) |
| **Notifications** | Email (SMTP), SMS (Twilio or console for dev) |
| **API Documentation** | DRF Spectacular (OpenAPI) |
| **Containerization** | Docker, Docker Compose (PostgreSQL, Redis, Nginx, Django app, Celery worker) |
| **Mobile App** | React Native + Expo |
| **Web Dashboard** | Django admin (customized) – no separate frontend |
| **Version Control** | Git |
| **Deployment (optional)** | Any cloud VPS (DigitalOcean, AWS) or local server |

---

## 7. Why We Chose This Approach (Rationale)

### 7.1 No Real‑Time Bank APIs

- **Cameroon does not offer open banking APIs** for microfinance institutions.  
- Connecting directly to bank core systems is legally and technically impossible for a school project.  
- **Our manual confirmation workflow** is realistic, secure, and already used by local savings apps like *Nkwa*.

### 7.2 Manual Deposit Confirmation – Not a Weakness

- It mimics the real world: even when you deposit at a bank counter, a human verifies the cash.  
- It avoids fraud: automatic detection of MoMo payments would require integration with MTN/Orange, which is not feasible.  
- For a school project, manual confirmation demonstrates understanding of the domain constraint – and it works.

### 7.3 Using Django Admin as Bank Dashboard

- Building a separate React dashboard would double the work.  
- Django admin is secure, customizable, and can be locked down to show only one institution’s data.  
- We can add filters, actions (confirm deposit), and readonly fields – perfect for an MVP.

### 7.4 Simple Expense Management

- The project’s primary innovation is the deposit/withdrawal layer.  
- Expense tracking is a secondary feature to make the app useful for daily budgeting.  
- Keeping it simple (no linking to bank accounts) avoids complexity.

---

## 8. Project Scope – What Is Included & What Is Not

### ✅ Included (MVP for school project)

- User registration, login, JWT authentication.  
- List financial institutions (banks / MFs).  
- Deposit request + manual confirmation by admin.  
- Withdrawal request + manual payout by admin.  
- Basic expense tracking (CRUD + summaries).  
- Notification (email/SMS) on deposit confirmation & withdrawal completion.  
- Web dashboard (Django admin) for banks to manage requests.  
- Mobile app (React Native/Expo) that calls all API endpoints.

### ❌ Excluded (out of scope for this project)

- Real‑time balance fetching from bank APIs.  
- Automatic payment detection via Mobile Money webhooks.  
- Complex investment tracking or stock market data.  
- Credit score calculation.  
- Multi‑currency (only CFA Francs).  
- Advanced fraud detection (beyond biometric app lock and JWT).

---

## 9. Expected Outcomes

1. A **functional mobile application** that allows users to deposit and withdraw money from multiple microfinance institutions using Mobile Money.  
2. A **Django backend** with clear REST APIs and an admin dashboard for bank staff.  
3. **Documentation** (this file + code comments) sufficient for academic evaluation.  
4. A **practical solution** that could be adopted by a real microfinance institution in Bamenda with minimal changes.  
5. **Evidence** that mobile applications can reduce physical banking friction and improve financial literacy when designed with local constraints in mind.

---

## 10. Conclusion

SmartSave is not a naive attempt to clone Western fintech apps. It is a **context‑aware, practical solution** that respects the reality of Cameroon’s financial infrastructure. By using Mobile Money as the bridge and manual confirmation as the trust mechanism, we deliver a working product that solves a real problem – long queues and poor financial tracking – while staying within the feasibility limits of a school project.

The Django starter already provides a robust foundation; we will add only the necessary models and endpoints. The result will be clean, simple, and ready to present to supervisors and examiners.

---

*Document generated for the SmartSave project – Academic Year 2025/2026.*
