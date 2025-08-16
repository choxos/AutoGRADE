from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json
import uuid

class GRADEProject(models.Model):
    """
    Main project containing a systematic review or meta-analysis assessment
    """
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # PICO Elements
    population = models.TextField(help_text="Target population description")
    intervention = models.TextField(help_text="Intervention being assessed")
    comparison = models.TextField(help_text="Comparator/control")
    
    # Protocol URL
    protocol_url = models.URLField(blank=True, help_text="Link to study protocol (PROSPERO, etc.)")
    
    # Manuscript files
    manuscript_file = models.FileField(upload_to='manuscripts/', null=True, blank=True)
    supplementary_file = models.FileField(upload_to='supplementary/', null=True, blank=True)
    manuscript_text = models.TextField(blank=True, help_text="Extracted text from manuscript")
    
    # AI-extracted PICO
    ai_extracted_pico = models.JSONField(null=True, blank=True, help_text="AI-extracted PICO elements")
    
    class Meta:
        ordering = ['-created_at']
    
    def get_assessment_count(self):
        """Get the number of completed GRADE assessments for this project"""
        from django.db.models import Count
        return GRADEAssessment.objects.filter(outcome__project=self).count()
    
    def __str__(self):
        return self.title

class Outcome(models.Model):
    """
    Individual outcomes assessed in the systematic review
    """
    OUTCOME_TYPES = [
        ('beneficial', 'Beneficial'),
        ('harmful', 'Harmful'),
        ('burden', 'Burden/Cost'),
    ]
    
    IMPORTANCE_LEVELS = [
        (1, 'Not Important (1-3)'),
        (2, 'Not Important (1-3)'),
        (3, 'Not Important (1-3)'),
        (4, 'Important (4-6)'),
        (5, 'Important (4-6)'),
        (6, 'Important (4-6)'),
        (7, 'Critical (7-9)'),
        (8, 'Critical (7-9)'),
        (9, 'Critical (7-9)'),
    ]
    
    project = models.ForeignKey(GRADEProject, on_delete=models.CASCADE, related_name='outcomes')
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    outcome_type = models.CharField(max_length=20, choices=OUTCOME_TYPES)
    importance = models.IntegerField(choices=IMPORTANCE_LEVELS, validators=[MinValueValidator(1), MaxValueValidator(9)])
    
    # Outcome measurement details
    measurement_scale = models.CharField(max_length=200, blank=True, help_text="e.g., Visual Analog Scale, mortality")
    time_frame = models.CharField(max_length=200, help_text="Duration of follow-up")
    minimal_important_difference = models.FloatField(null=True, blank=True, help_text="MID threshold")
    
    # Effect estimates
    relative_effect = models.FloatField(null=True, blank=True, help_text="RR, OR, HR")
    relative_effect_type = models.CharField(max_length=20, blank=True, help_text="RR, OR, HR, MD, SMD")
    confidence_interval_lower = models.FloatField(null=True, blank=True)
    confidence_interval_upper = models.FloatField(null=True, blank=True)
    
    # Absolute effects
    baseline_risk = models.FloatField(null=True, blank=True, help_text="Control group event rate")
    intervention_risk = models.FloatField(null=True, blank=True, help_text="Intervention group event rate")
    risk_difference = models.FloatField(null=True, blank=True)
    risk_difference_ci_lower = models.FloatField(null=True, blank=True)
    risk_difference_ci_upper = models.FloatField(null=True, blank=True)
    
    # Number of studies and participants
    number_of_studies = models.IntegerField(null=True, blank=True)
    total_participants = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-importance', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_importance_display()})"

class Study(models.Model):
    """
    Individual studies included in the systematic review
    """
    STUDY_TYPES = [
        ('rct', 'Randomized Controlled Trial'),
        ('cohort', 'Cohort Study'),
        ('case_control', 'Case-Control Study'),
        ('case_series', 'Case Series'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(GRADEProject, on_delete=models.CASCADE, related_name='studies')
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)
    year = models.IntegerField(null=True, blank=True)
    journal = models.CharField(max_length=200, blank=True)
    study_type = models.CharField(max_length=20, choices=STUDY_TYPES)
    
    # Participants
    total_participants = models.IntegerField(null=True, blank=True)
    intervention_participants = models.IntegerField(null=True, blank=True)
    control_participants = models.IntegerField(null=True, blank=True)
    
    # Study characteristics
    population_description = models.TextField(blank=True)
    intervention_description = models.TextField(blank=True)
    control_description = models.TextField(blank=True)
    follow_up_duration = models.CharField(max_length=100, blank=True)
    
    # Funding
    funding_source = models.CharField(max_length=200, blank=True)
    industry_funded = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['year', 'authors']
    
    def __str__(self):
        return f"{self.title} ({self.year})"

class GRADEAssessment(models.Model):
    """
    GRADE certainty assessment for each outcome
    """
    CERTAINTY_LEVELS = [
        ('very_low', 'Very Low'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]
    
    RATING_DECISIONS = [
        ('not_serious', 'Not Serious'),
        ('serious', 'Serious'),
        ('very_serious', 'Very Serious'),
        ('extremely_serious', 'Extremely Serious'),
    ]
    
    outcome = models.OneToOneField(Outcome, on_delete=models.CASCADE, related_name='grade_assessment')
    
    # Starting certainty
    starting_certainty = models.CharField(max_length=20, choices=CERTAINTY_LEVELS, default='high')
    
    # Five GRADE domains for rating down
    risk_of_bias = models.CharField(max_length=20, choices=RATING_DECISIONS, default='not_serious')
    risk_of_bias_rationale = models.TextField(blank=True)
    risk_of_bias_rating_down = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    
    inconsistency = models.CharField(max_length=20, choices=RATING_DECISIONS, default='not_serious')
    inconsistency_rationale = models.TextField(blank=True)
    inconsistency_rating_down = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    
    indirectness = models.CharField(max_length=20, choices=RATING_DECISIONS, default='not_serious')
    indirectness_rationale = models.TextField(blank=True)
    indirectness_rating_down = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    
    imprecision = models.CharField(max_length=20, choices=RATING_DECISIONS, default='not_serious')
    imprecision_rationale = models.TextField(blank=True)
    imprecision_rating_down = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    
    publication_bias = models.CharField(max_length=20, choices=RATING_DECISIONS, default='not_serious')
    publication_bias_rationale = models.TextField(blank=True)
    publication_bias_rating_down = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    
    # Reasons for rating up (for observational studies)
    large_effect = models.BooleanField(default=False)
    large_effect_rationale = models.TextField(blank=True)
    large_effect_rating_up = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    
    dose_response = models.BooleanField(default=False)
    dose_response_rationale = models.TextField(blank=True)
    dose_response_rating_up = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Final certainty
    final_certainty = models.CharField(max_length=20, choices=CERTAINTY_LEVELS)
    
    # AI assessment data
    ai_assessment_data = models.JSONField(null=True, blank=True, help_text="Raw AI assessment data")
    
    # Assessment metadata
    assessed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assessed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_final_certainty(self):
        """Calculate final certainty based on starting certainty and rating changes"""
        certainty_scores = {'high': 4, 'moderate': 3, 'low': 2, 'very_low': 1}
        certainty_levels = {1: 'very_low', 2: 'low', 3: 'moderate', 4: 'high'}
        
        # Start with initial certainty score
        if self.starting_certainty == 'high':
            score = 4
        elif self.starting_certainty == 'low':  # For observational studies
            score = 2
        else:
            score = certainty_scores.get(self.starting_certainty, 4)
        
        # Apply rating down
        total_rating_down = (
            self.risk_of_bias_rating_down +
            self.inconsistency_rating_down +
            self.indirectness_rating_down +
            self.imprecision_rating_down +
            self.publication_bias_rating_down
        )
        
        # Apply rating up (only for observational studies starting at low)
        total_rating_up = 0
        if self.starting_certainty == 'low':
            total_rating_up = (
                self.large_effect_rating_up +
                self.dose_response_rating_up
            )
        
        final_score = score - total_rating_down + total_rating_up
        final_score = max(1, min(4, final_score))  # Constrain between 1 and 4
        
        return certainty_levels[final_score]
    
    def save(self, *args, **kwargs):
        self.final_certainty = self.calculate_final_certainty()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"GRADE Assessment: {self.outcome.name} - {self.final_certainty.title()} Certainty"

class SummaryOfFindingsTable(models.Model):
    """
    Summary of Findings table following GRADE format
    """
    project = models.OneToOneField(GRADEProject, on_delete=models.CASCADE, related_name='sof_table')
    
    # Table metadata
    title = models.CharField(max_length=500)
    population = models.TextField()
    intervention = models.TextField()
    comparison = models.TextField()
    setting = models.CharField(max_length=200, blank=True)
    
    # Bibliography citation
    bibliography = models.TextField(blank=True, help_text="Citation for the systematic review")
    
    # Table generation metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # AI generation data
    ai_generation_data = models.JSONField(null=True, blank=True)
    
    def get_outcomes_by_importance(self):
        """Get outcomes ordered by importance (critical first, then important)"""
        return self.project.outcomes.filter(
            importance__gte=7  # Critical outcomes first
        ).union(
            self.project.outcomes.filter(
                importance__range=(4, 6)  # Important outcomes second
            )
        ).order_by('-importance', 'name')
    
    def __str__(self):
        return f"SoF Table: {self.title}"

class PlainLanguageStatement(models.Model):
    """
    Plain language statements for each outcome following GRADE guidance
    """
    outcome = models.OneToOneField(Outcome, on_delete=models.CASCADE, related_name='plain_language')
    
    statement = models.TextField(help_text="Plain language summary of the finding")
    certainty_description = models.CharField(max_length=100, help_text="e.g., 'likely', 'may', 'probably'")
    
    # AI generation metadata
    generated_by_ai = models.BooleanField(default=False)
    ai_generation_data = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Plain Language: {self.outcome.name}"

class AIAnalysisSession(models.Model):
    """
    Track AI analysis sessions for debugging and improvement
    """
    project = models.ForeignKey(GRADEProject, on_delete=models.CASCADE, related_name='ai_sessions')
    
    session_type = models.CharField(max_length=50)  # 'pico_extraction', 'grade_assessment', 'sof_generation'
    input_data = models.JSONField()  # Input sent to AI
    ai_response = models.JSONField()  # Full AI response
    processing_time = models.FloatField(null=True, blank=True)  # Time taken in seconds
    
    # Error handling
    error_occurred = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Session: {self.session_type} - {self.created_at}"


# =============================================================================
# CORE GRADE ENHANCED MODELS
# Models to support detailed Core GRADE methodology as per BMJ 2025 series
# =============================================================================

class RiskOfBiasAssessment(models.Model):
    """
    Risk of Bias assessment for individual studies with Core GRADE tools support
    """
    ROB_TOOLS = [
        ('rob2', 'RoB 2 (Cochrane)'),
        ('robust_rct', 'ROBUST-RCT'),
        ('robins_i', 'ROBINS-I'),
        ('newcastle_ottawa', 'Newcastle-Ottawa Scale'),
        ('clarity_cohort', 'CLARITY (Cohort)'),
        ('clarity_case_control', 'CLARITY (Case-Control)'),
        ('custom', 'Custom Tool'),
    ]
    
    ROB_CLASSIFICATION = [
        ('low', 'Low Risk of Bias'),
        ('high', 'High Risk of Bias'),
        ('unclear', 'Unclear Risk of Bias'),
    ]
    
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name='rob_assessments')
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name='rob_assessments')
    tool_used = models.CharField(max_length=50, choices=ROB_TOOLS)
    
    # Overall classification
    overall_classification = models.CharField(max_length=20, choices=ROB_CLASSIFICATION)
    weight_in_analysis = models.FloatField(
        help_text="Statistical weight of this study in the meta-analysis (0.0 to 1.0)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    
    # Individual domain assessments (flexible JSON to accommodate different tools)
    domain_assessments = models.JSONField(
        help_text="Individual domain assessments (e.g., randomization, blinding, etc.)",
        default=dict
    )
    
    # Rationale and notes
    assessment_rationale = models.TextField(blank=True)
    reviewer_notes = models.TextField(blank=True)
    
    # Data upload support
    rob_data_file = models.FileField(
        upload_to='rob_data/', 
        null=True, blank=True,
        help_text="Upload CSV file with RoB assessment data"
    )
    
    assessed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assessed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['study', 'outcome', 'tool_used']
        ordering = ['study__year', 'study__title']
    
    def __str__(self):
        return f"RoB: {self.study.title} - {self.overall_classification}"


class ImprecisionAssessment(models.Model):
    """
    Enhanced imprecision assessment supporting MID vs null threshold decisions
    """
    THRESHOLD_CHOICES = [
        ('mid', 'Minimal Important Difference (MID)'),
        ('null', 'Null Effect'),
    ]
    
    IMPRECISION_DECISIONS = [
        ('no_rating_down', 'No Rating Down'),
        ('rate_down_once', 'Rate Down Once'),
        ('rate_down_twice', 'Rate Down Twice'),
    ]
    
    outcome = models.OneToOneField(Outcome, on_delete=models.CASCADE, related_name='imprecision_assessment')
    
    # Threshold selection
    threshold_type = models.CharField(max_length=10, choices=THRESHOLD_CHOICES)
    mid_value = models.FloatField(null=True, blank=True, help_text="MID threshold value")
    null_value = models.FloatField(default=0.0, help_text="Null effect threshold (usually 0 or 1)")
    
    # Confidence interval analysis
    point_estimate = models.FloatField(help_text="Point estimate of effect")
    ci_lower_bound = models.FloatField(help_text="95% CI lower bound")
    ci_upper_bound = models.FloatField(help_text="95% CI upper bound")
    
    # Threshold crossing analysis
    ci_crosses_threshold = models.BooleanField(help_text="Does CI cross the threshold?")
    ci_includes_important_benefit = models.BooleanField(default=False)
    ci_includes_important_harm = models.BooleanField(default=False)
    ci_includes_no_effect = models.BooleanField(default=False)
    
    # Optimal Information Size (OIS) considerations
    sample_size = models.IntegerField(null=True, blank=True)
    optimal_information_size = models.IntegerField(null=True, blank=True)
    ois_criterion_met = models.BooleanField(default=False)
    
    # Final imprecision decision
    imprecision_decision = models.CharField(max_length=20, choices=IMPRECISION_DECISIONS)
    rationale = models.TextField(help_text="Rationale for imprecision rating")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Imprecision: {self.outcome.name} - {self.get_imprecision_decision_display()}"


class InconsistencyAssessment(models.Model):
    """
    Inconsistency assessment with forest plot analysis and subgroup evaluation
    """
    INCONSISTENCY_DECISIONS = [
        ('no_rating_down', 'No Rating Down'),
        ('rate_down_once', 'Rate Down Once'),
        ('rate_down_twice', 'Rate Down Twice'),
    ]
    
    outcome = models.OneToOneField(Outcome, on_delete=models.CASCADE, related_name='inconsistency_assessment')
    
    # Forest plot analysis
    forest_plot_file = models.FileField(
        upload_to='forest_plots/', 
        null=True, blank=True,
        help_text="Upload forest plot image or data file"
    )
    
    # I² statistic
    i_squared = models.FloatField(
        null=True, blank=True,
        help_text="I² statistic (0-100%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    i_squared_interpretation = models.TextField(blank=True)
    
    # Visual inspection criteria
    point_estimates_similar = models.BooleanField(help_text="Are point estimates similar across studies?")
    cis_overlap = models.BooleanField(help_text="Do confidence intervals overlap?")
    effects_same_side_threshold = models.BooleanField(help_text="Are effects on same side of threshold?")
    
    # Subgroup analysis
    subgroup_hypotheses = models.TextField(
        blank=True,
        help_text="A priori subgroup hypotheses to explain heterogeneity"
    )
    subgroups_analyzed = models.BooleanField(default=False)
    
    # Final inconsistency decision
    inconsistency_decision = models.CharField(max_length=20, choices=INCONSISTENCY_DECISIONS)
    rationale = models.TextField(help_text="Rationale for inconsistency rating")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inconsistency: {self.outcome.name} - {self.get_inconsistency_decision_display()}"


class SubgroupAnalysis(models.Model):
    """
    Subgroup analysis with credibility assessment
    """
    CREDIBILITY_LEVELS = [
        ('low', 'Low Credibility'),
        ('moderate', 'Moderate Credibility'),
        ('high', 'High Credibility'),
    ]
    
    inconsistency_assessment = models.ForeignKey(
        InconsistencyAssessment, 
        on_delete=models.CASCADE, 
        related_name='subgroup_analyses'
    )
    
    subgroup_name = models.CharField(max_length=200)
    subgroup_description = models.TextField()
    hypothesis_prespecified = models.BooleanField(help_text="Was this hypothesis specified a priori?")
    
    # Credibility assessment criteria
    within_study_comparison = models.BooleanField(
        help_text="Is the comparison within studies rather than between studies?"
    )
    interaction_test_p_value = models.FloatField(
        null=True, blank=True,
        help_text="P-value for interaction test"
    )
    direction_consistent = models.BooleanField(
        help_text="Is direction of effect consistent across subgroups?"
    )
    biological_plausibility = models.BooleanField(
        help_text="Is there biological plausibility for the subgroup effect?"
    )
    
    # Overall credibility
    credibility_level = models.CharField(max_length=20, choices=CREDIBILITY_LEVELS)
    credibility_rationale = models.TextField()
    
    # Effect estimates for subgroup
    subgroup_effect_estimate = models.FloatField(null=True, blank=True)
    subgroup_ci_lower = models.FloatField(null=True, blank=True)
    subgroup_ci_upper = models.FloatField(null=True, blank=True)
    
    requires_separate_assessment = models.BooleanField(
        default=False,
        help_text="Does this subgroup require separate evidence summary and certainty rating?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Subgroup: {self.subgroup_name} ({self.credibility_level})"


class IndirectnessAssessment(models.Model):
    """
    Indirectness assessment with PICO element comparison
    """
    INDIRECTNESS_DECISIONS = [
        ('no_rating_down', 'No Rating Down'),
        ('rate_down_once', 'Rate Down Once'),
        ('rate_down_twice', 'Rate Down Twice'),
    ]
    
    outcome = models.OneToOneField(Outcome, on_delete=models.CASCADE, related_name='indirectness_assessment')
    
    # Target PICO (what we want to know about)
    target_population = models.TextField(help_text="Target population of interest")
    target_intervention = models.TextField(help_text="Target intervention of interest")
    target_comparison = models.TextField(help_text="Target comparator of interest")
    target_outcome = models.TextField(help_text="Target outcome of interest")
    
    # Population indirectness
    population_mismatch = models.BooleanField(default=False)
    population_differences = models.TextField(
        blank=True,
        help_text="Describe differences between target and study populations"
    )
    
    # Intervention indirectness
    intervention_mismatch = models.BooleanField(default=False)
    intervention_differences = models.TextField(
        blank=True,
        help_text="Describe differences in intervention (dose, duration, adherence, etc.)"
    )
    
    # Comparator indirectness
    comparator_mismatch = models.BooleanField(default=False)
    comparator_differences = models.TextField(
        blank=True,
        help_text="Describe differences in comparator (suboptimal care, placebo vs active, etc.)"
    )
    
    # Outcome indirectness
    outcome_mismatch = models.BooleanField(default=False)
    outcome_differences = models.TextField(
        blank=True,
        help_text="Describe differences in outcome (surrogate vs patient-important, timing)"
    )
    
    # Surrogate outcome assessment
    is_surrogate_outcome = models.BooleanField(default=False)
    surrogate_relationship_strength = models.CharField(
        max_length=20,
        choices=[
            ('strong', 'Strong relationship to patient-important outcome'),
            ('moderate', 'Moderate relationship'),
            ('weak', 'Weak relationship'),
            ('uncertain', 'Uncertain relationship'),
        ],
        blank=True
    )
    
    # Overall indirectness decision
    indirectness_decision = models.CharField(max_length=20, choices=INDIRECTNESS_DECISIONS)
    rationale = models.TextField(help_text="Rationale for indirectness rating")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Indirectness: {self.outcome.name} - {self.get_indirectness_decision_display()}"


class PublicationBiasAssessment(models.Model):
    """
    Publication bias assessment with funnel plots and statistical tests
    """
    PUBLICATION_BIAS_DECISIONS = [
        ('undetected', 'Publication bias undetected'),
        ('strongly_suspected', 'Publication bias strongly suspected'),
    ]
    
    outcome = models.OneToOneField(Outcome, on_delete=models.CASCADE, related_name='publication_bias_assessment')
    
    # Funnel plot analysis
    funnel_plot_file = models.FileField(
        upload_to='funnel_plots/', 
        null=True, blank=True,
        help_text="Upload funnel plot image"
    )
    funnel_plot_asymmetric = models.BooleanField(
        help_text="Is the funnel plot visually asymmetric?"
    )
    missing_studies_suspected = models.BooleanField(
        help_text="Are studies missing from expected regions of funnel plot?"
    )
    
    # Statistical tests
    eggers_test_performed = models.BooleanField(default=False)
    eggers_test_p_value = models.FloatField(null=True, blank=True)
    beggs_test_performed = models.BooleanField(default=False)
    beggs_test_p_value = models.FloatField(null=True, blank=True)
    statistical_test_interpretation = models.TextField(blank=True)
    
    # Study characteristics
    number_of_studies = models.IntegerField(help_text="Number of studies in meta-analysis")
    studies_mostly_small = models.BooleanField(help_text="Are most studies small?")
    industry_sponsorship_common = models.BooleanField(
        help_text="Are most/all studies industry sponsored?"
    )
    
    # Documentation of unpublished studies
    unpublished_studies_known = models.BooleanField(
        default=False,
        help_text="Are there known unpublished studies?"
    )
    unpublished_studies_description = models.TextField(
        blank=True,
        help_text="Describe known unpublished studies and their potential impact"
    )
    
    # Search comprehensiveness
    comprehensive_search_performed = models.BooleanField(
        help_text="Was a comprehensive search performed (multiple databases, registries, etc.)?"
    )
    search_strategy_description = models.TextField(
        blank=True,
        help_text="Describe search strategy and sources"
    )
    
    # Final publication bias decision
    publication_bias_decision = models.CharField(max_length=30, choices=PUBLICATION_BIAS_DECISIONS)
    rationale = models.TextField(help_text="Rationale for publication bias assessment")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Publication Bias: {self.outcome.name} - {self.get_publication_bias_decision_display()}"


class EnhancedSummaryOfFindings(models.Model):
    """
    Enhanced Summary of Findings table with multiple risk groups and presentation options
    """
    project = models.ForeignKey(GRADEProject, on_delete=models.CASCADE, related_name='enhanced_sof_tables')
    
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    # Multiple risk groups support
    risk_groups_used = models.BooleanField(
        default=False,
        help_text="Does this SoF table stratify by different risk groups?"
    )
    
    # Baseline risk sources
    baseline_risk_source = models.TextField(
        blank=True,
        help_text="Source of baseline risk estimates (systematic review, pragmatic trial, etc.)"
    )
    
    # Plain language summaries included
    plain_language_included = models.BooleanField(default=True)
    
    # Generation metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Enhanced SoF: {self.title}"


class RiskGroup(models.Model):
    """
    Risk stratification groups for calculating different absolute effects
    """
    sof_table = models.ForeignKey(
        EnhancedSummaryOfFindings, 
        on_delete=models.CASCADE, 
        related_name='risk_groups'
    )
    
    group_name = models.CharField(max_length=200, help_text="e.g., 'Very low risk', 'High risk'")
    group_description = models.TextField(help_text="Description of risk group characteristics")
    baseline_risk = models.FloatField(help_text="Baseline risk for this group (0.0 to 1.0)")
    
    # Risk group criteria
    risk_factors = models.TextField(
        blank=True,
        help_text="Risk factors that define this group"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['baseline_risk']
    
    def __str__(self):
        return f"{self.group_name} (Risk: {self.baseline_risk:.3f})"


class ContinuousOutcomePresentation(models.Model):
    """
    Multiple presentation options for continuous outcomes
    """
    PRESENTATION_OPTIONS = [
        ('mean_difference', 'Mean Difference (Index Instrument)'),
        ('binary_mid', 'Binary (Proportion Above MID)'),
        ('standardized_mean_difference', 'Standardized Mean Difference'),
        ('ratio_of_means', 'Ratio of Means'),
    ]
    
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name='presentations')
    presentation_type = models.CharField(max_length=50, choices=PRESENTATION_OPTIONS)
    
    # Index instrument details (for mean difference presentation)
    index_instrument_name = models.CharField(max_length=200, blank=True)
    index_instrument_range = models.CharField(
        max_length=100, blank=True,
        help_text="e.g., '0-100, higher scores better'"
    )
    
    # Effect estimates in this presentation format
    control_group_value = models.FloatField(null=True, blank=True)
    intervention_group_value = models.FloatField(null=True, blank=True)
    effect_estimate = models.FloatField(help_text="Effect estimate in this format")
    ci_lower = models.FloatField(help_text="95% CI lower bound")
    ci_upper = models.FloatField(help_text="95% CI upper bound")
    
    # For binary MID presentation
    proportion_control = models.FloatField(
        null=True, blank=True,
        help_text="Proportion achieving MID in control group"
    )
    proportion_intervention = models.FloatField(
        null=True, blank=True,
        help_text="Proportion achieving MID in intervention group"
    )
    
    # Interpretation notes
    interpretation_notes = models.TextField(
        blank=True,
        help_text="Notes on interpreting this presentation format"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.outcome.name} - {self.get_presentation_type_display()}"


class EvidenceToDecisionFramework(models.Model):
    """
    Evidence-to-Decision framework for moving from evidence to recommendations
    """
    RECOMMENDATION_STRENGTH = [
        ('strong_for', 'Strong Recommendation For'),
        ('conditional_for', 'Conditional Recommendation For'),
        ('conditional_against', 'Conditional Recommendation Against'),
        ('strong_against', 'Strong Recommendation Against'),
        ('either_option', 'Either Option Acceptable'),
        ('research_only', 'Only in Research Setting'),
    ]
    
    PERSPECTIVE_CHOICES = [
        ('individual', 'Individual Patient Perspective'),
        ('individual_population', 'Individual Patient + Population Perspective'),
        ('population', 'Population Perspective'),
    ]
    
    project = models.OneToOneField(
        GRADEProject, 
        on_delete=models.CASCADE, 
        related_name='etd_framework'
    )
    
    # Perspective
    perspective = models.CharField(max_length=30, choices=PERSPECTIVE_CHOICES)
    
    # Primary considerations (always considered)
    benefits_harms_assessment = models.TextField(
        help_text="Assessment of balance between benefits, harms, and burdens"
    )
    
    certainty_of_evidence_summary = models.TextField(
        help_text="Summary of certainty across critical and important outcomes"
    )
    
    values_preferences_statement = models.TextField(
        help_text="Statement about patients' values and preferences"
    )
    
    # Secondary considerations (population perspective)
    resource_costs_assessment = models.TextField(
        blank=True,
        help_text="Assessment of costs, savings, and cost-effectiveness"
    )
    
    feasibility_assessment = models.TextField(
        blank=True,
        help_text="Assessment of implementation feasibility"
    )
    
    acceptability_assessment = models.TextField(
        blank=True,
        help_text="Assessment of acceptability to stakeholders"
    )
    
    equity_assessment = models.TextField(
        blank=True,
        help_text="Assessment of impact on health equity"
    )
    
    # Final recommendation
    recommendation_direction_strength = models.CharField(
        max_length=30, 
        choices=RECOMMENDATION_STRENGTH
    )
    
    recommendation_text = models.TextField(
        help_text="Full recommendation statement"
    )
    
    justification = models.TextField(
        help_text="Justification for the recommendation"
    )
    
    # Recommendation metadata
    panel_members = models.TextField(
        blank=True,
        help_text="List of panel members involved in recommendation"
    )
    
    developed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    developed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"EtD Framework: {self.project.title} - {self.get_recommendation_direction_strength_display()}"


class MinimalImportantDifference(models.Model):
    """
    MID specifications for outcomes with supporting evidence
    """
    MID_SOURCES = [
        ('systematic_review', 'Systematic Review of MID Studies'),
        ('anchor_based', 'Anchor-based Methods'),
        ('distribution_based', 'Distribution-based Methods'),
        ('panel_survey', 'Panel Survey'),
        ('focus_group', 'Focus Group'),
        ('clinical_experience', 'Clinical Experience'),
        ('literature_estimate', 'Literature Estimate'),
    ]
    
    outcome = models.OneToOneField(Outcome, on_delete=models.CASCADE, related_name='mid_specification')
    
    mid_value = models.FloatField(help_text="MID threshold value")
    mid_source = models.CharField(max_length=30, choices=MID_SOURCES)
    
    # Evidence supporting MID
    supporting_evidence = models.TextField(
        help_text="Description of evidence supporting this MID value"
    )
    
    confidence_in_mid = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High Confidence'),
            ('moderate', 'Moderate Confidence'),
            ('low', 'Low Confidence'),
        ]
    )
    
    # Panel survey data if applicable
    panel_survey_data = models.JSONField(
        null=True, blank=True,
        help_text="Raw data from panel MID survey"
    )
    
    # Alternative MID estimates
    alternative_mid_values = models.JSONField(
        default=list,
        help_text="Other MID estimates considered"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MID: {self.outcome.name} = {self.mid_value} ({self.get_mid_source_display()})"


class ValuesAndPreferences(models.Model):
    """
    Assessment of patient values and preferences
    """
    project = models.OneToOneField(
        GRADEProject, 
        on_delete=models.CASCADE, 
        related_name='values_preferences'
    )
    
    # Evidence sources
    systematic_review_conducted = models.BooleanField(
        default=False,
        help_text="Was a systematic review of values and preferences conducted?"
    )
    
    focus_groups_conducted = models.BooleanField(
        default=False,
        help_text="Were focus groups with patients conducted?"
    )
    
    clinical_experience_consulted = models.BooleanField(
        default=False,
        help_text="Was clinical experience with shared decision making consulted?"
    )
    
    # Assessment results
    values_preferences_summary = models.TextField(
        help_text="Summary of patient values and preferences assessment"
    )
    
    variability_assessment = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Variability'),
            ('moderate', 'Moderate Variability'),
            ('high', 'High Variability'),
        ],
        help_text="Variability in values and preferences across patients"
    )
    
    certainty_in_assessment = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High Certainty'),
            ('moderate', 'Moderate Certainty'),
            ('low', 'Low Certainty'),
        ],
        help_text="Certainty in values and preferences assessment"
    )
    
    # Supporting data
    supporting_evidence = models.TextField(
        blank=True,
        help_text="Detailed description of supporting evidence"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Values & Preferences: {self.project.title}"
