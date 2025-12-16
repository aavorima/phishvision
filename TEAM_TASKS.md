# PhishVision Team Task Distribution

**Last Updated: December 8, 2025**

## Team Structure
- **You (Developer)** - Lead development, architecture
- **2 Red Teamers** - Offensive security, phishing templates, attack simulation
- **4 Blue Teamers** - Defensive security, SOC features, detection, analysis

---

## 📊 Overall Progress Summary

| Feature | Status | Owner |
|---------|--------|-------|
| SOC Response Timeline | ✅ DONE | Blue 2 / Dev |
| SOC Dashboard | ✅ DONE | Blue 1 / Dev |
| User Risk Scoring | ✅ DONE | Blue 3 / Dev |
| Employee Management | ✅ DONE | Dev |
| Template Editor | ✅ DONE | Dev |
| ML Classifier | ❌ TODO | Blue 4 |
| Sentiment Analysis | ❌ TODO | Blue 4 |
| New Templates (15+) | 🔄 IN PROGRESS | Red 1 |
| NLP Bypass Testing | 🔄 IN PROGRESS | Red 2 |

---

## Task Assignment by Role

### 🔴 RED TEAM (2 people)

**Red Teamer 1: Template & Attack Specialist**

| Week | Task | Deliverable |
|------|------|-------------|
| Week 1 | Create 15 new phishing templates | HTML templates in multiple categories |
| Week 1 | Research real-world phishing campaigns | Document 10 current attack patterns |
| Week 2 | Test AI template generator | Quality report, improvement suggestions |
| Week 2 | Create multi-language templates | 5 Azerbaijani, 5 Turkish templates |
| Week 3 | Demo attack scenarios | 3 realistic demo campaigns |

**Specific Tasks:**
```
1. Template Categories to Create:
   - IT/Helpdesk (password reset, software update)
   - HR (benefits enrollment, policy update)
   - Finance (invoice, expense report)
   - Executive/CEO fraud (urgent wire transfer)
   - Shipping (package delivery, customs)
   - Social media (account verification)

2. For Each Template Document:
   - Target audience
   - Psychological triggers used
   - Red flags (for training)
   - Difficulty level (easy/medium/hard)
   - Success rate estimate
```

**Red Teamer 2: Evasion & Realism Specialist**

| Week | Task | Deliverable |
|------|------|-------------|
| Week 1 | Research email evasion techniques | Document for NLP improvement |
| Week 1 | Test current NLP analyzer | List of bypasses found |
| Week 2 | Create "hard" phishing samples | 10 sophisticated emails |
| Week 2 | Improve AI prompt for templates | Better Gemini prompts |
| Week 3 | Penetration test the platform | Security report |

**Specific Tasks:**
```
1. Test NLP Analyzer Against:
   - Unicode tricks (homoglyph attacks)
   - Base64 encoded content
   - Image-only emails
   - Zero-width characters
   - Legitimate-looking domains

2. Document Evasion Techniques:
   - How attackers bypass filters
   - Social engineering tactics
   - Current trends (QR codes, voice phishing)

3. Improve AI Template Generation:
   - Better prompts for Gemini
   - More realistic outputs
   - Context-aware generation
```

---

### 🔵 BLUE TEAM (4 people)

**Blue Teamer 1: SOC Dashboard Lead** ✅ COMPLETED

| Week | Task | Deliverable | Status |
|------|------|-------------|--------|
| Week 1 | Design SOC dashboard layout | Figma/sketch mockup | ✅ Done |
| Week 1 | Implement SOC metrics display | Dashboard components | ✅ Done |
| Week 2 | Create incident visualization | Charts, timelines | ✅ Done |
| Week 2 | Add risk heatmaps | Department risk view | ❌ TODO |
| Week 3 | Polish and integrate | Final dashboard | 🔄 In Progress |

**Files Created:**
- ✅ `frontend/src/components/Dashboard.js` - Updated with SOC metrics
- ❌ `frontend/src/components/RiskHeatmap.js` - TODO

---

**Blue Teamer 2: SOC Response Timeline** ✅ COMPLETED

| Week | Task | Deliverable | Status |
|------|------|-------------|--------|
| Week 1 | Design incident workflow | State diagram | ✅ Done |
| Week 1 | Create SecurityIncident model | Database schema | ✅ Done |
| Week 2 | Build timeline API | Backend routes | ✅ Done |
| Week 2 | Create timeline UI | Frontend component | ✅ Done |
| Week 3 | Add incident management | CRUD operations | ✅ Done |

**Files Created:**
- ✅ `backend/routes/soc_routes.py` - Full API
- ✅ `backend/models.py` - SecurityIncident model
- ✅ `frontend/src/components/SOCTimeline.js` - Timeline UI

---

**Blue Teamer 3: User Risk Scoring** ✅ COMPLETED

| Week | Task | Deliverable | Status |
|------|------|-------------|--------|
| Week 1 | Design risk scoring algorithm | Documentation | ✅ Done |
| Week 1 | Create UserRiskScore model | Database schema | ✅ Done |
| Week 2 | Implement scoring API | Backend routes | ✅ Done |
| Week 2 | Build risk dashboard UI | Frontend component | ✅ Done |
| Week 3 | Add user profiles | Individual risk pages | ✅ Done |

**Files Created:**
- ✅ `backend/routes/risk_routes.py` - Full API
- ✅ `backend/models.py` - UserRiskScore model with calculate_risk_score()
- ✅ `frontend/src/components/UserRiskDashboard.js` - Risk dashboard

---

**Blue Teamer 4: NLP Enhancement & ML** ❌ TODO

| Week | Task | Deliverable | Status |
|------|------|-------------|--------|
| Week 1 | Research ML models for phishing | Model selection report | ⏳ Pending |
| Week 1 | Gather training data | Dataset (1000+ samples) | ⏳ Pending |
| Week 2 | Train ML classifier | Working model | ❌ TODO |
| Week 2 | Integrate with existing NLP | Hybrid system | ❌ TODO |
| Week 3 | Add sentiment analysis | Emotional detection | ❌ TODO |

**Files to Create:**
- ❌ `backend/services/ml_classifier.py` - TODO
- ❌ `backend/services/sentiment_analyzer.py` - TODO
- ❌ `backend/data/training_data.csv` - TODO

**Specific Tasks Still Needed:**
```
1. ML Model Options:
   - Random Forest (recommended - easy, good accuracy)
   - Naive Bayes (simple, fast)

2. Training Data Sources:
   - Kaggle phishing datasets
   - Existing templates (as malicious)
   - Legitimate emails (as safe)

3. Integration:
   - Keep existing NLP as fallback
   - ML provides probability (0-1)
   - Combine scores for final classification
```

---

## 👨‍💻 YOUR TASKS (Developer/Lead)

| Week | Task | Deliverable | Status |
|------|------|-------------|--------|
| Week 1 | Set up development environment | Docker, shared DB | ✅ Done |
| Week 1 | Create API structure for new features | Route templates | ✅ Done |
| Week 1 | Code review all PRs | Quality control | ✅ Done |
| Week 1 | Employee Management System | Full CRUD | ✅ Done |
| Week 1 | Template Editor | Code editor UI | ✅ Done |
| Week 2 | Integration of all components | Working system | 🔄 In Progress |
| Week 2 | Fix bugs, resolve conflicts | Stable codebase | 🔄 In Progress |
| Week 3 | Final integration | Complete product | ⏳ Pending |
| Week 3 | Demo preparation | Demo script, data | ⏳ Pending |

**Your Specific Responsibilities:**
```
1. Architecture Decisions:
   - Database schema approval
   - API design review
   - Frontend component structure

2. Code Quality:
   - Review all pull requests
   - Ensure consistent coding style
   - Security review

3. Integration:
   - Merge all features together
   - Resolve conflicts
   - End-to-end testing

4. Demo Prep:
   - Create demo accounts
   - Generate realistic data
   - Write demo script
   - Practice presentation
```

---

## Daily Standup Questions

Each team member should answer:
1. What did you complete yesterday?
2. What are you working on today?
3. Any blockers?

---

## Communication Channels

```
Recommended Setup:
- Discord/Telegram group for quick chat
- GitHub for code (branches per feature)
- Shared doc for documentation
- Daily 15-min standup (video/voice)
```

---

## Git Branch Strategy

```
main
├── feature/soc-dashboard      (Blue 1)
├── feature/soc-timeline       (Blue 2)
├── feature/risk-scoring       (Blue 3)
├── feature/ml-classifier      (Blue 4)
├── feature/new-templates      (Red 1)
└── feature/nlp-improvements   (Red 2)
```

**Rules:**
- Never push directly to main
- Create PR for review
- You (developer) approves all merges
- Test before merging

---

## Week-by-Week Schedule

### Week 1 (Dec 1-7): Foundation

| Day | Red Team | Blue Team | You |
|-----|----------|-----------|-----|
| Mon | Template research | SOC design | Setup branches |
| Tue | Start templates | Start models | API templates |
| Wed | Continue templates | Continue models | Review PRs |
| Thu | Test NLP | Build routes | Integration help |
| Fri | Document bypasses | Build UI | Code review |
| Sat | More templates | More UI | Bug fixes |
| Sun | Polish | Polish | Testing |

### Week 2 (Dec 8-14): Development

| Day | Red Team | Blue Team | You |
|-----|----------|-----------|-----|
| Mon | Hard templates | ML training | Integration |
| Tue | AI prompt improve | ML integration | Integration |
| Wed | Testing | Sentiment | Code review |
| Thu | Demo scenarios | Risk profiles | Bug fixes |
| Fri | Final templates | Final features | Testing |
| Sat | Security test | Polish | Integration |
| Sun | Documentation | Documentation | Demo prep |

### Week 3 (Dec 15-18): Polish & Demo

| Day | Red Team | Blue Team | You |
|-----|----------|-----------|-----|
| Mon | Demo attacks | Final polish | Full testing |
| Tue | Help demo | Help demo | Demo data |
| Wed | Practice | Practice | Demo script |
| Thu | Final prep | Final prep | Final prep |
| Fri | **COMPETITION DAY** | | |

---

## What to Tell Each Person

### Tell Red Teamer 1:
> "Your job is to create realistic phishing templates. We need 15 new templates across different categories - IT helpdesk, HR, Finance, CEO fraud, shipping. For each template, document what makes it convincing and what red flags users should notice. Also create 5 Azerbaijani and 5 Turkish templates since that's our unique advantage."

### Tell Red Teamer 2:
> "Your job is to test our NLP analyzer and make it better. Try to bypass it with tricky phishing emails - use unicode tricks, encoded content, image-only emails. Document what works and what doesn't. Also improve our AI template generator by writing better prompts for Gemini. At the end, do a security test of the whole platform."

### Tell Blue Teamer 1:
> "You own the SOC Dashboard. Design and build a professional security operations dashboard showing metrics like Mean Time to Detect, incident counts, risk heatmaps by department. Use Recharts for visualizations. Make it look impressive for the judges."

### Tell Blue Teamer 2:
> "You own the SOC Response Timeline - this is a key competition requirement. Build the incident tracking system with states (detected → investigating → contained → resolved). Create both the backend API and the frontend timeline view. Users should see when incidents happened and how fast they were resolved."

### Tell Blue Teamer 3:
> "You own User Risk Scoring. Create a system that gives each user a risk score from 0-100 based on how they respond to phishing campaigns. Build a dashboard showing high-risk users, department comparisons, and individual user profiles with their history."

### Tell Blue Teamer 4:
> "You own the ML/AI enhancement for our email analyzer. Train a machine learning model (Random Forest recommended) to classify emails. Find training data from Kaggle, train the model, and integrate it with our existing NLP analyzer. Also add sentiment analysis to detect emotional manipulation."

---

## Files Each Person Should Create

### Red Teamer 1:
```
backend/templates/
├── it_templates.py
├── hr_templates.py
├── finance_templates.py
├── ceo_fraud_templates.py
├── shipping_templates.py
└── azerbaijani_templates.py
```

### Red Teamer 2:
```
docs/
├── nlp_bypass_report.md
├── evasion_techniques.md
└── security_assessment.md

backend/services/
└── ai_template_generator.py (improvements)
```

### Blue Teamer 1:
```
frontend/src/components/
├── SOCDashboard.js
├── RiskHeatmap.js
├── MetricCards.js
└── ThreatDistribution.js
```

### Blue Teamer 2:
```
backend/
├── routes/soc_routes.py
└── models.py (SecurityIncident)

frontend/src/components/
└── SOCTimeline.js
```

### Blue Teamer 3:
```
backend/
├── routes/risk_routes.py
├── services/risk_scorer.py
└── models.py (UserRiskScore)

frontend/src/components/
├── UserRiskDashboard.js
└── UserRiskProfile.js
```

### Blue Teamer 4:
```
backend/
├── services/ml_classifier.py
├── services/sentiment_analyzer.py
└── data/training_data.csv
```

---

## Success Criteria

### Must Have (Competition Requirements):
- [x] SOC Response Timeline working ✅
- [x] Full Dashboard with SOC metrics ✅
- [x] Template builder ✅
- [x] NLP analyzer ✅

### Should Have (Impressive):
- [x] User risk scoring ✅
- [ ] ML-based classification ❌ TODO
- [ ] 20+ templates 🔄 IN PROGRESS
- [x] Multi-language support ✅ (language field in templates)

### Nice to Have (Wow Factor):
- [ ] Sentiment analysis ❌ TODO
- [ ] Risk heatmaps ❌ TODO
- [ ] Real-time updates ⏳ Optional
- [ ] Export/reports ⏳ Optional

---

## Questions?

If anyone is stuck:
1. Check existing code in similar files
2. Ask in team chat
3. Escalate to you (developer lead)

Good luck team! 🚀
