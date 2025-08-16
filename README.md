# AutoGRADE 🎯

**Automated GRADE Evidence Assessment Platform**

A comprehensive Django-based web application implementing the Core GRADE methodology (BMJ 2025 series) for systematic reviews and evidence-based guideline development.

[![Django](https://img.shields.io/badge/Django-4.2.8-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GRADE](https://img.shields.io/badge/GRADE-Core%20Methodology-red.svg)](https://www.bmj.com/content/384/bmj-2024-080576)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Core GRADE Implementation](#core-grade-implementation)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## 🎯 Overview

AutoGRADE is a state-of-the-art platform designed to streamline the GRADE (Grading of Recommendations, Assessment, Development and Evaluations) process for systematic reviewers, guideline developers, and evidence synthesis teams. Built following the latest Core GRADE methodology from the BMJ 2025 series, it provides comprehensive support for rigorous evidence assessment and recommendation development.

### Key Benefits

- **🔬 Methodological Rigor**: Implements the latest Core GRADE guidance (BMJ 2025)
- **⚡ Streamlined Workflows**: Guided assessments with contextual help
- **📊 Comprehensive Analysis**: Support for all GRADE domains and assessment types
- **🔄 Transparent Process**: Complete audit trail and rationale documentation
- **👥 Team Collaboration**: Multi-user support with role-based permissions
- **📱 Modern Interface**: Responsive design with progressive disclosure

---

## ✨ Features

### Core Functionality
- **Project Management**: Organize systematic reviews and guideline projects
- **PICO Framework**: Structured population, intervention, comparator, outcome definition
- **Evidence Integration**: Upload and process manuscripts, studies, and data
- **GRADE Assessment**: Complete implementation of all GRADE domains
- **Summary of Findings**: Generate publication-ready evidence summaries
- **Evidence-to-Decision**: Structured recommendation development process

### Advanced Capabilities
- **Multiple RoB Tools**: Support for RoB 2, ROBUST-RCT, ROBINS-I, Newcastle-Ottawa
- **Forest Plot Analysis**: Upload and analyze forest plots with I² interpretation
- **Risk Stratification**: Multiple baseline risk groups for clinical decision making
- **Subgroup Analysis**: ICEMAN-based credibility assessment framework
- **Publication Bias Detection**: Funnel plot analysis with statistical tests
- **Automated Calculations**: OIS, absolute effects, and confidence interval analysis

### 🤖 AI-Powered GRADE Assessment (Claude Sonnet 4)
- **🎯 AI Risk of Bias Analysis**: Automated RoB assessment from study manuscripts
- **📑 AI PICO Extraction**: Intelligent extraction of population, intervention, comparator, outcomes
- **✨ AI Summary Generation**: Automated Summary of Findings table creation
- **🧠 AI Recommendation Assistance**: Evidence-to-decision framework guidance
- **📊 Intelligent Data Processing**: Claude Sonnet 4 for nuanced evidence interpretation
- **🔍 Smart Document Analysis**: PDF/DOCX manuscript processing with AI insights

---

## 🧬 Core GRADE Implementation

AutoGRADE implements all seven Core GRADE articles from the BMJ 2025 series:

### 📚 Core GRADE Articles Implemented

| Article | Focus | Implementation |
|---------|-------|-----------------|
| **Core GRADE 1** | Framework Overview | Complete GRADE workflow integration |
| **Core GRADE 2** | Imprecision Assessment | MID vs null threshold analysis, OIS calculations |
| **Core GRADE 3** | Inconsistency Assessment | I² analysis, subgroup credibility (ICEMAN) |
| **Core GRADE 4** | Risk of Bias & Publication Bias | Multiple RoB tools, funnel plot analysis |
| **Core GRADE 5** | Indirectness Assessment | PICO mismatch detection, surrogate outcomes |
| **Core GRADE 6** | Summary of Findings | Risk-stratified presentations, multiple outcome formats |
| **Core GRADE 7** | Evidence-to-Decision | Complete EtD framework with MID and values integration |

### 🔧 Assessment Domains

1. **Risk of Bias Assessment**
   - Binary low/high classification
   - Multiple tool support (RoB 2, ROBUST-RCT, ROBINS-I, Newcastle-Ottawa)
   - CSV bulk upload capability
   - Direction of bias consideration

2. **Imprecision Assessment**
   - MID vs null threshold selection
   - Confidence interval crossing analysis
   - Optimal Information Size (OIS) calculations
   - Structured rating guidance

3. **Inconsistency Assessment**
   - Forest plot file upload and analysis
   - I² statistic interpretation
   - Visual inspection prioritization
   - ICEMAN subgroup credibility assessment

4. **Indirectness Assessment**
   - Target vs study PICO comparison
   - Population/intervention/comparator/outcome mismatch detection
   - Surrogate outcome relationship evaluation
   - Severity-based rating structure

5. **Publication Bias Assessment**
   - Funnel plot upload and analysis
   - Statistical test integration (Egger's, Begg's)
   - Industry sponsorship evaluation
   - Search strategy documentation

---

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment support
- Git

### Local Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/choxos/AutoGRADE.git
   cd AutoGRADE
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **🤖 Enable AI-Powered GRADE (Claude Sonnet 4)**
   ```bash
   # Get your API key from https://console.anthropic.com/
   # Add to your .env file:
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-api-key-here
   
   # Optional: Configure AI features (all enabled by default)
   AI_RISK_OF_BIAS_ANALYSIS=True
   AI_PICO_EXTRACTION=True
   AI_SUMMARY_GENERATION=True
   AI_RECOMMENDATION_ASSISTANCE=True
   ```

6. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

6. **Create Superuser**
   
   **Option A: Default Development Superuser (Quick Setup)**
   ```bash
   python manage.py setup_default_superuser
   ```
   
   **Default Credentials:**
   - Username: `choxos`
   - Email: `ahmad.pub@gmail.com`
   - Password: `!*)@&)`
   
   ⚠️ **Security Warning**: These are default development credentials. Change them immediately in production!
   
   **Option B: Custom Superuser (Recommended for Production)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the application.

### Railway Deployment

1. **Deploy to Railway**
   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/django)

2. **Add PostgreSQL Database**
   ```bash
   # Railway automatically provides DATABASE_URL
   # No manual database configuration needed
   ```

3. **Set Environment Variables**
   ```bash
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-railway-domain.railway.app
   ```

4. **Railway automatically handles**:
   - Port configuration (uses $PORT)
   - PostgreSQL DATABASE_URL
   - Static file serving with WhiteNoise
   - Automatic migrations and collectstatic

---

## 🏃‍♂️ Quick Start

### 1. Create Your First Project
```bash
# Access the web interface at http://127.0.0.1:8000
# Login with your superuser credentials
# Navigate to "Create New Project"
```

### 2. Define Your Research Question
- **Population**: Define target population characteristics
- **Intervention**: Specify intervention details
- **Comparator**: Define comparison intervention
- **Outcomes**: List primary and secondary outcomes

### 3. Upload Evidence
- Import studies via CSV upload
- Upload individual study manuscripts
- Configure risk of bias assessments

### 4. Conduct GRADE Assessment
- Risk of Bias: Select tool and assess domains
- Imprecision: Set MID thresholds and analyze CIs
- Inconsistency: Upload forest plots and assess I²
- Indirectness: Compare target vs study PICO
- Publication Bias: Analyze funnel plots and tests

### 5. Generate Summary of Findings
- Configure risk groups and baseline risks
- Select outcome presentation formats
- Generate publication-ready tables

### 6. Evidence-to-Decision Framework
- Specify minimal important differences
- Assess values and preferences
- Evaluate benefits, harms, and secondary considerations
- Formulate recommendations

---

## 📁 Project Structure

```
AutoGRADE/
├── autograde/                 # Django project settings
│   ├── settings.py           # Main configuration
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── grade/                    # Main Django application
│   ├── models.py            # Database models
│   ├── views.py             # View controllers
│   ├── forms.py             # Form definitions
│   ├── admin.py             # Admin interface
│   ├── urls.py              # App URL patterns
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   └── utils/               # Utility modules
│       ├── grade_engine.py  # Core GRADE logic
│       ├── pico_extractor.py # PICO processing
│       ├── manuscript_processor.py # Document processing
│       └── sof_generator.py # Summary of Findings generation
├── requirements.txt         # Python dependencies
├── manage.py               # Django management
├── .gitignore             # Git ignore rules
├── .env.example           # Environment template
└── README.md              # This file
```

---

## 📖 Usage Guide

### Project Management

Create and manage systematic review projects with comprehensive metadata:

```python
# Example project creation
project = GRADEProject.objects.create(
    title="Effectiveness of Intervention X for Condition Y",
    description="Systematic review examining...",
    review_question="What is the effectiveness of...",
    protocol_url="https://prospero.link/...",
    target_population="Adults with condition Y",
    target_intervention="Intervention X",
    target_comparator="Standard care",
    target_outcomes=["Primary outcome", "Secondary outcome"]
)
```

### GRADE Assessment Workflow

1. **Risk of Bias Assessment**
   ```python
   rob_assessment = RiskOfBiasAssessment.objects.create(
       project=project,
       tool_used='rob_2',
       domain_assessments={
           'randomization': 'low',
           'deviation_interventions': 'some_concerns',
           'missing_outcome_data': 'low',
           'measurement_outcome': 'low',
           'selection_reported_result': 'high'
       },
       overall_classification='high'
   )
   ```

2. **Imprecision Assessment**
   ```python
   imprecision = ImprecisionAssessment.objects.create(
       outcome=outcome,
       mid_threshold=0.5,
       null_threshold=0.0,
       confidence_interval_lower=-0.2,
       confidence_interval_upper=1.2,
       crosses_mid_threshold=True,
       crosses_null_threshold=False,
       optimal_information_size=2000,
       total_sample_size=1500,
       rating='down_once'
   )
   ```

### Advanced Features

#### Subgroup Analysis with ICEMAN Framework
```python
subgroup = SubgroupAnalysis.objects.create(
    inconsistency_assessment=inconsistency,
    subgroup_hypothesis="Age-based subgroup effect",
    a_priori_specified=True,
    iceman_criteria={
        'independent': True,
        'credible': True,
        'early_stopped': False,
        'multiple_testing': False,
        'appropriate': True,
        'no_heterogeneity': False
    },
    credibility_rating='highly_credible'
)
```

#### Publication Bias Assessment
```python
pub_bias = PublicationBiasAssessment.objects.create(
    outcome=outcome,
    funnel_plot_file="path/to/funnel_plot.png",
    visual_asymmetry=True,
    eggers_test_p_value=0.03,
    beggs_test_p_value=0.08,
    small_study_effects=True,
    industry_sponsorship_present=True,
    rating='down_once'
)
```

---

## 🔌 API Documentation

AutoGRADE provides a RESTful API for programmatic access:

### Authentication
```bash
# Token-based authentication
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/projects/
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/` | GET, POST | List/create projects |
| `/api/projects/{id}/` | GET, PUT, DELETE | Project details |
| `/api/outcomes/` | GET, POST | Manage outcomes |
| `/api/assessments/rob/` | GET, POST | Risk of bias assessments |
| `/api/assessments/imprecision/` | GET, POST | Imprecision assessments |
| `/api/sof/generate/` | POST | Generate Summary of Findings |

### Example API Usage
```python
import requests

# Create a new project
response = requests.post('http://localhost:8000/api/projects/', {
    'title': 'New Systematic Review',
    'description': 'Description here',
    'review_question': 'Research question'
}, headers={'Authorization': 'Token YOUR_TOKEN'})

project_id = response.json()['id']
```

---

## 🤝 Contributing

We welcome contributions to AutoGRADE! Please see our contributing guidelines:

### Development Process

1. **Fork the Repository**
   ```bash
   git fork https://github.com/choxos/AutoGRADE.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow Django best practices
   - Add tests for new functionality
   - Update documentation as needed

4. **Run Tests**
   ```bash
   python manage.py test
   ```

5. **Submit Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure CI passes

### Code Standards

- **Style**: Follow PEP 8 and Django coding standards
- **Documentation**: Document all new functions and classes
- **Tests**: Maintain >90% test coverage
- **Commits**: Use conventional commit messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Open Source Libraries

AutoGRADE builds upon several excellent open source libraries:

- **Django**: Web framework
- **Bootstrap**: UI framework
- **Chart.js**: Data visualization
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Pillow**: Image processing

---

## 🆘 Support

### Documentation
- [Core GRADE Guidelines](https://www.bmj.com/content/384/bmj-2024-080576)
- [Django Documentation](https://docs.djangoproject.com/)
- [GRADE Working Group](https://www.gradeworkinggroup.org/)

### Community
- [GitHub Issues](https://github.com/choxos/AutoGRADE/issues)
- [Discussions](https://github.com/choxos/AutoGRADE/discussions)
- [Wiki](https://github.com/choxos/AutoGRADE/wiki)

### Professional Support
For institutional deployments, training, and custom development:
- Email: support@autograde.org
- Website: https://autograde.org

---

## 🙏 Acknowledgments

- **GRADE Working Group** for developing the GRADE methodology
- **BMJ** for publishing the Core GRADE series
- **Cochrane Collaboration** for evidence synthesis guidance
- **Django Community** for the excellent web framework
- **Contributors** who have helped improve AutoGRADE

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/choxos/AutoGRADE)
![GitHub forks](https://img.shields.io/github/forks/choxos/AutoGRADE)
![GitHub issues](https://img.shields.io/github/issues/choxos/AutoGRADE)
![GitHub last commit](https://img.shields.io/github/last-commit/choxos/AutoGRADE)

---

**AutoGRADE** - *Advancing Evidence-Based Medicine Through Rigorous GRADE Assessment*

Made with ❤️ for the global evidence synthesis community
