# Human Vulnerability Score (HVS) System

## Overview

The Human Vulnerability Score (HVS) is a real-time vulnerability tracking system that measures employee susceptibility to phishing attacks on a scale of 0-100. The system automatically updates scores based on employee behavior during phishing simulations.

---

## 📊 Score Range and Levels

| Score Range | Level | Color | Description |
|------------|-------|-------|-------------|
| 0-24 | **Low** | 🟢 Green | Employee shows strong security awareness |
| 25-49 | **Medium** | 🟡 Yellow | Moderate vulnerability, needs attention |
| 50-74 | **High** | 🟠 Orange | High risk, immediate training required |
| 75-100 | **Critical** | 🔴 Red | Critical risk, urgent intervention needed |

---

## 🎯 Score Changes

### Negative Behaviors (Increase Score)

| Event | Score Change | Description |
|-------|-------------|-------------|
| **Opened Email** | +5 | Employee opened a phishing email |
| **Clicked SMS Link** | +20 | Employee clicked a link in SMS phishing campaign |
| **Clicked Phishing Link** | +25 | Employee clicked a malicious link in email |
| **Submitted Credentials** | +40 | Employee entered credentials on fake login page |

### Positive Behaviors (Decrease Score)

| Event | Score Change | Description |
|-------|-------------|-------------|
| **Watched Training** | -15 | Employee completed security awareness training |
| **Reported Phishing** | -25 | Employee correctly identified and reported phishing |

**Important:** Scores are automatically capped between 0 and 100.

---

## 🔄 Automatic Updates

HVS scores are **automatically updated** when the following events occur:

1. **Email Opened** - `/api/track/open/<token>` endpoint
2. **Link Clicked** - `/api/track/click/<token>` endpoint
3. **SMS Link Clicked** - `/api/sms/click/<token>` endpoint
4. **Credentials Submitted** - `/api/landing/capture/<token>` endpoint

No manual intervention required! The system tracks everything in real-time.

---

## 🏢 Department HVS

Each department has an **average HVS score** calculated from all active employees in that department.

**Example:**
```
IT Department:
  - 10 employees
  - Average HVS: 32.5 (Medium)
  - Range: 15-68
```

Department HVS helps identify which teams need targeted training.

---

## 🛠️ Setup

### 1. Run Migration Script

```bash
cd backend
python migrate_hvs.py
```

This will:
- Add `hvs_score` and `hvs_last_updated` columns to `employees` table
- Create `hvs_events` table for event tracking
- Initialize all existing employees with HVS score of 0

### 2. Restart Backend

```bash
python app.py
```

The HVS routes will now be active at `/api/hvs/*`

---

## 📡 API Endpoints

### Employee HVS

#### Get All Employee HVS Scores
```http
GET /api/hvs/employees
```

**Query Parameters:**
- `department` - Filter by department
- `min_score` - Minimum HVS score
- `max_score` - Maximum HVS score
- `level` - Filter by level (low, medium, high, critical)

**Example:**
```http
GET /api/hvs/employees?department=IT&level=high
```

**Response:**
```json
[
  {
    "id": "uuid",
    "email": "john.doe@company.com",
    "full_name": "John Doe",
    "department": "IT",
    "job_title": "Software Engineer",
    "hvs_score": 65,
    "hvs_level": "high",
    "hvs_last_updated": "2025-12-15T10:30:00"
  }
]
```

---

#### Get Employee HVS Detail
```http
GET /api/hvs/employees/<employee_id>
```

**Response:**
```json
{
  "employee": { /* full employee object */ },
  "hvs_score": 45,
  "hvs_level": "medium",
  "hvs_last_updated": "2025-12-15T10:30:00",
  "recent_events": [
    {
      "id": "uuid",
      "event_type": "clicked_link",
      "score_change": 25,
      "score_before": 20,
      "score_after": 45,
      "event_time": "2025-12-15T10:30:00",
      "campaign_id": "uuid"
    }
  ]
}
```

---

#### Get Employee HVS Events
```http
GET /api/hvs/employees/<employee_id>/events?limit=50&offset=0
```

**Response:**
```json
{
  "events": [ /* array of HVS events */ ],
  "total": 125,
  "limit": 50,
  "offset": 0
}
```

---

#### Manual HVS Update
```http
POST /api/hvs/employees/<employee_id>/manual-update
Content-Type: application/json

{
  "event_type": "watched_training",
  "notes": "Completed Q4 Security Training"
}
```

**Valid Event Types:**
- `watched_training`
- `reported_phishing`
- `clicked_link`
- `submitted_credentials`
- `clicked_sms`
- `opened_email`

**Response:**
```json
{
  "success": true,
  "employee_id": "uuid",
  "event_type": "watched_training",
  "old_score": 45,
  "new_score": 30,
  "score_change": -15,
  "hvs_level": "medium"
}
```

---

### Department HVS

#### Get All Department HVS Scores
```http
GET /api/hvs/departments
```

**Response:**
```json
[
  {
    "department": "IT",
    "employee_count": 25,
    "avg_hvs_score": 32.4,
    "min_hvs_score": 5,
    "max_hvs_score": 78,
    "hvs_level": "medium"
  },
  {
    "department": "HR",
    "employee_count": 15,
    "avg_hvs_score": 18.5,
    "min_hvs_score": 0,
    "max_hvs_score": 45,
    "hvs_level": "low"
  }
]
```

**Note:** Results are sorted by average score (highest risk first)

---

#### Get Department HVS Detail
```http
GET /api/hvs/departments/<department_name>
```

**Response:**
```json
{
  "department": "IT",
  "employee_count": 25,
  "avg_hvs_score": 32.4,
  "min_hvs_score": 5,
  "max_hvs_score": 78,
  "level_distribution": {
    "low": 10,
    "medium": 8,
    "high": 5,
    "critical": 2
  },
  "employees": [
    {
      "id": "uuid",
      "email": "employee@company.com",
      "full_name": "Employee Name",
      "job_title": "Position",
      "hvs_score": 78,
      "hvs_level": "high",
      "hvs_last_updated": "2025-12-15T10:30:00"
    }
  ]
}
```

---

### Overall Statistics

#### Get HVS Statistics
```http
GET /api/hvs/stats
```

**Response:**
```json
{
  "total_employees": 150,
  "avg_hvs_score": 28.5,
  "level_distribution": {
    "low": 80,
    "medium": 45,
    "high": 20,
    "critical": 5
  },
  "recent_events_7d": 342,
  "high_risk_employees": [
    {
      "id": "uuid",
      "email": "high.risk@company.com",
      "full_name": "High Risk Employee",
      "department": "Sales",
      "hvs_score": 85,
      "hvs_level": "critical"
    }
  ]
}
```

---

### Event History

#### Get Recent HVS Events
```http
GET /api/hvs/events/recent?limit=50&offset=0&event_type=clicked_link
```

**Query Parameters:**
- `limit` - Number of events to return (default: 50)
- `offset` - Pagination offset (default: 0)
- `event_type` - Filter by event type (optional)

**Response:**
```json
{
  "events": [
    {
      "id": "uuid",
      "employee_id": "uuid",
      "event_type": "clicked_link",
      "score_change": 25,
      "score_before": 20,
      "score_after": 45,
      "campaign_id": "uuid",
      "event_time": "2025-12-15T10:30:00",
      "notes": null,
      "employee": {
        "email": "employee@company.com",
        "full_name": "Employee Name",
        "department": "IT"
      }
    }
  ],
  "total": 1250,
  "limit": 50,
  "offset": 0
}
```

---

## 💾 Database Schema

### `employees` Table (New Columns)

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| `hvs_score` | INTEGER | 0 | Current HVS score (0-100) |
| `hvs_last_updated` | DATETIME | NULL | Last time HVS was updated |

### `hvs_events` Table (New)

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(36) | Primary key (UUID) |
| `employee_id` | VARCHAR(36) | Foreign key to employees |
| `event_type` | VARCHAR(50) | Type of event |
| `score_change` | INTEGER | Score change (positive or negative) |
| `score_before` | INTEGER | Score before event |
| `score_after` | INTEGER | Score after event |
| `campaign_id` | VARCHAR(36) | Related campaign (optional) |
| `event_time` | DATETIME | When event occurred |
| `notes` | TEXT | Additional notes (optional) |

---

## 🎓 Usage Examples

### Example 1: Find High-Risk Employees

```python
import requests

response = requests.get('http://localhost:5000/api/hvs/employees?level=critical')
critical_employees = response.json()

for emp in critical_employees:
    print(f"{emp['full_name']} ({emp['department']}): {emp['hvs_score']}")
```

### Example 2: Track Department Performance

```python
response = requests.get('http://localhost:5000/api/hvs/departments')
departments = response.json()

for dept in departments:
    print(f"{dept['department']}: Avg HVS = {dept['avg_hvs_score']} ({dept['hvs_level']})")
```

### Example 3: Record Training Completion

```python
response = requests.post(
    'http://localhost:5000/api/hvs/employees/employee-uuid/manual-update',
    json={
        'event_type': 'watched_training',
        'notes': 'Completed Security Awareness Training Q4 2024'
    }
)
result = response.json()
print(f"Score: {result['old_score']} → {result['new_score']}")
```

---

## 📈 Best Practices

### 1. **Regular Monitoring**
- Check high-risk employees weekly
- Review department scores monthly
- Track score trends over time

### 2. **Immediate Action for Critical Scores**
- HVS ≥ 75: Mandatory training within 24 hours
- HVS ≥ 50: Scheduled training within 1 week
- HVS ≥ 25: Reminder training within 2 weeks

### 3. **Reward Good Behavior**
- Recognize employees who report phishing
- Celebrate departments with low average HVS
- Gamify security awareness

### 4. **Data-Driven Training**
- Target training based on HVS levels
- Focus on departments with high averages
- Customize content based on event types

---

## 🔐 Security Notes

1. **Privacy**: HVS scores are internal metrics for training purposes only
2. **Access Control**: Limit HVS data access to security teams and HR
3. **Audit Trail**: All HVS events are logged in `hvs_events` table
4. **No PII in Events**: Events track behavior, not personal data

---

## 🐛 Troubleshooting

### HVS Score Not Updating

**Check:**
1. Employee exists in `employees` table with matching email
2. Employee `is_active = True`
3. Campaign target has correct email address
4. Backend logs for errors

**Solution:**
```bash
# Check employee
curl http://localhost:5000/api/employees

# Manually update if needed
curl -X POST http://localhost:5000/api/hvs/employees/<id>/manual-update \
  -H "Content-Type: application/json" \
  -d '{"event_type":"clicked_link"}'
```

### Migration Failed

**Solution:**
```bash
# Recreate database (WARNING: This deletes all data!)
cd backend
rm phishvision.db
python app.py  # This will create a fresh database
python seed_employees.py  # Re-seed employees if needed
```

---

## 📚 Integration with Existing Features

### Employee Management
- HVS scores automatically appear in employee lists
- Employee detail pages show HVS history
- Export includes HVS data

### Campaign Management
- Each click/open automatically updates HVS
- Campaign reports show HVS impact
- Target high-HVS employees for future campaigns

### Risk Scoring
- HVS complements existing UserRiskScore system
- Both metrics work together for comprehensive view
- HVS is per-employee, UserRiskScore is per-email

---

## 🎉 Quick Start Guide

1. **Run Migration:**
   ```bash
   python migrate_hvs.py
   ```

2. **Restart Backend:**
   ```bash
   python app.py
   ```

3. **Check Stats:**
   ```bash
   curl http://localhost:5000/api/hvs/stats
   ```

4. **View Departments:**
   ```bash
   curl http://localhost:5000/api/hvs/departments
   ```

5. **Done!** HVS is now tracking all phishing simulations automatically.

---

## 📞 Support

For questions or issues with the HVS system:
- Check backend logs: `backend/logs/` or terminal output
- Review HVS events: `GET /api/hvs/events/recent`
- Test with manual update: `POST /api/hvs/employees/<id>/manual-update`

---

**Built for PhishVision** 🎣
A comprehensive phishing awareness platform
