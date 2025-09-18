# OpenML Crawler

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://readthedocs.org/projects/openmlcrawler/badge/?version=latest)](https://krish567366.github.io/openmlcrawler/)
[![DOI](https://zenodo.org/badge/1058899260.svg)](https://doi.org/10.5281/zenodo.17144991)

A unified framework for crawling and preparing ML-ready datasets from various sources including web APIs, open data portals, and custom data sources.

## Features

### 🔌 **Connectors (Free APIs + Curated Data Sources)**

- **Weather**: Open-Meteo, OpenWeather, NOAA, Weather Underground
- **Social Media**: Twitter/X API, Reddit API, Facebook Graph API, Instagram
- **Government Data**: US data.gov, EU Open Data, UK data.gov.uk, Indian data.gov.in
- **Finance**: Yahoo Finance, Alpha Vantage, FRED, CoinMarketCap
- **Knowledge**: Wikipedia, Wikidata
- **News**: NewsAPI, Google News, Bing News, NY Times
- **Social/Dev**: GitHub, Stack Exchange
- **Health**: CDC, WHO, PubMed, ClinicalTrials.gov
- **Agriculture**: FAO, USDA, Government open data portals
- **Energy**: EIA, IEA

### 🕷️ **Generic Web Crawling**

- Support for CSV, JSON, XML, HTML parsing
- PDF parsing with pdfplumber/PyPDF2
- Async crawling with aiohttp
- Headless browser mode with Playwright/Selenium
- Auto format detection (mimetype, file extension)

### 🧹 **Data Cleaning & Processing**

- Deduplication and anomaly detection
- Missing value handling
- Auto type detection (int, float, datetime, category)
- Text cleaning (stopwords, stemming, lemmatization)
- NLP utilities: language detection, translation, NER

### 🤖 **ML-Ready Dataset Preparation**

- Schema detection (features/labels)
- Feature/target separation (`X`, `y`)
- Train/validation/test split
- Normalization & encoding (optional)
- Export to CSV, JSON, Parquet
- Ready-made loaders for scikit-learn, PyTorch, TensorFlow
- Streaming mode for big data (generator-based)

### 🔒 **Advanced Data Quality & Privacy**

- **Data Quality Assessment**: Missing data analysis, duplicate detection, outlier analysis, trust scoring
- **PII Detection**: Automatic detection of personal identifiable information
- **Data Anonymization**: Hash, mask, redact methods for privacy protection
- **Compliance Checking**: GDPR, HIPAA compliance validation
- **Quality Scoring**: Automated data quality metrics and reporting

### 📊 **Smart Search & Discovery**

- **AI-Powered Search**: Vector embeddings and semantic matching
- **Dataset Indexing**: Automatic indexing with metadata and quality metrics
- **Multi-Platform Search**: Kaggle, Google Dataset Search, Zenodo, DataCite integration
- **Relevance Ranking**: Similarity scoring and quality-based ranking

### ☁️ **Cloud Integration**

- **Multi-Provider Support**: AWS S3, Google Cloud Storage, Azure Blob Storage
- **Unified API**: Single interface for all cloud providers
- **Auto-Detection**: Automatic provider detection from URLs
- **Batch Operations**: Upload/download multiple files

### ⚙️ **Workflow Orchestration**

- **YAML-Based Pipelines**: Declarative workflow configuration
- **Conditional Branching**: Dynamic execution based on data conditions
- **Error Handling**: Robust error recovery and retry mechanisms
- **Async Execution**: Parallel workflow execution

### 🎯 **Active Learning & Sampling**

- **Intelligent Sampling**: Diversity, uncertainty, anomaly-based sampling
- **Stratified Sampling**: Maintain class/label distributions
- **Quality-Based Sampling**: Focus on data that improves quality
- **Active Learning**: Iterative model improvement through targeted sampling

### 🚀 **Distributed Processing**

- **Ray Integration**: Distributed computing with Ray
- **Dask Support**: Large dataset processing with Dask
- **Parallel Pipelines**: Concurrent data processing
- **Scalable Loading**: Memory-efficient large file processing

### 🧠 **ML Pipeline Integration**

- **AutoML**: Automated model selection and training
- **Feature Store**: Centralized feature management
- **ML Data Preparation**: One-click ML-ready data preparation
- **Model Evaluation**: Automated model performance assessment

### 🛠️ **Developer & User Tools**

- CLI tool (`openmlcrawler fetch ...`)
- Config-driven pipelines (YAML/JSON configs)
- Local caching system
- Rate-limit + retry handling
- Logging + progress bars
- Dataset search: `search_open_data("air quality")`

## Installation

```bash
# Install from PyPI
pip install openmlcrawler

# Or install from source
git clone https://github.com/krish567366/openmlcrawler.git
cd openmlcrawler
pip install -e .
```

## Quick Start

### Load Built-in Dataset

```python
from openmlcrawler import load_dataset

# Weather data
df = load_dataset("weather", location="Delhi", days=7)
print(df.head())

# Twitter data
df = load_dataset("twitter", query="machine learning", max_results=50)
print(df.head())

# Reddit data
df = load_dataset("reddit", subreddit="MachineLearning", limit=25)
print(df.head())

# US Government data
df = load_dataset("us_gov", query="climate change", limit=20)
print(df.head())
```

### Crawl Open Dataset

```python
from openmlcrawler import crawl_and_prepare

# Crawl CSV dataset
df = crawl_and_prepare(
    source="https://datahub.io/core/covid-19/countries.csv",
    type="csv",
    label_column="Country"
)
print(f"Loaded {len(df)} records")
```

### Search Open Data

```python
from openmlcrawler import search_open_data

# Search for datasets
results = search_open_data("climate change")
for result in results:
    print(f"{result['title']}: {result['url']}")
```

### ML-Ready Preparation

```python
from openmlcrawler import prepare_for_ml

# Prepare for ML
X, y, X_train, X_test, y_train, y_test = prepare_for_ml(
    df,
    target_column="Confirmed",
    test_size=0.2,
    normalize=True
)

print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
```

### Export Dataset

```python
from openmlcrawler import export_dataset

# Export to different formats
export_dataset(df, "data.csv", format="csv")
export_dataset(df, "data.json", format="json")
export_dataset(df, "data.parquet", format="parquet")
```

## Advanced Usage Examples

### Data Quality Assessment

```python
from openmlcrawler import assess_data_quality

# Assess data quality
quality_report = assess_data_quality(df)
print(f"Completeness: {quality_report['completeness_score']:.2f}")
print(f"Missing rate: {quality_report['missing_rate']:.2%}")
```

### Privacy & PII Detection

```python
from openmlcrawler import detect_pii, anonymize_data

# Detect PII
pii_report = detect_pii(df)
print("PII found in columns:", list(pii_report.keys()))

# Anonymize data
anonymized_df = anonymize_data(df, method='hash')
```

### Smart Dataset Search

```python
from openmlcrawler import SmartSearchEngine

# Index and search datasets
search_engine = SmartSearchEngine()
search_engine.index_dataset(df, "my_dataset")

# Search for similar datasets
results = search_engine.search_datasets("machine learning datasets")
for result in results:
    print(f"Found: {result['dataset_id']} (similarity: {result['similarity_score']:.3f})")
```

### Cloud Storage Integration

```python
from openmlcrawler import create_aws_connector, create_gcs_connector

# AWS S3
aws_conn = create_aws_connector(bucket_name="my-bucket")
url = aws_conn.upload_dataset(df, "my_dataset")

# Google Cloud Storage
gcs_conn = create_gcs_connector(bucket_name="my-bucket")
url = gcs_conn.upload_dataset(df, "my_dataset")
```

### Workflow Orchestration

```python
from openmlcrawler import execute_workflow_from_file

# Execute YAML workflow
result = execute_workflow_from_file("workflow.yaml", input_data=df)
print(f"Workflow status: {result['status']}")
```

### Intelligent Sampling

```python
from openmlcrawler import smart_sample_dataset

# Sample diverse data points
sampled_df = smart_sample_dataset(df, sample_size=1000, strategy='diversity')

# Uncertainty-based sampling for active learning
uncertainty_sample = smart_sample_dataset(
    df, sample_size=500, strategy='uncertainty', target_column='target'
)
```

### ML Pipeline Integration

```python
from openmlcrawler import prepare_dataset_for_ml, create_automl_pipeline

# Prepare data for ML
X_processed, y = prepare_dataset_for_ml(df, target_column='price')

# Run AutoML
automl = create_automl_pipeline()
results = automl.run_automl(X_processed, y)
print(f"Best model: {results['best_model'].__class__.__name__}")
```

### External Data Platform Integration

```python
from openmlcrawler import create_kaggle_connector, create_zenodo_connector

# Search Kaggle datasets
kaggle_conn = create_kaggle_connector()
results = kaggle_conn.search_datasets("machine learning")

# Search Zenodo research data
zenodo_conn = create_zenodo_connector()
results = zenodo_conn.search_datasets("climate data")
```

## CLI Usage

```bash
# Load weather data
openmlcrawler load weather --location "Delhi" --days 7 --output weather.csv

# Crawl dataset
openmlcrawler crawl https://example.com/data.csv --type csv --output data.csv

# Search datasets
openmlcrawler search "climate change" --max-results 5

# Export dataset
openmlcrawler export data.csv --format json --output data.json

# NEW: Assess data quality
openmlcrawler quality data.csv --format text

# NEW: Check data privacy
openmlcrawler privacy data.csv --action detect

# NEW: Generate EDA report
openmlcrawler report data.csv --output report.html

# NEW: Smart search datasets
openmlcrawler smart-search "machine learning datasets"

# NEW: Sample dataset
openmlcrawler sample data.csv --method diversity --size 1000 --output sample.csv

# NEW: Prepare data for ML
openmlcrawler ml prepare data.csv --target price --output ml_data.csv

# NEW: Run AutoML
openmlcrawler ml automl data.csv --target price --output results.json
```

## Configuration

Create a YAML configuration file for pipeline automation:

```yaml
# config/pipeline.yaml
datasets:
  - name: weather_delhi
    connector: weather
    params:
      location: "Delhi"
      days: 7
    output: "weather_delhi.csv"

  - name: covid_data
    source: "https://datahub.io/core/covid-19/countries.csv"
    type: csv
    cleaning:
      remove_duplicates: true
      handle_missing: "drop"
    output: "covid_clean.csv"
```

## Advanced Features

### Async Crawling

```python
import asyncio
from openmlcrawler.core.crawler import Crawler

async def crawl_multiple():
    crawler = Crawler()
    urls = ["url1", "url2", "url3"]

    tasks = [crawler.crawl_async(url) for url in urls]
    results = await asyncio.gather(*tasks)

    for result in results:
        print(f"Crawled {len(result)} characters")

asyncio.run(crawl_multiple())
```

### Custom Connectors

```python
# openmlcrawler/connectors/custom.py
def load_custom_dataset(api_key, **kwargs):
    # Your custom connector logic
    return pd.DataFrame()

# Use it
from openmlcrawler.connectors.custom import load_custom_dataset
df = load_custom_dataset(api_key="your_key")
```

### NLP Processing

```python
from openmlcrawler.core.nlp import TextProcessor, extract_text_features

processor = TextProcessor()

# Process text column
df = processor.process_text_column(df, "description", lowercase=True, remove_stopwords=True)

# Extract features
df_features = extract_text_features(df, "text_column")
```

### Real-time Data Monitoring

Monitor data streams with automated alerting, anomaly detection, and performance tracking.

```python
from openmlcrawler.core.monitoring import create_real_time_monitor, setup_email_alerts

# Create monitor
monitor = create_real_time_monitor()

# Configure email alerts
email_config = setup_email_alerts(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="your-email@gmail.com",
    password="your-password",
    from_email="your-email@gmail.com",
    to_emails=["admin@example.com"]
)
monitor.configure_alerts(email_config=email_config)

# Set feature columns for anomaly detection
monitor.set_feature_columns(['feature1', 'feature2', 'feature3'])

# Start monitoring
monitor.start_monitoring()

# Process data points
for data_point in data_stream:
    result = monitor.process_data_point(data_point)
    print(f"Processed: {result}")

# Get monitoring status
status = monitor.get_monitoring_status()
print(f"Active alerts: {status['active_alerts']}")

# Stop monitoring
monitor.stop_monitoring()

**CLI Usage:**
```bash
# Start monitoring with email alerts
openmlcrawler monitor start --features col1 col2 col3 \
  --email-smtp smtp.gmail.com --email-user user@gmail.com \
  --email-pass password --email-from user@gmail.com \
  --email-to admin@example.com

# Start with Slack alerts
openmlcrawler monitor start --slack-webhook https://hooks.slack.com/... \
  --features feature1 feature2

# Get status
openmlcrawler monitor status

# View recent alerts
openmlcrawler monitor alerts --hours 24
```

### Federated Learning

Enable distributed training across multiple datasets without centralizing data. Perfect for healthcare, finance, and multi-org collaborations with secure FedAvg aggregation.

```python
from openmlcrawler.core.federated import (
    create_federated_coordinator, create_federated_client,
    FederatedConfig, load_federated_config
)

# Create federated configuration
config = FederatedConfig(
    coordinator_host="localhost",
    coordinator_port=8080,
    num_rounds=10,
    min_clients=3,
    max_clients=5,
    secure_aggregation=True
)

# Create coordinator
coordinator = create_federated_coordinator(config)

# Register nodes (hospitals, clinics, etc.)
nodes_config = [
    {
        "node_id": "hospital_a",
        "host": "192.168.1.100",
        "port": 8081,
        "dataset_info": {
            "name": "patient_data_a",
            "size": 10000,
            "features": ["age", "blood_pressure", "cholesterol"],
            "target": "heart_disease"
        }
    }
]

for node_data in nodes_config:
    from openmlcrawler.core.federated import FederatedNode
    node = FederatedNode(**node_data)
    await coordinator.register_node(node)

# Start federated training
initial_model = {"weights": np.random.randn(10, 1), "bias": np.random.randn(1)}
await coordinator.start_federated_training(initial_model)

# Get training status
status = coordinator.get_training_status()
print(f"Round: {status['current_round']}/{status['total_rounds']}")

**CLI Usage:**
```bash
# Start federated learning
openmlcrawler federated start --nodes config/nodes.json \
  --model logistic_regression --rounds 10 --min-clients 3

# Get federated learning status
openmlcrawler federated status

# Stop federated learning
openmlcrawler federated stop
```

## Architecture

```txt
openmlcrawler/
├── __init__.py          # Main API with all advanced features
├── core/
│   ├── crawler.py       # Sync + async crawling
│   ├── parsers.py       # Data format parsers
│   ├── cleaners.py      # Data cleaning utilities
│   ├── schema.py        # Schema detection & ML prep
│   ├── exporter.py      # Export functions
│   ├── nlp.py          # NLP utilities
│   ├── utils.py        # Utilities & caching
│   ├── quality.py      # Data quality assessment
│   ├── privacy.py      # PII detection & anonymization
│   ├── reporting.py    # EDA reports & visualization
│   ├── search.py       # Smart search & discovery
│   ├── cloud.py        # Cloud storage integration
│   ├── workflow.py     # Workflow orchestration
│   ├── external.py     # External platform integration
│   ├── sampling.py     # Active learning & sampling
│   ├── distributed.py  # Distributed processing
│   └── ml_pipeline.py  # ML pipeline integration
├── connectors/          # Built-in connectors
│   ├── weather.py
│   ├── finance.py
│   └── ...
├── plugins/            # Community plugins
├── datasets/           # Local cache
├── cli.py             # Enhanced CLI with all commands
├── config/            # Pipeline configs
└── ...
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Krishna Bajpai**
- **Vedanshi Gupta**

## Acknowledgments

- Open data providers and API maintainers
- Python data science community
- Contributors and users

## Roadmap

### ✅ **Completed Features**

- [x] Plugin system for custom connectors
- [x] Advanced NLP features (translation, NER)
- [x] HuggingFace Datasets integration
- [x] Cloud storage integration (S3, GCS, Azure)
- [x] Data quality assessment and validation
- [x] Privacy & PII detection/anonymization
- [x] Smart search & discovery with AI
- [x] Workflow orchestration with YAML
- [x] Active learning & intelligent sampling
- [x] Distributed processing (Ray, Dask)
- [x] ML pipeline integration & AutoML
- [x] External platform integration (Kaggle, Zenodo, DataCite)
- [x] Enhanced CLI with all advanced commands
- [x] Comprehensive data visualization & reporting
- [x] Web UI for dataset exploration
- [x] Streaming data processing
- [x] Advanced ML model training pipelines
- [x] Real-time data monitoring
- [x] Social media connectors (Twitter/X, Reddit, Facebook)
- [x] Government portal connectors (US, EU, UK, India)
- [x] Federated learning support
- [x] More built-in connectors (social media, government portals)
- [x] Advanced time series analysis
- [x] Automated data lineage tracking
- [x] Integration with MLflow and other MLOps tools
- [x] Support for graph databases and knowledge graphs

 
