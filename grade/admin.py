from django.contrib import admin
from django.utils.html import format_html
from .models import (
    GRADEProject, Outcome, Study, GRADEAssessment, 
    SummaryOfFindingsTable, PlainLanguageStatement, AIAnalysisSession,
    # Core GRADE enhanced models
    RiskOfBiasAssessment, ImprecisionAssessment, InconsistencyAssessment,
    SubgroupAnalysis, IndirectnessAssessment, PublicationBiasAssessment,
    EnhancedSummaryOfFindings, RiskGroup, ContinuousOutcomePresentation,
    EvidenceToDecisionFramework, MinimalImportantDifference, ValuesAndPreferences
)

@admin.register(GRADEProject)
class GRADEProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'outcomes_count', 'has_sof_table']
    list_filter = ['created_at', 'created_by']
    search_fields = ['title', 'description', 'population', 'intervention', 'comparison']
    readonly_fields = ['created_at', 'updated_at', 'ai_extracted_pico']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'description', 'created_by']
        }),
        ('PICO Elements', {
            'fields': ['population', 'intervention', 'comparison']
        }),
        ('Manuscript', {
            'fields': ['manuscript_file', 'manuscript_text']
        }),
        ('AI Analysis', {
            'fields': ['ai_extracted_pico'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def outcomes_count(self, obj):
        return obj.outcomes.count()
    outcomes_count.short_description = 'Outcomes'
    
    def has_sof_table(self, obj):
        return hasattr(obj, 'sof_table')
    has_sof_table.boolean = True
    has_sof_table.short_description = 'SoF Table'

@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'outcome_type', 'importance', 'grade_certainty', 'has_plain_language']
    list_filter = ['outcome_type', 'importance', 'project']
    search_fields = ['name', 'description', 'project__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['project', 'name', 'description', 'outcome_type', 'importance']
        }),
        ('Measurement', {
            'fields': ['measurement_scale', 'time_frame', 'minimal_important_difference']
        }),
        ('Effect Estimates', {
            'fields': [
                'relative_effect', 'relative_effect_type', 
                'confidence_interval_lower', 'confidence_interval_upper'
            ]
        }),
        ('Absolute Effects', {
            'fields': [
                'baseline_risk', 'intervention_risk', 'risk_difference',
                'risk_difference_ci_lower', 'risk_difference_ci_upper'
            ]
        }),
        ('Study Data', {
            'fields': ['number_of_studies', 'total_participants']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def grade_certainty(self, obj):
        try:
            assessment = obj.grade_assessment
            certainty = assessment.final_certainty.replace('_', ' ').title()
            color_map = {
                'High': '#28a745',
                'Moderate': '#ffc107', 
                'Low': '#fd7e14',
                'Very Low': '#dc3545'
            }
            color = color_map.get(certainty, '#6c757d')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, certainty
            )
        except:
            return 'Not assessed'
    grade_certainty.short_description = 'GRADE Certainty'
    
    def has_plain_language(self, obj):
        return hasattr(obj, 'plain_language')
    has_plain_language.boolean = True
    has_plain_language.short_description = 'Plain Language'

@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'study_type', 'year', 'total_participants', 'industry_funded']
    list_filter = ['study_type', 'year', 'industry_funded', 'project']
    search_fields = ['title', 'authors', 'journal', 'project__title']
    readonly_fields = ['created_at']

@admin.register(GRADEAssessment)
class GRADEAssessmentAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'starting_certainty', 'final_certainty', 'assessed_by', 'assessed_at']
    list_filter = ['starting_certainty', 'final_certainty', 'assessed_by', 'assessed_at']
    search_fields = ['outcome__name', 'outcome__project__title']
    readonly_fields = ['assessed_at', 'updated_at', 'final_certainty', 'ai_assessment_data']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['outcome', 'assessed_by', 'starting_certainty', 'final_certainty']
        }),
        ('Risk of Bias', {
            'fields': ['risk_of_bias', 'risk_of_bias_rationale', 'risk_of_bias_rating_down']
        }),
        ('Inconsistency', {
            'fields': ['inconsistency', 'inconsistency_rationale', 'inconsistency_rating_down']
        }),
        ('Indirectness', {
            'fields': ['indirectness', 'indirectness_rationale', 'indirectness_rating_down']
        }),
        ('Imprecision', {
            'fields': ['imprecision', 'imprecision_rationale', 'imprecision_rating_down']
        }),
        ('Publication Bias', {
            'fields': ['publication_bias', 'publication_bias_rationale', 'publication_bias_rating_down']
        }),
        ('Rating Up (Observational Studies)', {
            'fields': [
                'large_effect', 'large_effect_rationale', 'large_effect_rating_up',
                'dose_response', 'dose_response_rationale', 'dose_response_rating_up'
            ],
            'classes': ['collapse']
        }),
        ('AI Data', {
            'fields': ['ai_assessment_data'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['assessed_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(SummaryOfFindingsTable)
class SummaryOfFindingsTableAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'generated_by', 'generated_at']
    list_filter = ['generated_by', 'generated_at']
    search_fields = ['title', 'project__title']
    readonly_fields = ['generated_at', 'ai_generation_data']

@admin.register(PlainLanguageStatement)
class PlainLanguageStatementAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'certainty_description', 'generated_by_ai', 'created_at']
    list_filter = ['certainty_description', 'generated_by_ai', 'created_at']
    search_fields = ['outcome__name', 'statement']
    readonly_fields = ['created_at', 'updated_at', 'ai_generation_data']

@admin.register(AIAnalysisSession)
class AIAnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['session_type', 'project', 'created_by', 'processing_time', 'error_occurred', 'created_at']
    list_filter = ['session_type', 'error_occurred', 'created_by', 'created_at']
    search_fields = ['project__title', 'session_type', 'error_message']
    readonly_fields = ['created_at', 'input_data', 'ai_response']
    
    def has_add_permission(self, request):
        # Prevent manual creation of AI sessions
        return False


# =============================================================================
# CORE GRADE ENHANCED ADMIN CONFIGURATIONS
# Admin interfaces for detailed Core GRADE methodology support
# =============================================================================

@admin.register(RiskOfBiasAssessment)
class RiskOfBiasAssessmentAdmin(admin.ModelAdmin):
    list_display = ['study', 'outcome', 'tool_used', 'overall_classification', 'weight_in_analysis', 'assessed_by']
    list_filter = ['tool_used', 'overall_classification', 'assessed_by']
    search_fields = ['study__title', 'outcome__name', 'assessment_rationale']
    readonly_fields = ['assessed_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['study', 'outcome', 'tool_used', 'overall_classification', 'assessed_by']
        }),
        ('Assessment Details', {
            'fields': ['weight_in_analysis', 'domain_assessments', 'assessment_rationale']
        }),
        ('Data Upload', {
            'fields': ['rob_data_file']
        }),
        ('Notes', {
            'fields': ['reviewer_notes']
        }),
        ('Metadata', {
            'fields': ['assessed_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(ImprecisionAssessment)
class ImprecisionAssessmentAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'threshold_type', 'imprecision_decision', 'ci_crosses_threshold']
    list_filter = ['threshold_type', 'imprecision_decision', 'ci_crosses_threshold']
    search_fields = ['outcome__name', 'rationale']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['outcome', 'threshold_type', 'mid_value', 'null_value']
        }),
        ('Effect Estimates', {
            'fields': ['point_estimate', 'ci_lower_bound', 'ci_upper_bound']
        }),
        ('Threshold Analysis', {
            'fields': [
                'ci_crosses_threshold', 'ci_includes_important_benefit',
                'ci_includes_important_harm', 'ci_includes_no_effect'
            ]
        }),
        ('Sample Size', {
            'fields': ['sample_size', 'optimal_information_size', 'ois_criterion_met']
        }),
        ('Decision', {
            'fields': ['imprecision_decision', 'rationale']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(InconsistencyAssessment)
class InconsistencyAssessmentAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'i_squared', 'inconsistency_decision', 'subgroups_analyzed']
    list_filter = ['inconsistency_decision', 'subgroups_analyzed']
    search_fields = ['outcome__name', 'rationale']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['outcome', 'forest_plot_file']
        }),
        ('Statistical Analysis', {
            'fields': ['i_squared', 'i_squared_interpretation']
        }),
        ('Visual Inspection', {
            'fields': [
                'point_estimates_similar', 'cis_overlap', 'effects_same_side_threshold'
            ]
        }),
        ('Subgroup Analysis', {
            'fields': ['subgroup_hypotheses', 'subgroups_analyzed']
        }),
        ('Decision', {
            'fields': ['inconsistency_decision', 'rationale']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(SubgroupAnalysis)
class SubgroupAnalysisAdmin(admin.ModelAdmin):
    list_display = ['subgroup_name', 'inconsistency_assessment', 'credibility_level', 'hypothesis_prespecified']
    list_filter = ['credibility_level', 'hypothesis_prespecified', 'within_study_comparison']
    search_fields = ['subgroup_name', 'subgroup_description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['inconsistency_assessment', 'subgroup_name', 'subgroup_description']
        }),
        ('Credibility Assessment', {
            'fields': [
                'hypothesis_prespecified', 'within_study_comparison', 'interaction_test_p_value',
                'direction_consistent', 'biological_plausibility', 'credibility_level'
            ]
        }),
        ('Effect Estimates', {
            'fields': ['subgroup_effect_estimate', 'subgroup_ci_lower', 'subgroup_ci_upper']
        }),
        ('Assessment Decision', {
            'fields': ['requires_separate_assessment', 'credibility_rationale']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(IndirectnessAssessment)
class IndirectnessAssessmentAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'indirectness_decision', 'population_mismatch', 'intervention_mismatch']
    list_filter = ['indirectness_decision', 'population_mismatch', 'intervention_mismatch', 'is_surrogate_outcome']
    search_fields = ['outcome__name', 'rationale']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Target PICO', {
            'fields': ['outcome', 'target_population', 'target_intervention', 'target_comparison', 'target_outcome']
        }),
        ('Population Indirectness', {
            'fields': ['population_mismatch', 'population_differences']
        }),
        ('Intervention Indirectness', {
            'fields': ['intervention_mismatch', 'intervention_differences']
        }),
        ('Comparator Indirectness', {
            'fields': ['comparator_mismatch', 'comparator_differences']
        }),
        ('Outcome Indirectness', {
            'fields': ['outcome_mismatch', 'outcome_differences']
        }),
        ('Surrogate Outcomes', {
            'fields': ['is_surrogate_outcome', 'surrogate_relationship_strength']
        }),
        ('Decision', {
            'fields': ['indirectness_decision', 'rationale']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(PublicationBiasAssessment)
class PublicationBiasAssessmentAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'publication_bias_decision', 'funnel_plot_asymmetric', 'industry_sponsorship_common']
    list_filter = ['publication_bias_decision', 'funnel_plot_asymmetric', 'industry_sponsorship_common']
    search_fields = ['outcome__name', 'rationale']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['outcome', 'funnel_plot_file', 'number_of_studies']
        }),
        ('Funnel Plot Analysis', {
            'fields': ['funnel_plot_asymmetric', 'missing_studies_suspected']
        }),
        ('Statistical Tests', {
            'fields': [
                'eggers_test_performed', 'eggers_test_p_value',
                'beggs_test_performed', 'beggs_test_p_value', 'statistical_test_interpretation'
            ]
        }),
        ('Study Characteristics', {
            'fields': ['studies_mostly_small', 'industry_sponsorship_common']
        }),
        ('Unpublished Studies', {
            'fields': ['unpublished_studies_known', 'unpublished_studies_description']
        }),
        ('Search Strategy', {
            'fields': ['comprehensive_search_performed', 'search_strategy_description']
        }),
        ('Decision', {
            'fields': ['publication_bias_decision', 'rationale']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(MinimalImportantDifference)
class MinimalImportantDifferenceAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'mid_value', 'mid_source', 'confidence_in_mid']
    list_filter = ['mid_source', 'confidence_in_mid']
    search_fields = ['outcome__name', 'supporting_evidence']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['outcome', 'mid_value', 'mid_source']
        }),
        ('Evidence', {
            'fields': ['supporting_evidence', 'confidence_in_mid']
        }),
        ('Survey Data', {
            'fields': ['panel_survey_data']
        }),
        ('Alternatives', {
            'fields': ['alternative_mid_values']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(EvidenceToDecisionFramework)
class EvidenceToDecisionFrameworkAdmin(admin.ModelAdmin):
    list_display = ['project', 'perspective', 'recommendation_direction_strength', 'developed_by']
    list_filter = ['perspective', 'recommendation_direction_strength', 'developed_by']
    search_fields = ['project__title', 'recommendation_text']
    readonly_fields = ['developed_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['project', 'perspective', 'developed_by']
        }),
        ('Primary Considerations', {
            'fields': [
                'benefits_harms_assessment', 'certainty_of_evidence_summary',
                'values_preferences_statement'
            ]
        }),
        ('Secondary Considerations', {
            'fields': [
                'resource_costs_assessment', 'feasibility_assessment',
                'acceptability_assessment', 'equity_assessment'
            ]
        }),
        ('Recommendation', {
            'fields': [
                'recommendation_direction_strength', 'recommendation_text', 'justification'
            ]
        }),
        ('Panel Information', {
            'fields': ['panel_members']
        }),
        ('Metadata', {
            'fields': ['developed_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(ValuesAndPreferences)
class ValuesAndPreferencesAdmin(admin.ModelAdmin):
    list_display = ['project', 'variability_assessment', 'certainty_in_assessment']
    list_filter = ['variability_assessment', 'certainty_in_assessment']
    search_fields = ['project__title', 'values_preferences_summary']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['project']
        }),
        ('Evidence Sources', {
            'fields': [
                'systematic_review_conducted', 'focus_groups_conducted',
                'clinical_experience_consulted'
            ]
        }),
        ('Assessment Results', {
            'fields': [
                'values_preferences_summary', 'variability_assessment',
                'certainty_in_assessment'
            ]
        }),
        ('Supporting Evidence', {
            'fields': ['supporting_evidence']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(EnhancedSummaryOfFindings)
class EnhancedSummaryOfFindingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'risk_groups_used', 'generated_by']
    list_filter = ['risk_groups_used', 'plain_language_included', 'generated_by']
    search_fields = ['title', 'project__title']
    readonly_fields = ['generated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['project', 'title', 'description', 'generated_by']
        }),
        ('Configuration', {
            'fields': ['risk_groups_used', 'plain_language_included']
        }),
        ('Risk Information', {
            'fields': ['baseline_risk_source']
        }),
        ('Metadata', {
            'fields': ['generated_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(RiskGroup)
class RiskGroupAdmin(admin.ModelAdmin):
    list_display = ['group_name', 'sof_table', 'baseline_risk']
    list_filter = ['sof_table']
    search_fields = ['group_name', 'group_description']
    readonly_fields = ['created_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['sof_table', 'group_name', 'group_description']
        }),
        ('Risk Information', {
            'fields': ['baseline_risk', 'risk_factors']
        }),
        ('Metadata', {
            'fields': ['created_at'],
            'classes': ['collapse']
        })
    ]

@admin.register(ContinuousOutcomePresentation)
class ContinuousOutcomePresentationAdmin(admin.ModelAdmin):
    list_display = ['outcome', 'presentation_type', 'effect_estimate']
    list_filter = ['presentation_type']
    search_fields = ['outcome__name', 'index_instrument_name']
    readonly_fields = ['created_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['outcome', 'presentation_type']
        }),
        ('Index Instrument', {
            'fields': ['index_instrument_name', 'index_instrument_range']
        }),
        ('Effect Estimates', {
            'fields': [
                'control_group_value', 'intervention_group_value',
                'effect_estimate', 'ci_lower', 'ci_upper'
            ]
        }),
        ('Binary Presentation', {
            'fields': ['proportion_control', 'proportion_intervention']
        }),
        ('Notes', {
            'fields': ['interpretation_notes']
        }),
        ('Metadata', {
            'fields': ['created_at'],
            'classes': ['collapse']
        })
    ]
