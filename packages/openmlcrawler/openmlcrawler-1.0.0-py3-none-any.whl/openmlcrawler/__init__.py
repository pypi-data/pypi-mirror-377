"""
OpenML Crawler - A unified framework for crawling and preparing ML-ready datasets.

This package provides tools to:
- Crawl open web datasets (CSV, JSON, XML, HTML, PDF, APIs)
- Connect to free/public APIs (weather, finance, Wikipedia, news, etc.)
- Clean, structure, and export ML-ready datasets
- CLI and config-driven pipelines
- Async crawling, caching, and metadata tracking
- Advanced features: data quality, privacy, visualization, smart search, cloud integration
"""

__version__ = "0.1.0"
__authors__ = ["Krishna Bajpai", "Vedanshi Gupta"]

# Core functionality
from .core.crawler import crawl_and_prepare
from .core.exporter import export_dataset
from .core.schema import prepare_for_ml
from .connectors.weather import load_weather_dataset
from .connectors.social_media import (
    load_twitter_dataset, load_reddit_dataset, load_facebook_dataset,
    TwitterConnector, RedditConnector, FacebookConnector
)
from .connectors.government import (
    load_us_gov_dataset, load_eu_gov_dataset, load_uk_gov_dataset, load_india_gov_dataset,
    USGovernmentConnector, EUOpenDataConnector, UKGovernmentConnector, IndianGovernmentConnector
)
from .core.utils import search_open_data

# Advanced modules
from .core.quality import assess_data_quality, validate_dataset_schema, check_data_quality
from .core.privacy import detect_pii, anonymize_data, check_compliance
from .core.reporting import generate_eda_report, generate_schema_diagram, generate_cli_report
from .core.search import smart_search_datasets, SmartSearchEngine
from .core.cloud import (
    create_aws_connector, create_gcs_connector, create_azure_connector,
    create_cloud_manager, AWSConnector, GCSConnector, AzureConnector
)
from .core.workflow import execute_workflow_from_file, execute_workflow_from_config, WorkflowEngine
try:
    from .core.external import (
        create_kaggle_connector, create_google_dataset_connector,
        create_zenodo_connector, create_datacite_connector, create_external_data_manager
    )
except ImportError:
    # External connectors may fail due to missing optional dependencies
    create_kaggle_connector = None
    create_google_dataset_connector = None
    create_zenodo_connector = None
    create_datacite_connector = None
    create_external_data_manager = None
from .core.sampling import (
    smart_sample_dataset, create_intelligent_sampler, create_active_learning_manager
)
from .core.distributed import (
    create_distributed_crawler, create_distributed_processor,
    create_parallel_pipeline, create_scalable_loader
)
from .core.ml_pipeline import (
    prepare_dataset_for_ml, create_ml_preparator, create_automl_pipeline,
    create_feature_store, create_ml_pipeline_manager
)

# Web UI
from .core.web import launch_web_ui, DatasetExplorer

# Streaming data processing
from .core.streaming import (
    StreamingDataProcessor, StreamingDataSource, HTTPStreamingSource,
    WebSocketStreamingSource, FileStreamingSource, StreamingPipeline,
    StreamingWebServer, create_http_streaming_source, create_websocket_streaming_source,
    create_file_streaming_source, create_streaming_pipeline
)

# Advanced ML training
from .core.ml_training import (
    ModelTrainingPipeline, AutoMLPipeline, create_model_training_pipeline,
    create_automl_pipeline, compare_models
)

# Real-time monitoring
from .core.monitoring import (
    RealTimeMonitor, AlertManager, AnomalyDetector, PerformanceMonitor,
    create_real_time_monitor, setup_email_alerts, setup_slack_alerts,
    setup_webhook_alerts, AlertLevel, AlertChannel
)

# Federated learning
from .core.federated import (
    FederatedCoordinator, FederatedClient, SecureAggregator,
    FederatedConfig, FederatedNode, ModelUpdate,
    create_federated_coordinator, create_federated_client,
    load_federated_config
)

# Self-healing pipelines
from .core.self_healing import (
    SelfHealingPipeline, ExponentialBackoffRetry, FallbackDataSourceManager,
    AdaptiveAnomalyDetector, SelfHealingConfig, RetryConfig, FallbackConfig,
    AdaptiveThresholdConfig, create_self_healing_pipeline,
    create_default_self_healing_config, load_self_healing_config,
    with_self_healing
)

def load_dataset(connector_name, **kwargs):
    """
    Load dataset from built-in connectors.

    Args:
        connector_name (str): Name of the connector (e.g., 'weather', 'twitter', 'us_gov')
        **kwargs: Connector-specific parameters

    Returns:
        pd.DataFrame: Loaded dataset
    """
    if connector_name == "weather":
        return load_weather_dataset(**kwargs)
    elif connector_name == "twitter":
        return load_twitter_dataset(**kwargs)
    elif connector_name == "reddit":
        return load_reddit_dataset(**kwargs)
    elif connector_name == "facebook":
        return load_facebook_dataset(**kwargs)
    elif connector_name == "us_gov":
        return load_us_gov_dataset(**kwargs)
    elif connector_name == "eu_gov":
        return load_eu_gov_dataset(**kwargs)
    elif connector_name == "uk_gov":
        return load_uk_gov_dataset(**kwargs)
    elif connector_name == "india_gov":
        return load_india_gov_dataset(**kwargs)
    else:
        raise ValueError(f"Unknown connector: {connector_name}")

__all__ = [
    # Core functions
    "load_dataset",
    "crawl_and_prepare",
    "export_dataset",
    "prepare_for_ml",
    "search_open_data",

    # Social media connectors
    "load_twitter_dataset",
    "load_reddit_dataset",
    "load_facebook_dataset",
    "TwitterConnector",
    "RedditConnector",
    "FacebookConnector",

    # Government data connectors
    "load_us_gov_dataset",
    "load_eu_gov_dataset",
    "load_uk_gov_dataset",
    "load_india_gov_dataset",
    "USGovernmentConnector",
    "EUOpenDataConnector",
    "UKGovernmentConnector",
    "IndianGovernmentConnector",

    # Data quality and validation
    "assess_data_quality",
    "validate_dataset_schema",
    "check_data_quality",

    # Privacy and security
    "detect_pii",
    "anonymize_data",
    "check_compliance",

    # Reporting and visualization
    "generate_eda_report",
    "generate_schema_diagram",
    "generate_cli_report",

    # Smart search
    "smart_search_datasets",
    "SmartSearchEngine",

    # Cloud integration
    "create_aws_connector",
    "create_gcs_connector",
    "create_azure_connector",
    "create_cloud_manager",
    "AWSConnector",
    "GCSConnector",
    "AzureConnector",

    # Workflow orchestration
    "execute_workflow_from_file",
    "execute_workflow_from_config",
    "WorkflowEngine",

    # External data platforms
    "create_kaggle_connector",
    "create_google_dataset_connector",
    "create_zenodo_connector",
    "create_datacite_connector",
    "create_external_data_manager",

    # Active learning and sampling
    "smart_sample_dataset",
    "create_intelligent_sampler",
    "create_active_learning_manager",

    # Distributed processing
    "create_distributed_crawler",
    "create_distributed_processor",
    "create_parallel_pipeline",
    "create_scalable_loader",

    # ML pipeline integration
    "prepare_dataset_for_ml",
    "create_ml_preparator",
    "create_automl_pipeline",
    "create_feature_store",
    "create_ml_pipeline_manager",

    # Web UI
    "launch_web_ui",
    "DatasetExplorer",

    # Streaming data processing
    "StreamingDataProcessor",
    "StreamingDataSource",
    "HTTPStreamingSource",
    "WebSocketStreamingSource",
    "FileStreamingSource",
    "StreamingPipeline",
    "StreamingWebServer",
    "create_http_streaming_source",
    "create_websocket_streaming_source",
    "create_file_streaming_source",
    "create_streaming_pipeline",

    # Advanced ML training
    "ModelTrainingPipeline",
    "AutoMLPipeline",
    "create_model_training_pipeline",
    "create_automl_pipeline",
    "compare_models",

    # Real-time monitoring
    "RealTimeMonitor",
    "AlertManager",
    "AnomalyDetector",
    "PerformanceMonitor",
    "create_real_time_monitor",
    "setup_email_alerts",
    "setup_slack_alerts",
    "setup_webhook_alerts",
    "AlertLevel",
    "AlertChannel",

    # Federated learning
    "FederatedCoordinator",
    "FederatedClient",
    "SecureAggregator",
    "FederatedConfig",
    "FederatedNode",
    "ModelUpdate",
    "create_federated_coordinator",
    "create_federated_client",
    "load_federated_config",

    # Self-healing pipelines
    "SelfHealingPipeline",
    "ExponentialBackoffRetry",
    "FallbackDataSourceManager",
    "AdaptiveAnomalyDetector",
    "SelfHealingConfig",
    "RetryConfig",
    "FallbackConfig",
    "AdaptiveThresholdConfig",
    "create_self_healing_pipeline",
    "create_default_self_healing_config",
    "load_self_healing_config",
    "with_self_healing"
]