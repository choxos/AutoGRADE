# AutoGRADE Core GRADE Enhancements

## Overview

AutoGRADE has been significantly enhanced to support the detailed Core GRADE methodology as outlined in the BMJ 2025 Core GRADE series (Articles 1-7). This implementation provides comprehensive support for systematic reviewers and guideline developers to conduct rigorous GRADE assessments following the latest evidence-based methodological guidance.

## Core GRADE Series Implementation

This implementation is based on the comprehensive BMJ 2025 Core GRADE series:

1. **Core GRADE 1**: Overview of the Core GRADE approach
2. **Core GRADE 2**: Choosing the target of certainty rating and assessing imprecision  
3. **Core GRADE 3**: Rating certainty of evidence—assessing inconsistency
4. **Core GRADE 4**: Rating certainty of evidence—risk of bias, publication bias, and reasons for rating up certainty
5. **Core GRADE 5**: Rating certainty of evidence—assessing indirectness
6. **Core GRADE 6**: Presenting the evidence in summary of findings tables
7. **Core GRADE 7**: Principles for moving from evidence to recommendations and decisions

## Enhanced Features

### 1. Risk of Bias Assessment (Core GRADE 4)

**New Models:**
- `RiskOfBiasAssessment`: Individual study RoB assessments with support for multiple tools

**Key Features:**
- Support for Core GRADE recommended tools:
  - RoB 2 (Cochrane)
  - ROBUST-RCT (simplified, rigorous)
  - ROBINS-I (for NRSI)
  - Newcastle-Ottawa Scale
  - CLARITY tools (cohort and case-control)
- Binary classification: Low/High risk of bias (following Core GRADE simplification)
- Statistical weighting integration for determining if high RoB studies dominate
- CSV data upload capability for bulk RoB assessment import
- Flexible domain assessment storage (JSON) to accommodate different tools
- Automated analysis of whether high RoB studies carry >65% or ≥55% weight

**Core GRADE Principles Implemented:**
- Simplified binary RoB classification instead of complex multi-level systems
- Weight-based decision making for rating down
- Direction of bias consideration to avoid unnecessary rating down
- Separate evidence summaries when low and high RoB studies show substantial differences

### 2. Imprecision Assessment (Core GRADE 2)

**New Models:**
- `ImprecisionAssessment`: Enhanced imprecision evaluation with MID vs null threshold support

**Key Features:**
- **Target Selection**: Choose between MID threshold or null effect threshold
- **CI Analysis**: Automated analysis of confidence interval crossing patterns
- **OIS Consideration**: Optimal Information Size calculations and criterion assessment
- **Structured Rating**: Clear guidance for rating down once vs twice
- **Threshold Crossing**: Detailed analysis of CI relationships to thresholds

**Core GRADE Principles Implemented:**
- MID-focused imprecision assessment (preferred approach)
- Systematic analysis of CI boundaries relative to decision thresholds
- Integration of sample size adequacy (OIS) considerations
- Clear rationale requirement for imprecision decisions

### 3. Inconsistency Assessment (Core GRADE 3)

**New Models:**
- `InconsistencyAssessment`: Comprehensive inconsistency evaluation
- `SubgroupAnalysis`: Credibility assessment framework for subgroup effects

**Key Features:**
- **Forest Plot Integration**: Upload and analysis of forest plot visualizations
- **I² Statistic**: Proper interpretation with Core GRADE caveats
- **Visual Inspection**: Systematic criteria for forest plot assessment
- **Subgroup Hypotheses**: A priori hypothesis specification and testing
- **Credibility Assessment**: ICEMAN-based credibility evaluation for subgroup effects

**Core GRADE Principles Implemented:**
- Visual inspection prioritized over statistical tests alone
- A priori subgroup hypothesis requirement
- Credibility assessment using established criteria:
  - Prespecified hypotheses
  - Within-study comparisons preferred
  - Interaction test p-values
  - Biological plausibility
  - Direction consistency
- Separate evidence summaries for credible subgroups

### 4. Indirectness Assessment (Core GRADE 5)

**New Models:**
- `IndirectnessAssessment`: Comprehensive PICO indirectness evaluation

**Key Features:**
- **Target PICO Definition**: Clear specification of target population, intervention, comparator, outcome
- **PICO Mismatch Detection**: Systematic evaluation of differences in each PICO element
- **Surrogate Outcome Handling**: Specialized assessment for surrogate endpoints
- **Indirectness Severity**: Rating down once vs twice based on relationship strength

**Core GRADE Principles Implemented:**
- Distinction between indirect comparisons and PICO-related indirectness
- Population indirectness: Age, comorbidity, disease stage differences
- Intervention indirectness: Dose, duration, adherence, technology evolution
- Comparator indirectness: Suboptimal controls, placebo vs active comparisons
- Outcome indirectness: Surrogate vs patient-important outcomes, timing differences
- Two-level rating down for very indirect surrogate outcomes

### 5. Publication Bias Assessment (Core GRADE 4)

**New Models:**
- `PublicationBiasAssessment`: Comprehensive publication bias evaluation

**Key Features:**
- **Funnel Plot Analysis**: Upload and systematic visual assessment
- **Statistical Tests**: Integration of Egger's and Begg's tests
- **Industry Sponsorship**: Detection of industry-funded small studies
- **Comprehensive Search**: Documentation of search strategy completeness
- **Unpublished Studies**: Documentation of known unpublished research

**Core GRADE Principles Implemented:**
- Funnel plot asymmetry assessment with alternative explanations
- Small study + industry sponsorship = high suspicion threshold
- Statistical test integration (≥10 studies required)
- Search comprehensiveness documentation
- "Undetected" vs "strongly suspected" terminology

### 6. Enhanced Summary of Findings (Core GRADE 6)

**New Models:**
- `EnhancedSummaryOfFindings`: Advanced SoF table with risk stratification
- `RiskGroup`: Multiple baseline risk groups for absolute effect calculation
- `ContinuousOutcomePresentation`: Multiple presentation options for continuous outcomes

**Key Features:**
- **Risk Stratification**: Support for multiple risk groups with different baseline risks
- **Absolute Effect Calculation**: Automated calculation across risk groups
- **Continuous Outcome Options**: Multiple presentation formats:
  - Mean difference (index instrument)
  - Binary (proportion achieving MID)
  - Standardized mean difference
  - Ratio of means
- **Plain Language Integration**: Automated plain language summary generation

**Core GRADE Principles Implemented:**
- Risk-stratified absolute effects for clinical decision making
- Multiple presentation options to handle continuous outcome challenges
- Index instrument approach for interpretable mean differences
- Binary conversion using MID thresholds
- Plain language summaries following GRADE guidance

### 7. Evidence-to-Decision Framework (Core GRADE 7)

**New Models:**
- `EvidenceToDecisionFramework`: Comprehensive EtD framework
- `MinimalImportantDifference`: MID specification with evidence support
- `ValuesAndPreferences`: Patient values and preferences assessment

**Key Features:**
- **Perspective Selection**: Individual patient vs population perspective
- **Primary Considerations**: Benefits/harms, certainty, values/preferences
- **Secondary Considerations**: Costs, feasibility, acceptability, equity
- **MID Evidence Base**: Systematic documentation of MID sources and confidence
- **Recommendation Strength**: Framework for strong vs conditional recommendations

**Core GRADE Principles Implemented:**
- Structured evidence-to-decision process
- MID-based values and preferences integration
- Primary vs secondary consideration hierarchy
- Strong recommendations require high/moderate certainty + clear net benefit
- Conditional recommendations for close balance or low certainty
- Values and preferences statements with variability assessment

## Technical Implementation

### Database Architecture

The enhanced models maintain backward compatibility while adding sophisticated assessment capabilities:

- **Flexible JSON Storage**: Domain assessments and survey data stored as JSON for tool flexibility
- **File Upload Support**: Integrated file handling for RoB data, forest plots, funnel plots
- **Relationship Mapping**: Proper foreign key relationships maintaining data integrity
- **Audit Trail**: Comprehensive tracking of assessments, updates, and rationale

### Forms and User Interface

Enhanced forms provide guided input following Core GRADE methodology:

- **Progressive Disclosure**: Complex assessments broken into manageable sections
- **Contextual Help**: Integrated guidance reflecting Core GRADE principles
- **File Validation**: Appropriate file type and size restrictions
- **Data Validation**: Business logic validation ensuring methodological consistency

### Admin Interface

Comprehensive administrative interface for all enhanced models:

- **Organized Fieldsets**: Logical grouping of related fields
- **Search and Filtering**: Efficient navigation of large datasets
- **Readonly Fields**: Protection of calculated and metadata fields
- **Color-Coded Displays**: Visual indicators for certainty levels and decisions

## Usage Guide

### 1. Setting Up Enhanced Assessments

1. **Create GRADE Project**: Standard project creation with PICO specification
2. **Add Studies**: Include all studies with funding source information
3. **Define Outcomes**: Specify critical vs important outcomes with MIDs
4. **Conduct Domain Assessments**: Use enhanced forms for each GRADE domain

### 2. Risk of Bias Workflow

1. **Select RoB Tool**: Choose appropriate tool (RoB 2, ROBUST-RCT, etc.)
2. **Assess Individual Studies**: Binary low/high classification per outcome
3. **Upload RoB Data**: Optional CSV import for bulk assessments
4. **Weight Analysis**: System calculates if high RoB studies dominate
5. **Rating Decision**: Automated guidance on rating down based on weights

### 3. Imprecision Assessment

1. **Choose Target**: Select MID vs null threshold approach
2. **Specify MID**: Define MID value with supporting evidence
3. **CI Analysis**: Input confidence intervals for automated analysis
4. **OIS Consideration**: Assess sample size adequacy
5. **Rating Decision**: System guides rating down once vs twice

### 4. Creating Enhanced SoF Tables

1. **Select Risk Groups**: Define different baseline risk populations
2. **Configure Presentations**: Choose continuous outcome presentation formats
3. **Generate Table**: Automated creation with risk-stratified absolute effects
4. **Plain Language**: Integrated plain language summary generation

### 5. Evidence-to-Decision Process

1. **Perspective Selection**: Individual vs population viewpoint
2. **Primary Assessment**: Benefits/harms, certainty, values/preferences
3. **Secondary Assessment**: Costs, feasibility, acceptability, equity
4. **Recommendation Formation**: Structured recommendation with justification

## Migration and Compatibility

### Database Migrations

- **Migration 0003**: Adds all Core GRADE enhanced models
- **Backward Compatible**: Existing data and functionality preserved
- **Incremental Enhancement**: Enhanced features available alongside standard GRADE

### Data Import

- **CSV Support**: Risk of bias assessments via CSV upload
- **Image Support**: Forest plots and funnel plots (PNG, JPG, PDF, SVG)
- **JSON Flexibility**: Domain assessments and survey data as structured JSON

## Benefits

### For Systematic Reviewers

- **Methodological Rigor**: Implementation of latest Core GRADE guidance
- **Efficiency**: Streamlined assessment with guided workflows
- **Transparency**: Comprehensive documentation of assessment rationale
- **Flexibility**: Support for different RoB tools and assessment approaches

### for Guideline Developers

- **Evidence-to-Decision**: Structured framework for recommendation development
- **Risk Stratification**: Absolute effects for different patient populations
- **Values Integration**: Systematic incorporation of patient preferences
- **Plain Language**: Automated generation of interpretable summaries

### For Educators and Trainers

- **Best Practice**: Implementation reflects current methodological consensus
- **Learning Support**: Integrated guidance and contextual help
- **Standardization**: Consistent approach across different assessment teams
- **Audit Trail**: Complete documentation for quality assurance

## Future Enhancements

### Planned Features

1. **AI-Enhanced Assessment**: Integration of AI support for complex assessments
2. **Interactive Visualizations**: Dynamic forest plots and funnel plots
3. **Collaborative Features**: Multi-reviewer assessment with conflict resolution
4. **Export Capabilities**: Direct export to systematic review software
5. **Template Library**: Predefined templates for common clinical questions

### Research Integration

1. **Living Evidence**: Support for living systematic reviews and guidelines
2. **Network Meta-Analysis**: Integration with indirect comparison methods
3. **Individual Patient Data**: Enhanced support for IPD meta-analyses
4. **Machine Learning**: Automated detection of publication bias patterns

## Conclusion

The Core GRADE enhancements represent a significant advancement in AutoGRADE's capabilities, providing comprehensive support for the latest GRADE methodology. These enhancements maintain the system's ease of use while adding sophisticated assessment capabilities that reflect current best practices in evidence synthesis and guideline development.

The implementation provides a solid foundation for rigorous systematic reviews and evidence-based guideline development, with extensive documentation and support for the complete GRADE process from evidence assessment through recommendation formulation.
