# Project Index - Automotive Sales Analytics Chatbot

## 📁 Complete File Reference

### 📋 Core Application Files

#### `/app/` - Application Package

| File | Lines | Purpose |
|------|-------|---------|
| **`__init__.py`** | 25 | Package initialization, exports all public interfaces |
| **`config.py`** | 85 | Configuration management, environment variables, validation |
| **`database.py`** | 208 | BigQuery connection, SQLDatabase wrapper, connection pooling |
| **`llm.py`** | 161 | Vertex AI Gemini integration, LLM initialization, configuration |
| **`agent.py`** | 245 | LangChain SQL agent, query processing, result formatting |
| **`main.py`** | 446 | Streamlit UI, chat interface, system initialization |

**Total Application Code**: ~1,170 lines

---

### 🐳 Container & Deployment

| File | Purpose |
|------|---------|
| **`Dockerfile`** | Multi-stage Docker build, Python 3.11 slim, non-root user |
| **`.dockerignore`** | Optimize Docker build, exclude unnecessary files |
| **`requirements.txt`** | 20 Python dependencies with pinned versions |
| **`deploy.sh`** | Automated deployment script (executable, 232 lines) |
| **`env-vars.yaml`** | Cloud Run environment variables template |

---

### ⚙️ Configuration Files

| File | Purpose |
|------|---------|
| **`.env.template`** | Environment variables template for local development |
| **`.gitignore`** | Git ignore rules for credentials, cache, logs |

---

### 📚 Documentation (5 Files, ~2,300 lines)

| File | Lines | Description | Audience |
|------|-------|-------------|----------|
| **`README.md`** | 247 | Main documentation, overview, quick start | Everyone |
| **`LOCAL_DEVELOPMENT.md`** | 285 | Local setup, testing, debugging | Developers |
| **`DEPLOYMENT_GUIDE.md`** | 468 | Cloud Run deployment, configuration, monitoring | DevOps |
| **`TROUBLESHOOTING.md`** | 445 | Common issues and solutions | Support |
| **`QUICK_REFERENCE.md`** | 225 | Commands cheat sheet, quick lookup | Everyone |
| **`PROJECT_SUMMARY.md`** | 530 | Complete project details, handoff doc | Management |

---

### 🧪 Testing & Utilities

| File | Lines | Purpose |
|------|-------|---------|
| **`test_setup.py`** | 380 | Comprehensive test suite, validates all components |

---

## 📖 Documentation Reading Order

### For First-Time Users
1. **README.md** - Start here for overview
2. **QUICK_REFERENCE.md** - Quick commands
3. **LOCAL_DEVELOPMENT.md** - Set up locally
4. **TROUBLESHOOTING.md** - When you hit issues

### For Deployment
1. **README.md** - Understand the project
2. **DEPLOYMENT_GUIDE.md** - Follow deployment steps
3. **QUICK_REFERENCE.md** - Deployment commands
4. **TROUBLESHOOTING.md** - If deployment fails

### For Development
1. **LOCAL_DEVELOPMENT.md** - Set up environment
2. **README.md** - Understand architecture
3. **Code files** - Review implementation
4. **TROUBLESHOOTING.md** - Debug issues

### For Management/Handoff
1. **PROJECT_SUMMARY.md** - Complete overview
2. **README.md** - Quick reference
3. **DEPLOYMENT_GUIDE.md** - Operations guide

---

## 🗂️ File Categorization

### Must Read (Start Here)
- ✅ README.md
- ✅ QUICK_REFERENCE.md
- ✅ TROUBLESHOOTING.md

### Implementation Files
- 📝 app/config.py
- 📝 app/database.py
- 📝 app/llm.py
- 📝 app/agent.py
- 📝 app/main.py

### Setup & Configuration
- ⚙️ .env.template
- ⚙️ env-vars.yaml
- ⚙️ requirements.txt
- ⚙️ Dockerfile

### Guides (Choose Based on Role)
- 👨‍💻 LOCAL_DEVELOPMENT.md (Developers)
- ☁️ DEPLOYMENT_GUIDE.md (DevOps)
- 📊 PROJECT_SUMMARY.md (Management)

### Tools & Scripts
- 🔧 deploy.sh (Automated deployment)
- 🧪 test_setup.py (Validation)

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (main.py)                   │
│  • Chat interface • Sample questions • System status        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Configuration Layer (config.py)                │
│  • Environment variables • Validation • Settings            │
└────────┬────────────────────┬───────────────────┬───────────┘
         │                    │                   │
         ▼                    ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   Database     │  │      LLM       │  │     Agent      │
│  (database.py) │  │    (llm.py)    │  │   (agent.py)   │
├────────────────┤  ├────────────────┤  ├────────────────┤
│ • BigQuery     │  │ • Vertex AI    │  │ • LangChain    │
│ • SQLDatabase  │  │ • Gemini 2.0   │  │ • SQL Tools    │
│ • Connection   │  │ • Chat Model   │  │ • Query Logic  │
└────────┬───────┘  └────────┬───────┘  └────────┬───────┘
         │                   │                    │
         └───────────────────┴────────────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │   External Services   │
                 ├───────────────────────┤
                 │ • BigQuery API        │
                 │ • Vertex AI API       │
                 │ • Cloud Logging       │
                 └───────────────────────┘
```

---

## 🔍 Quick File Lookup

### Need to...

**Configure the application?**
→ `.env.template` (local) or `env-vars.yaml` (Cloud Run)

**Understand how queries work?**
→ `app/agent.py` (SQL agent logic)

**Change the UI?**
→ `app/main.py` (Streamlit interface)

**Connect to different database?**
→ `app/database.py` + `app/config.py`

**Use different LLM model?**
→ `app/llm.py` + `app/config.py`

**Deploy to Cloud Run?**
→ `DEPLOYMENT_GUIDE.md` or run `./deploy.sh`

**Debug local issues?**
→ `TROUBLESHOOTING.md` + run `python test_setup.py`

**See all commands?**
→ `QUICK_REFERENCE.md`

**Get project overview?**
→ `README.md` or `PROJECT_SUMMARY.md`

---

## 📊 Project Statistics

### Code Metrics
- **Total Files**: 19
- **Application Code**: ~1,170 lines (6 files)
- **Documentation**: ~2,300 lines (6 files)
- **Configuration**: 5 files
- **Tests**: 380 lines (1 file)
- **Scripts**: 232 lines (1 file)

### Components
- **Streamlit UI**: 1 main file
- **Backend Logic**: 5 modules
- **External Services**: 3 (BigQuery, Vertex AI, Cloud Run)
- **Dependencies**: 20 packages

### Documentation Coverage
- ✅ Architecture explained
- ✅ Local development guide
- ✅ Cloud deployment guide
- ✅ Troubleshooting guide
- ✅ API documentation (docstrings)
- ✅ Configuration reference
- ✅ Quick reference card

---

## 🎯 Common Workflows

### 1️⃣ First Time Setup (Local)
```
1. Read: README.md
2. Follow: LOCAL_DEVELOPMENT.md
3. Configure: .env.template → .env
4. Test: python test_setup.py
5. Run: streamlit run app/main.py
6. If issues: TROUBLESHOOTING.md
```

### 2️⃣ Deploy to Cloud
```
1. Read: DEPLOYMENT_GUIDE.md
2. Configure: env-vars.yaml
3. Run: ./deploy.sh
4. Verify: Check Cloud Run console
5. If issues: TROUBLESHOOTING.md
```

### 3️⃣ Make Code Changes
```
1. Edit: app/*.py files
2. Test locally: streamlit run app/main.py
3. Validate: python test_setup.py
4. Build: docker build -t test .
5. Deploy: ./deploy.sh
```

### 4️⃣ Troubleshoot Issues
```
1. Check: TROUBLESHOOTING.md
2. Run: python test_setup.py
3. Review: Logs (local terminal or Cloud Run)
4. Verify: QUICK_REFERENCE.md (commands)
5. Debug: Enable LOG_LEVEL=DEBUG
```

---

## 🔗 Related Files

### Configuration Chain
```
.env.template
    ↓
.env (local dev)
    ↓
app/config.py
    ↓
app/*.py (all modules)
```

### Deployment Chain
```
requirements.txt
    ↓
Dockerfile
    ↓
.dockerignore
    ↓
deploy.sh
    ↓
Cloud Run (env-vars.yaml)
```

### Documentation Chain
```
README.md (overview)
    ↓
├─→ LOCAL_DEVELOPMENT.md (for developers)
├─→ DEPLOYMENT_GUIDE.md (for DevOps)
├─→ TROUBLESHOOTING.md (for support)
├─→ QUICK_REFERENCE.md (for everyone)
└─→ PROJECT_SUMMARY.md (for management)
```

---

## 🎓 Learning Path

### Beginner (Never seen the project)
1. README.md (30 min)
2. QUICK_REFERENCE.md (10 min)
3. Run test_setup.py (5 min)
4. Try sample queries (15 min)

### Intermediate (Want to develop)
1. LOCAL_DEVELOPMENT.md (45 min)
2. Review app/*.py (60 min)
3. Make small change (30 min)
4. Test locally (15 min)

### Advanced (Ready to deploy)
1. DEPLOYMENT_GUIDE.md (60 min)
2. Configure env-vars.yaml (10 min)
3. Run deploy.sh (15 min)
4. Monitor and optimize (30 min)

---

## 📞 Support Matrix

| Issue Type | Check File | Action |
|------------|-----------|--------|
| Can't install | TROUBLESHOOTING.md § 1 | Run test_setup.py |
| Auth errors | TROUBLESHOOTING.md § 2 | Check credentials |
| Config issues | TROUBLESHOOTING.md § 3 | Verify .env |
| BigQuery errors | TROUBLESHOOTING.md § 4 | Test bq access |
| Vertex AI errors | TROUBLESHOOTING.md § 5 | Enable APIs |
| UI issues | TROUBLESHOOTING.md § 6 | Clear cache |
| Docker issues | TROUBLESHOOTING.md § 7 | Check Dockerfile |
| Deploy errors | TROUBLESHOOTING.md § 8 | Review logs |
| Query errors | TROUBLESHOOTING.md § 9 | Check agent logs |
| Performance | TROUBLESHOOTING.md § 10 | Increase resources |

---

## ✅ Checklist: Before First Deployment

- [ ] Read README.md
- [ ] Run python test_setup.py
- [ ] Verify BigQuery data uploaded (480 rows across 6 tables)
- [ ] Configure env-vars.yaml with your project
- [ ] Grant service account permissions
- [ ] Enable all required APIs
- [ ] Review DEPLOYMENT_GUIDE.md
- [ ] Run ./deploy.sh
- [ ] Test deployed service
- [ ] Set up monitoring/alerts

---

## 🚀 Quick Command Reference

```bash
# Test everything
python test_setup.py

# Run locally
streamlit run app/main.py

# Deploy to Cloud
./deploy.sh

# View logs
gcloud run services logs tail SERVICE_NAME --region=REGION
```

---

**Last Updated**: October 2025  
**Version**: 1.0.0  
**Total Project Size**: ~3,500 lines of code + documentation
