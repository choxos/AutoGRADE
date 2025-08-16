"""
Django forms for the AutoGRADE application
Enhanced with Core GRADE methodology support
"""
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import (
    GRADEProject, Outcome, Study, GRADEAssessment, SummaryOfFindingsTable,
    # Core GRADE enhanced models
    RiskOfBiasAssessment, ImprecisionAssessment, InconsistencyAssessment,
    SubgroupAnalysis, IndirectnessAssessment, PublicationBiasAssessment,
    EnhancedSummaryOfFindings, RiskGroup, ContinuousOutcomePresentation,
    EvidenceToDecisionFramework, MinimalImportantDifference, ValuesAndPreferences
)


class GRADEProjectForm(forms.ModelForm):
    """
    Form for creating and editing GRADE projects
    """
    class Meta:
        model = GRADEProject
        fields = [
            'title', 'description', 'protocol_url',
            'population', 'intervention', 'comparison',
            'manuscript_file', 'supplementary_file'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a descriptive title for your systematic review',
                'maxlength': 255
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your research question and objectives',
                'rows': 4
            }),
            'protocol_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.crd.york.ac.uk/prospero/...'
            }),
            'population': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Adults with Type 2 diabetes',
                'rows': 3
            }),
            'intervention': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Metformin therapy',
                'rows': 3
            }),
            'comparison': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Placebo or standard care',
                'rows': 3
            }),
            'manuscript_file': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'fileInput',
                'style': 'display: none;',
                'accept': '.pdf,.docx,.txt,.md'
            }),
            'supplementary_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx,.xlsx,.txt,.md,.png,.jpg,.jpeg'
            }),
        }

    def clean_manuscript_file(self):
        """Validate manuscript file"""
        file = self.cleaned_data.get('manuscript_file')
        if file:
            # Check file size (25MB limit)
            if file.size > 25 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 25MB')
            
            # Check file extension
            allowed_extensions = ['pdf', 'docx', 'txt', 'md']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(f'Unsupported file format. Allowed formats: {", ".join(allowed_extensions)}')
        
        return file

    def clean_supplementary_file(self):
        """Validate supplementary file"""
        file = self.cleaned_data.get('supplementary_file')
        if file:
            # Check file size (50MB limit for supplementary files)
            if file.size > 50 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 50MB')
        
        return file


class OutcomeForm(forms.ModelForm):
    """
    Form for creating and editing outcomes
    """
    IMPORTANCE_CHOICES = [
        (9, '9 - Critical'),
        (8, '8 - Critical'),
        (7, '7 - Critical'),
        (6, '6 - Important'),
        (5, '5 - Important'),
        (4, '4 - Important'),
        (3, '3 - Limited importance'),
        (2, '2 - Limited importance'),
        (1, '1 - Limited importance'),
    ]

    importance = forms.ChoiceField(
        choices=IMPORTANCE_CHOICES,
        initial=7,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Outcome
        fields = [
            'name', 'description', 'outcome_type', 'importance',
            'relative_effect_type', 'relative_effect', 'confidence_interval_lower',
            'confidence_interval_upper', 'total_participants', 'number_of_studies'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mortality at 30 days'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of how the outcome was measured'
            }),
            'outcome_type': forms.Select(attrs={'class': 'form-select'}),
            'relative_effect_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Risk Ratio, Odds Ratio, Mean Difference'
            }),
            'relative_effect': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.25'
            }),
            'confidence_interval_lower': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.10'
            }),
            'confidence_interval_upper': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.42'
            }),
            'total_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'number_of_studies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }



class StudyForm(forms.ModelForm):
    """
    Form for creating and editing studies
    """
    class Meta:
        model = Study
        fields = [
            'title', 'authors', 'journal', 'year', 'study_type',
            'total_participants', 'intervention_participants', 'control_participants',
            'population_description', 'intervention_description',
            'control_description', 'follow_up_duration', 'funding_source',
            'industry_funded'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the full study title'
            }),
            'authors': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Smith J, Johnson K, et al.'
            }),
            'journal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of the journal'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2030'
            }),
            'study_type': forms.Select(attrs={'class': 'form-select'}),
            'total_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'intervention_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'control_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'population_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of the study population'
            }),
            'intervention_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of the intervention'
            }),
            'control_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of the control/comparison'
            }),
            'follow_up_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 12 months, 30 days'
            }),
            'funding_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Source of funding for the study'
            }),
            'industry_funded': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and (year < 1900 or year > 2030):
            raise ValidationError('Please enter a valid publication year.')
        return year


class PICOExtractionForm(forms.Form):
    """
    Form for manual PICO extraction or review of AI-extracted PICO
    """
    manuscript_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Paste your manuscript text here, or leave empty if you uploaded a file'
        }),
        required=False,
        help_text="You can paste text here or upload a file above"
    )
    
    extract_outcomes = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Automatically extract outcomes from the manuscript"
    )


class SoFTableForm(forms.Form):
    """
    Form for Summary of Findings table configuration
    """
    use_ai_enhancement = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Use AI to enhance the Summary of Findings table with additional context and formatting"
    )
    
    additional_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional notes or instructions for the SoF table'
        }),
        help_text="Optional notes for customizing the SoF table generation"
    )


class AssessmentRunForm(forms.Form):
    """
    Form for running GRADE assessments
    """
    selected_outcomes = forms.ModelMultipleChoiceField(
        queryset=Outcome.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select specific outcomes to assess, or leave empty to assess all outcomes"
    )
    
    force_reassess = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Re-assess outcomes that already have GRADE assessments"
    )

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['selected_outcomes'].queryset = project.outcomes.all()


class SearchForm(forms.Form):
    """
    General search form for projects and outcomes
    """
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...',
            'type': 'search'
        })
    )
    
    filter_type = forms.ChoiceField(
        choices=[
            ('all', 'All'),
            ('projects', 'Projects'),
            ('outcomes', 'Outcomes'),
            ('studies', 'Studies'),
        ],
        initial='all',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


# =============================================================================
# CORE GRADE ENHANCED FORMS
# Forms to support detailed Core GRADE methodology as per BMJ 2025 series
# =============================================================================

class RiskOfBiasAssessmentForm(forms.ModelForm):
    """
    Form for Risk of Bias assessment with Core GRADE tools support
    """
    class Meta:
        model = RiskOfBiasAssessment
        fields = [
            'tool_used', 'overall_classification', 'weight_in_analysis',
            'domain_assessments', 'assessment_rationale', 'reviewer_notes',
            'rob_data_file'
        ]
        widgets = {
            'tool_used': forms.Select(attrs={'class': 'form-select'}),
            'overall_classification': forms.Select(attrs={'class': 'form-select'}),
            'weight_in_analysis': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'max': '1',
                'placeholder': 'e.g., 0.150'
            }),
            'domain_assessments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Individual domain assessments (JSON format)'
            }),
            'assessment_rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Rationale for overall RoB classification'
            }),
            'reviewer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional reviewer notes'
            }),
            'rob_data_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv,.xlsx'
            }),
        }

    def clean_rob_data_file(self):
        """Validate RoB data file"""
        file = self.cleaned_data.get('rob_data_file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 10MB')
            
            # Check file extension
            allowed_extensions = ['csv', 'xlsx']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(f'Unsupported file format. Allowed formats: {", ".join(allowed_extensions)}')
        
        return file


class ImprecisionAssessmentForm(forms.ModelForm):
    """
    Form for enhanced imprecision assessment
    """
    class Meta:
        model = ImprecisionAssessment
        fields = [
            'threshold_type', 'mid_value', 'null_value', 'point_estimate',
            'ci_lower_bound', 'ci_upper_bound', 'ci_crosses_threshold',
            'ci_includes_important_benefit', 'ci_includes_important_harm',
            'ci_includes_no_effect', 'sample_size', 'optimal_information_size',
            'ois_criterion_met', 'imprecision_decision', 'rationale'
        ]
        widgets = {
            'threshold_type': forms.Select(attrs={'class': 'form-select'}),
            'mid_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'MID threshold value'
            }),
            'null_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '0 or 1 typically'
            }),
            'point_estimate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Point estimate of effect'
            }),
            'ci_lower_bound': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '95% CI lower bound'
            }),
            'ci_upper_bound': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '95% CI upper bound'
            }),
            'ci_crosses_threshold': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ci_includes_important_benefit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ci_includes_important_harm': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ci_includes_no_effect': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sample_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'optimal_information_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'ois_criterion_met': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imprecision_decision': forms.Select(attrs={'class': 'form-select'}),
            'rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Rationale for imprecision rating'
            }),
        }


class InconsistencyAssessmentForm(forms.ModelForm):
    """
    Form for inconsistency assessment with forest plot analysis
    """
    class Meta:
        model = InconsistencyAssessment
        fields = [
            'forest_plot_file', 'i_squared', 'i_squared_interpretation',
            'point_estimates_similar', 'cis_overlap', 'effects_same_side_threshold',
            'subgroup_hypotheses', 'subgroups_analyzed', 'inconsistency_decision', 'rationale'
        ]
        widgets = {
            'forest_plot_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.png,.jpg,.jpeg,.pdf,.svg'
            }),
            'i_squared': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.1',
                'placeholder': 'I² statistic (%)'
            }),
            'i_squared_interpretation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Interpretation of I² statistic'
            }),
            'point_estimates_similar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cis_overlap': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'effects_same_side_threshold': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'subgroup_hypotheses': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'A priori subgroup hypotheses to explain heterogeneity'
            }),
            'subgroups_analyzed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'inconsistency_decision': forms.Select(attrs={'class': 'form-select'}),
            'rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Rationale for inconsistency rating'
            }),
        }

    def clean_forest_plot_file(self):
        """Validate forest plot file"""
        file = self.cleaned_data.get('forest_plot_file')
        if file:
            # Check file size (25MB limit)
            if file.size > 25 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 25MB')
            
            # Check file extension
            allowed_extensions = ['png', 'jpg', 'jpeg', 'pdf', 'svg']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(f'Unsupported file format. Allowed formats: {", ".join(allowed_extensions)}')
        
        return file


class SubgroupAnalysisForm(forms.ModelForm):
    """
    Form for subgroup analysis with credibility assessment
    """
    class Meta:
        model = SubgroupAnalysis
        fields = [
            'subgroup_name', 'subgroup_description', 'hypothesis_prespecified',
            'within_study_comparison', 'interaction_test_p_value',
            'direction_consistent', 'biological_plausibility',
            'credibility_level', 'credibility_rationale',
            'subgroup_effect_estimate', 'subgroup_ci_lower', 'subgroup_ci_upper',
            'requires_separate_assessment'
        ]
        widgets = {
            'subgroup_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of the subgroup'
            }),
            'subgroup_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of the subgroup'
            }),
            'hypothesis_prespecified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'within_study_comparison': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'interaction_test_p_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'max': '1',
                'placeholder': 'P-value for interaction test'
            }),
            'direction_consistent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'biological_plausibility': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'credibility_level': forms.Select(attrs={'class': 'form-select'}),
            'credibility_rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Rationale for credibility assessment'
            }),
            'subgroup_effect_estimate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Subgroup effect estimate'
            }),
            'subgroup_ci_lower': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '95% CI lower bound'
            }),
            'subgroup_ci_upper': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': '95% CI upper bound'
            }),
            'requires_separate_assessment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class IndirectnessAssessmentForm(forms.ModelForm):
    """
    Form for indirectness assessment with PICO element comparison
    """
    class Meta:
        model = IndirectnessAssessment
        fields = [
            'target_population', 'target_intervention', 'target_comparison', 'target_outcome',
            'population_mismatch', 'population_differences',
            'intervention_mismatch', 'intervention_differences',
            'comparator_mismatch', 'comparator_differences',
            'outcome_mismatch', 'outcome_differences',
            'is_surrogate_outcome', 'surrogate_relationship_strength',
            'indirectness_decision', 'rationale'
        ]
        widgets = {
            'target_population': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Target population of interest'
            }),
            'target_intervention': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Target intervention of interest'
            }),
            'target_comparison': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Target comparator of interest'
            }),
            'target_outcome': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Target outcome of interest'
            }),
            'population_mismatch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'population_differences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe population differences'
            }),
            'intervention_mismatch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'intervention_differences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe intervention differences'
            }),
            'comparator_mismatch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'comparator_differences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe comparator differences'
            }),
            'outcome_mismatch': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'outcome_differences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe outcome differences'
            }),
            'is_surrogate_outcome': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'surrogate_relationship_strength': forms.Select(attrs={'class': 'form-select'}),
            'indirectness_decision': forms.Select(attrs={'class': 'form-select'}),
            'rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Rationale for indirectness rating'
            }),
        }


class PublicationBiasAssessmentForm(forms.ModelForm):
    """
    Form for publication bias assessment with funnel plots
    """
    class Meta:
        model = PublicationBiasAssessment
        fields = [
            'funnel_plot_file', 'funnel_plot_asymmetric', 'missing_studies_suspected',
            'eggers_test_performed', 'eggers_test_p_value',
            'beggs_test_performed', 'beggs_test_p_value', 'statistical_test_interpretation',
            'number_of_studies', 'studies_mostly_small', 'industry_sponsorship_common',
            'unpublished_studies_known', 'unpublished_studies_description',
            'comprehensive_search_performed', 'search_strategy_description',
            'publication_bias_decision', 'rationale'
        ]
        widgets = {
            'funnel_plot_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.png,.jpg,.jpeg,.pdf,.svg'
            }),
            'funnel_plot_asymmetric': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'missing_studies_suspected': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'eggers_test_performed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'eggers_test_p_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'max': '1',
                'placeholder': "Egger's test p-value"
            }),
            'beggs_test_performed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'beggs_test_p_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'max': '1',
                'placeholder': "Begg's test p-value"
            }),
            'statistical_test_interpretation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Interpretation of statistical tests'
            }),
            'number_of_studies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Number of studies in meta-analysis'
            }),
            'studies_mostly_small': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'industry_sponsorship_common': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'unpublished_studies_known': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'unpublished_studies_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe known unpublished studies'
            }),
            'comprehensive_search_performed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'search_strategy_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe search strategy and sources'
            }),
            'publication_bias_decision': forms.Select(attrs={'class': 'form-select'}),
            'rationale': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Rationale for publication bias assessment'
            }),
        }

    def clean_funnel_plot_file(self):
        """Validate funnel plot file"""
        file = self.cleaned_data.get('funnel_plot_file')
        if file:
            # Check file size (25MB limit)
            if file.size > 25 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 25MB')
            
            # Check file extension
            allowed_extensions = ['png', 'jpg', 'jpeg', 'pdf', 'svg']
            file_extension = file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError(f'Unsupported file format. Allowed formats: {", ".join(allowed_extensions)}')
        
        return file


class MinimalImportantDifferenceForm(forms.ModelForm):
    """
    Form for MID specification with supporting evidence
    """
    class Meta:
        model = MinimalImportantDifference
        fields = [
            'mid_value', 'mid_source', 'supporting_evidence',
            'confidence_in_mid', 'alternative_mid_values'
        ]
        widgets = {
            'mid_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'MID threshold value'
            }),
            'mid_source': forms.Select(attrs={'class': 'form-select'}),
            'supporting_evidence': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description of evidence supporting this MID value'
            }),
            'confidence_in_mid': forms.Select(attrs={'class': 'form-select'}),
            'alternative_mid_values': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Other MID estimates considered (JSON format)'
            }),
        }


class EvidenceToDecisionForm(forms.ModelForm):
    """
    Form for Evidence-to-Decision framework
    """
    class Meta:
        model = EvidenceToDecisionFramework
        fields = [
            'perspective', 'benefits_harms_assessment', 'certainty_of_evidence_summary',
            'values_preferences_statement', 'resource_costs_assessment',
            'feasibility_assessment', 'acceptability_assessment', 'equity_assessment',
            'recommendation_direction_strength', 'recommendation_text', 'justification',
            'panel_members'
        ]
        widgets = {
            'perspective': forms.Select(attrs={'class': 'form-select'}),
            'benefits_harms_assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Assessment of balance between benefits, harms, and burdens'
            }),
            'certainty_of_evidence_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Summary of certainty across critical and important outcomes'
            }),
            'values_preferences_statement': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "Statement about patients' values and preferences"
            }),
            'resource_costs_assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Assessment of costs, savings, and cost-effectiveness'
            }),
            'feasibility_assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Assessment of implementation feasibility'
            }),
            'acceptability_assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Assessment of acceptability to stakeholders'
            }),
            'equity_assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Assessment of impact on health equity'
            }),
            'recommendation_direction_strength': forms.Select(attrs={'class': 'form-select'}),
            'recommendation_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Full recommendation statement'
            }),
            'justification': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Justification for the recommendation'
            }),
            'panel_members': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'List of panel members involved in recommendation'
            }),
        }


class ValuesAndPreferencesForm(forms.ModelForm):
    """
    Form for patient values and preferences assessment
    """
    class Meta:
        model = ValuesAndPreferences
        fields = [
            'systematic_review_conducted', 'focus_groups_conducted',
            'clinical_experience_consulted', 'values_preferences_summary',
            'variability_assessment', 'certainty_in_assessment', 'supporting_evidence'
        ]
        widgets = {
            'systematic_review_conducted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'focus_groups_conducted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'clinical_experience_consulted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'values_preferences_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Summary of patient values and preferences assessment'
            }),
            'variability_assessment': forms.Select(attrs={'class': 'form-select'}),
            'certainty_in_assessment': forms.Select(attrs={'class': 'form-select'}),
            'supporting_evidence': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of supporting evidence'
            }),
        }


class EnhancedSummaryOfFindingsForm(forms.ModelForm):
    """
    Form for Enhanced Summary of Findings table with risk stratification
    """
    class Meta:
        model = EnhancedSummaryOfFindings
        fields = [
            'title', 'description', 'risk_groups_used',
            'baseline_risk_source', 'plain_language_included'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title for the Summary of Findings table'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of the SoF table'
            }),
            'risk_groups_used': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'baseline_risk_source': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Source of baseline risk estimates'
            }),
            'plain_language_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RiskGroupForm(forms.ModelForm):
    """
    Form for risk stratification groups
    """
    class Meta:
        model = RiskGroup
        fields = ['group_name', 'group_description', 'baseline_risk', 'risk_factors']
        widgets = {
            'group_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "e.g., 'Very low risk', 'High risk'"
            }),
            'group_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of risk group characteristics'
            }),
            'baseline_risk': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'max': '1',
                'placeholder': 'Baseline risk (0.0 to 1.0)'
            }),
            'risk_factors': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Risk factors that define this group'
            }),
        }
