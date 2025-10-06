# Automotive Sales Analytics Chatbot 🚗

[![Deploy to Cloud Run](https://img.shields.io/badge/Deploy%20to-Cloud%20Run-blue?logo=google-cloud)](https://cloud.google.com/run)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An AI-powered conversational analytics platform for automotive sales data, built with Google Cloud Vertex AI Gemini, LangChain, and Streamlit.

## Features

✨ **Natural Language Querying**: Ask questions in plain English, get instant SQL-powered insights

🤖 **Powered by Gemini 2.0 Flash Lite**: Advanced language understanding with Google's latest AI

📊 **Comprehensive Analytics**: Sales, products, dealerships, customers, marketing, and competitive intelligence

🔗 **LangChain SQL Agent**: Intelligent query planning and execution with error handling

☁️ **Cloud-Native**: Fully serverless deployment on Google Cloud Run

🎨 **Modern UI**: Beautiful Streamlit interface with interactive visualizations

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│             │         │              │         │             │
│  Streamlit  │────────▶│  LangChain   │────────▶│  BigQuery   │
│     UI      │         │  SQL Agent   │         │  Database   │
│             │         │              │         │             │
└─────────────┘         └──────┬───────┘         └─────────────┘
                               │
                               │
                        ┌──────▼───────┐
                        │              │
                        │  Vertex AI   │
                        │    Gemini    │
                        │              │
                        └──────────────┘
```

## Project Structure

```
cloud/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── database.py          # BigQuery connection handler
│   ├── llm.py               # Vertex AI Gemini integration
│   ├── agent.py             # LangChain SQL agent
│   └── main.py              # Streamlit application
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container definition
├── .env.template            # Environment variables template
├── env-vars.yaml           # Cloud Run environment variables
├── .dockerignore           # Docker ignore rules
├── LOCAL_DEVELOPMENT.md    # Local development guide
├── DEPLOYMENT_GUIDE.md     # Cloud Run deployment guide
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Google Cloud Project with billing enabled
- BigQuery dataset `automotive_data`
- Python 3.11+
- Google Cloud SDK

### 1. Local Development

```bash
# Clone repository and navigate to cloud directory
cd chatbot/cloud

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your configuration

# Run locally (from cloud/ directory)
cd /path/to/chatbot/cloud
streamlit run app/main.py
```

See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for detailed instructions.

### 2. Deploy to Cloud Run

```bash
# Set variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE_NAME="automotive-chatbot"

# Build and deploy
gcloud builds submit --tag us-central1-docker.pkg.dev/${PROJECT_ID}/chatbot-images/automotive-chatbot:latest

gcloud run deploy ${SERVICE_NAME} \
  --image=us-central1-docker.pkg.dev/${PROJECT_ID}/chatbot-images/automotive-chatbot:latest \
  --platform=managed \
  --region=${REGION} \
  --memory=2Gi \
  --cpu=2 \
  --allow-unauthenticated \
  --env-vars-file=env-vars.yaml
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for comprehensive deployment instructions.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | Required |
| `GCP_LOCATION` | Vertex AI location | `us-central1` |
| `BIGQUERY_DATASET` | BigQuery dataset name | `automotive_data` |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.0-flash-lite-001` |
| `GEMINI_TEMPERATURE` | Model temperature | `0.1` |
| `LOG_LEVEL` | Logging level | `INFO` |

See `.env.template` for complete configuration options.

## Usage Examples

Once deployed, you can ask questions like:

**Sales Analysis:**
- "What were our total sales in California last quarter?"
- "Show me revenue trends by month for 2024"
- "Which dealership had the highest sales?"

**Product Insights:**
- "What are the top 5 best-selling vehicle models?"
- "Compare SUV sales to sedan sales"
- "What's the average discount on Toyota vehicles?"

**Customer Analytics:**
- "How many new customers registered in Q3 2024?"
- "Show customer registration trends over time"

**Competitive Intelligence:**
- "How do our sales compare to Tesla in California?"
- "Which competitor has the highest market share in Texas?"
- "Show competitor sales trends for the past year"

**Marketing Performance:**
- "What was our total marketing spend in 2023?"
- "Which campaigns had the largest budgets?"
- "List all campaigns that ran during summer 2024"

## Technology Stack

### Core Technologies
- **Frontend**: Streamlit 1.31.0
- **AI/ML**: Google Cloud Vertex AI (Gemini 2.0 Flash Lite)
- **Database**: Google BigQuery
- **Framework**: LangChain 0.1.10

### Key Dependencies
- `google-cloud-aiplatform`: Vertex AI SDK
- `google-cloud-bigquery`: BigQuery client
- `langchain-google-vertexai`: LangChain Vertex AI integration
- `langchain-community`: LangChain community tools
- `sqlalchemy-bigquery`: BigQuery SQLAlchemy dialect

See `requirements.txt` for complete dependency list.

## Security

### Service Account Permissions

The Cloud Run service account requires:
- `roles/bigquery.dataViewer` - Read BigQuery data
- `roles/bigquery.jobUser` - Run BigQuery jobs
- `roles/aiplatform.user` - Use Vertex AI
- `roles/logging.logWriter` - Write logs

### Authentication

**Local Development:**
- Uses `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Point to service account JSON key file

**Cloud Run:**
- Uses attached service account
- No credentials needed in container

## Monitoring

### View Logs

```bash
gcloud run services logs tail automotive-chatbot --region=us-central1
```

### Metrics

Access metrics in Cloud Console:
- Request count and latency
- Error rates
- CPU and memory usage
- Cold start frequency

### Alerts

Set up alerts for:
- High error rates (>5%)
- High latency (>10s)
- Service downtime

## Cost Estimation

### Development/Testing
- **Cloud Run**: ~$0-10/month (no minimum instances)
- **BigQuery**: Free tier (dataset is < 10GB)
- **Vertex AI**: ~$0.00125 per 1K characters

### Production (Low Traffic)
- **Cloud Run**: ~$40-60/month (1 minimum instance)
- **BigQuery**: Free tier
- **Vertex AI**: ~$50-100/month (1000 queries/day)

### Production (High Traffic)
- **Cloud Run**: ~$200-400/month (multiple instances)
- **BigQuery**: Free tier
- **Vertex AI**: Scales with usage

## Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install -r requirements.txt --force-reinstall
```

**"Authentication failed"**
```bash
gcloud auth application-default login
```

**"Cannot connect to BigQuery"**
```bash
gcloud services enable bigquery.googleapis.com
bq ls YOUR_PROJECT_ID:
```

**"Vertex AI initialization failed"**
```bash
gcloud services enable aiplatform.googleapis.com
```

See documentation for detailed troubleshooting guides.

## Development

### Running Tests

```bash
# Test database connection
python -c "from app.database import initialize_database; print(initialize_database())"

# Test LLM
python -c "from app.llm import initialize_llm; print(initialize_llm())"

# Test agent
python -c "from app.agent import initialize_agent; print(initialize_agent())"
```

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and modular

### Adding Features

1. Create new module in `app/`
2. Update `app/__init__.py`
3. Import in `main.py`
4. Test locally before deploying

## Performance Optimization

### Cold Start Reduction
- Use minimum instances (costs more)
- Optimize Docker image size
- Enable CPU boost

### Query Performance
- Use BigQuery best practices
- Add table indexes
- Limit result sizes
- Cache frequent queries

### Memory Management
- Adjust Cloud Run memory allocation
- Monitor memory usage
- Optimize Python code

## Roadmap

- [ ] **Authentication**: Add user authentication and authorization
- [ ] **Caching**: Implement query result caching
- [ ] **History**: Persistent conversation history
- [ ] **Export**: Export results to CSV/Excel
- [ ] **Visualizations**: Add charts and graphs
- [ ] **Multi-language**: Support multiple languages
- [ ] **Mobile**: Mobile-optimized UI
- [ ] **Voice**: Voice input/output

## Contributing

This is an internal project. For changes:
1. Test locally thoroughly
2. Document changes
3. Update relevant guides
4. Test deployment to staging
5. Deploy to production

## License

Internal use only. All rights reserved.

## Support

For issues or questions:
- Check documentation in this repository
- Review logs in Cloud Console
- Contact the AI Engineering team

## Acknowledgments

Built with:
- Google Cloud Platform
- Streamlit
- LangChain
- Vertex AI Gemini

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintained by**: AI Engineering Team
