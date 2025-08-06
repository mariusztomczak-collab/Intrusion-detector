# 🔒 Security Analysis Pipeline

A sophisticated **three-stage pipeline** for cybersecurity incident analysis that combines document processing, machine learning classification, and LLM-powered decision making.

## 🎯 Overview

This pipeline transforms plain text security documents into actionable security intelligence through three distinct stages:

```
Documents → Entity Extraction → Classification → LLM Recommendations
    ↓              ↓                ↓                ↓
Plain Text    Structured Data   NORMAL/MALICIOUS   Actionable Steps
```

## 🏗️ Architecture

### Stage 1: Document Processing & Entity Extraction
- **Input**: Plain text documents (logs, reports, emails, etc.)
- **Output**: Structured security entities (IPs, domains, timestamps, actions, etc.)
- **Technology**: NLP/LLM for entity extraction with regex patterns

### Stage 2: Classification Agent
- **Input**: Extracted entities
- **Output**: NORMAL/MALICIOUS classification with confidence scores
- **Technology**: ML models with threat intelligence integration

### Stage 3: LLM Decision Maker
- **Input**: Classification result + extracted entities
- **Output**: Detailed analysis and actionable recommendations
- **Technology**: LLM for security recommendations

## 🚀 Quick Start

### Installation

```bash
# Install core dependencies
pip install -r requirements_pipeline.txt

# Install spaCy model (optional but recommended)
python -m spacy download en_core_web_sm
```

### Basic Usage

```python
from src.core.security_pipeline import SecurityAnalysisPipeline

# Initialize pipeline
pipeline = SecurityAnalysisPipeline(
    llm_api_key="your-openai-key",  # Optional
    output_dir="analysis_output"
)

# Analyze a single document
result = pipeline.analyze_document("security_log.txt")

# Get results
print(f"Risk Score: {result.classification_result.risk_score}")
print(f"Is Malicious: {result.classification_result.is_malicious}")
print(f"Recommendations: {result.security_analysis.detailed_recommendations}")
```

### Demo

```bash
# Run full demo
python demo_pipeline.py

# Run quick demo
python demo_pipeline.py quick
```

## 📋 Features

### 🔍 Entity Extraction
- **IP Addresses**: IPv4 and IPv6 detection
- **Domains**: Malicious domain identification
- **Emails**: Email address extraction
- **Timestamps**: Various timestamp formats
- **URLs**: Web link detection
- **File Paths**: System file access patterns
- **Hashes**: MD5, SHA1, SHA256 detection
- **Security Keywords**: Threat-specific terminology

### 🎯 Classification
- **Rule-based**: Threat intelligence integration
- **ML-powered**: Random Forest classification
- **Confidence Scoring**: Probability-based decisions
- **Threat Detection**: Known malicious indicators

### 🤖 LLM Analysis
- **Contextual Analysis**: Deep security insights
- **Actionable Recommendations**: Specific next steps
- **Incident Response**: Immediate and follow-up actions
- **Risk Mitigation**: Long-term security strategies

## 📊 Output Structure

Each analysis produces comprehensive results:

```json
{
  "pipeline_id": "pipeline_20240115_143022",
  "document_analysis": {
    "document_name": "security_log.txt",
    "entities": [...],
    "risk_score": 0.75
  },
  "classification_result": {
    "is_malicious": true,
    "confidence": 0.89,
    "detected_threats": [...],
    "recommended_actions": [...]
  },
  "security_analysis": {
    "llm_analysis": "Detailed security analysis...",
    "detailed_recommendations": [...],
    "incident_response_steps": [...],
    "risk_mitigation_strategies": [...]
  }
}
```

## 🔧 Configuration

### Pipeline Configuration

```python
pipeline = SecurityAnalysisPipeline(
    llm_api_key="your-key",           # OpenAI API key (optional)
    classification_model_path="model.pkl",  # Pre-trained model (optional)
    output_dir="output"               # Output directory
)
```

### Customization Options

```python
# Update threat intelligence
pipeline.update_threat_intelligence({
    'high_risk_ips': {'192.168.1.100', '10.0.0.50'},
    'malicious_domains': {'malware.example.com'},
    'suspicious_keywords': {'exploit', 'backdoor'}
})

# Train custom classification model
training_data = [
    (entities_list_1, True),   # Malicious
    (entities_list_2, False),  # Normal
    # ... more training examples
]
pipeline.train_classification_model(training_data)
```

## 📁 File Structure

```
src/
├── core/
│   ├── __init__.py
│   ├── document_processor.py      # Stage 1: Entity extraction
│   ├── classification_agent.py    # Stage 2: ML classification
│   ├── llm_decision_maker.py      # Stage 3: LLM analysis
│   └── security_pipeline.py       # Main orchestrator
├── __init__.py
demo_pipeline.py                   # Demo script
requirements_pipeline.txt          # Dependencies
PIPELINE_README.md                 # This file
```

## 🎯 Use Cases

### 1. Security Log Analysis
```python
# Analyze firewall logs
results = pipeline.analyze_documents_batch([
    "firewall_logs.txt",
    "access_logs.txt",
    "error_logs.txt"
])
```

### 2. Incident Response
```python
# Quick analysis for immediate response
quick_result = pipeline.run_quick_analysis("incident_report.txt")
if quick_result['is_malicious']:
    print("🚨 IMMEDIATE ACTION REQUIRED")
```

### 3. Threat Intelligence
```python
# Extract entities for threat feeds
pipeline.export_entities_batch(
    document_paths=["threat_reports/*.txt"],
    output_path="threat_intelligence.json"
)
```

### 4. Compliance Reporting
```python
# Generate comprehensive reports
pipeline.generate_pipeline_report(
    results=analysis_results,
    output_path="compliance_report.json"
)
```

## 🔒 Security Considerations

### Data Privacy
- All processing is local by default
- LLM calls are optional and configurable
- No data is sent to external services unless explicitly configured

### Threat Intelligence
- Built-in threat indicators
- Configurable threat feeds
- Regular updates recommended

### Model Security
- Models can be trained on your data
- No external model dependencies
- Custom threat intelligence integration

## 🚀 Performance

### Processing Speed
- **Single Document**: ~1-3 seconds
- **Batch Processing**: ~10-30 documents/minute
- **Entity Extraction**: Real-time
- **Classification**: <1 second
- **LLM Analysis**: 2-5 seconds (if enabled)

### Scalability
- **Memory Efficient**: Processes documents one at a time
- **Batch Processing**: Handles multiple documents
- **Parallel Processing**: Can be extended for concurrent analysis
- **Resource Usage**: Minimal CPU/memory footprint

## 🔧 Advanced Usage

### Custom Entity Extraction

```python
from src.core.document_processor import DocumentProcessor

processor = DocumentProcessor()
processor.load_nlp_model("en_core_web_sm")

# Add custom patterns
processor.entity_patterns['custom_pattern'] = r'your-regex-pattern'

# Extract entities
entities = processor.extract_entities_from_text("your text here")
```

### Custom Classification

```python
from src.core.classification_agent import ClassificationAgent

agent = ClassificationAgent()

# Add custom threat indicators
agent.update_threat_intelligence({
    'custom_indicators': {'indicator1', 'indicator2'}
})

# Train on your data
agent.train_model(your_training_data)
```

### Custom LLM Integration

```python
from src.core.llm_decision_maker import LLMDecisionMaker

# Use different LLM providers
llm = LLMDecisionMaker(
    api_key="your-key",
    model="gpt-4"  # or other models
)

# Custom analysis templates
llm.analysis_templates['custom'] = "Your custom template..."
```

## 📈 Monitoring & Logging

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Pipeline Status

```python
status = pipeline.get_pipeline_status()
print(json.dumps(status, indent=2))
```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd security-pipeline

# Install dependencies
pip install -r requirements_pipeline.txt

# Install development dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Adding New Features

1. **Entity Types**: Add patterns to `DocumentProcessor`
2. **Classification Rules**: Extend `ClassificationAgent`
3. **LLM Templates**: Customize `LLMDecisionMaker`
4. **Pipeline Stages**: Extend `SecurityAnalysisPipeline`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

1. **spaCy Model Not Found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **LLM API Errors**
   - Check API key configuration
   - Verify API quota and limits
   - Use fallback mode if needed

3. **Memory Issues**
   - Process documents in smaller batches
   - Reduce batch size in configuration

### Getting Help

- Check the demo scripts for examples
- Review the source code documentation
- Open an issue for bugs or feature requests

---

**🎉 Ready to analyze your security documents with AI-powered intelligence!** 