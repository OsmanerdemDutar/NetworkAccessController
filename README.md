# 🛡️ Network Access Control (NAC) System

This project is a high-performance **Network Access Control (NAC) System** developed as a part of the network security infrastructure simulation. The system is designed to provide secure, centralized authentication and resource management using **FreeRADIUS**, **FastAPI**, **PostgreSQL**, and **Redis** within a Dockerized ecosystem.

---

## 🚀 Project Overview

The system provides a robust layer of security for network infrastructures by validating users and devices before granting network access. It implements a modern authentication flow where traditional RADIUS protocols meet contemporary Web APIs, ensuring both legacy compatibility and modern security standards.

### Key Features

*   **Dynamic Authentication Engine:** Implements a custom logic that intercepts RADIUS requests and validates them through a Python-based REST API.
*   **Security-First Architecture:** Passwords are never stored in plain text; the system utilizes **SHA-256** hashing for all credential verifications.
*   **Rate-Limiting & Brute-Force Protection:** Integrated with **Redis** to track failed login attempts and temporarily block suspicious activities.
*   **MAB (MAC Authentication Bypass):** Supports IoT and non-interactive device authentication through MAC address validation.
*   **Dockerized Microservices:** Seamless deployment and scalability using Docker Compose for all components.

---

## 🛠️ Technical Implementation

### System Architecture

The project follows a microservices-oriented approach where each component has a specific responsibility:

1.  **FreeRADIUS:** Acts as the gateway for NAS (Network Access Server) devices, using the `rest` module to communicate with the backend.
2.  **FastAPI (Backend):** The core intelligence of the system. It handles hashing, database queries, and logic execution.
3.  **PostgreSQL (Persistence):** Stores user credentials, device MAC addresses, and authorization levels.
4.  **Redis (Security):** Maintains a high-speed volatile storage for tracking login attempts and enforcing rate limits.

---

## 💻 Usage

### Prerequisites

*   **Docker & Docker Compose**
*   **Terminal** (CMD, PowerShell, or Bash)

### Compilation and Execution

To spin up the entire infrastructure, use the following command in the project root:

```bash
docker-compose up -d --build
```

# Operational Commands (Testing)

You can verify the system integrity using the following operational tasks:

---

## 🛠️ System Administration & Testing Guide

To fully manage and troubleshoot the NAC ecosystem, use the following administrative commands. These ensure operational integrity and real-time monitoring.

### 1. User & Device Management (Database CRUD)
Manage the PostgreSQL backend directly to audit or modify authorized entities:

*   **List All Registered Users & MAC Addresses:**
    ```bash
    docker exec -it s3m_nac_db psql -U postgres -d nac_database -c "SELECT * FROM radcheck;"
    ```
*   **Audit Authentication Logs (Database Level):**
    ```bash
    docker exec -it s3m_nac_db psql -U postgres -d nac_database -c "SELECT * FROM radpostauth;"
    ```

### 2. Real-Time Diagnostics (Live Logs)
Monitor the system's "heartbeat" to debug failed authentication attempts or API errors:

*   **Monitor FreeRADIUS Debug Output:**
    ```bash
    docker logs -f s3m_nac_freeradius
    ```
*   **Follow FastAPI Backend Requests:**
    ```bash
    docker logs -f s3m_nac_api
    ```

### 3. Security & Cache Inspection (Redis)
Inspect the brute-force prevention layer and manage the rate-limiting cache:

*   **Check Currently Blocked IP/Users (Failed Attempt Counters):**
    ```bash
    docker exec -it s3m_nac_redis redis-cli KEYS "failed_attempts:*"
    ```
*   **Manual Security Reset (Flush Rate-Limit Cache):**
    ```bash
    docker exec -it s3m_nac_redis redis-cli FLUSHALL
    ```

### 4. Basic Connectivity Tests
Verify the end-to-end authentication flow using standard RADIUS utilities:

*   **Standard PAP Authentication:**
    ```bash
    docker exec -it s3m_nac_freeradius radtest testuser 12345 localhost 0 testing123
    ```
*   **MAB (MAC Authentication Bypass) Simulation:**
    ```bash
    echo "User-Name=AA:BB:CC:DD:EE:FF, User-Password=AA:BB:CC:DD:EE:FF" | docker exec -i s3m_nac_freeradius radclient -x localhost:1812 auth testing123
    ```

### 5. Service Orchestration
Verify the health and status of all microservices:

```bash
docker-compose ps
```

---

## 📝 Reference Standards

The system enforces strict operational standards:

- **Authentication Port:** 1812 (UDP)  
- **Accounting Port:** 1813 (UDP)  
- **API Protocol:** JSON over HTTP/POST  
- **Rate Limit Threshold:** 3 failed attempts within a 60-second window  

---

## 📦 Project Structure

```bash
.
├── api/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── freeradius/
│   ├── Dockerfile
│   ├── default
│   └── rest
├── docker-compose.yml
├── init.sql
├── .env
└── README.md
```

---

## 🚀 Full Setup Guide

### 1. Clone the Repository

```bash id="cln123"
git clone https://github.com/your-repo/nac-system.git
cd nac-system
```

---

### 2. Start the System

```bash id="start001"
docker-compose up -d --build
```

---

### 3. Verify Database Initialization

Once the containers are up, the system automatically initializes the database schema. You can verify the tables by accessing the PostgreSQL container:

```bash
docker exec -it s3m_nac_db psql -U postgres -d nac_database -c "\dt"
```

---

## 🛠️ Detailed Functional Logic

### 🔐 Authentication Flow

The NAC system follows a strict security pipeline for every network access request:

1.  **NAS Gateway:** The client or network switch sends an `Access-Request` to the **FreeRADIUS** container.
2.  **REST Interceptor:** FreeRADIUS intercepts the request and forwards the credentials to the **FastAPI** backend via the `rest` module.
3.  **Security Pipeline:**
    *   **Rate-Limit Check:** **Redis** verifies if the user is currently locked out due to multiple failed attempts.
    *   **Credential Hashing:** The API hashes the incoming password using **SHA-256**.
    *   **Verification:** The resulting hash is compared against the secure record in **PostgreSQL**.
4.  **Response:** Upon successful verification, the system returns an `Access-Accept` with a custom "Reply-Message".

### 🛡️ Brute-Force Prevention

To safeguard against automated attacks, the system implements a dynamic lockout mechanism:

*   **Lockout Threshold:** 3 consecutive failed attempts.
*   **Cooldown Period:** 60-second window managed by Redis expiration.
*   **Auto-Reset:** A successful login attempt automatically clears the failure counter for that specific user.

### 🌐 API Endpoints

The backend services are accessible via the following REST endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/auth/radius` | `POST` | Core authentication endpoint for FreeRADIUS REST module. |
| `/health` | `GET` | Service health check and database connectivity status. |
| `/docs` | `GET` | Interactive Swagger UI documentation (FastAPI default). |


---

## 📊 Technical Specifications

The system utilizes the following industry standards for network integrity:

| Feature | Protocol / Algorithm |
| :--- | :--- |
| **RADIUS Protocol** | RFC 2865 |
| **Hashing Mechanism** | SHA-256 (Secure Hash Algorithm 2) |
| **Data Persistence** | PostgreSQL (Relational) |
| **Caching/Rate-Limit** | Redis (In-memory Data Store) |
| **Communication** | JSON over HTTP/POST |

---

## 👨‍💻 Author

**Osman Erdem Dutar**  
Computer Engineering Student  
*Hacettepe University*  
[GitHub Profile](https://github.com/OsmanerdemDutar)

---

> **Note:** This project is developed for educational purposes in network security and infrastructure management.