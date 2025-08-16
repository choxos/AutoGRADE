"""
GRADE assessment engine using Claude Sonnet API
Implements the five GRADE domains based on Core GRADE methodology
"""
import json
import time
from typing import Dict, List, Optional, Tuple
from django.conf import settings
import anthropic

from ..models import GRADEProject, Outcome, Study, GRADEAssessment, AIAnalysisSession


class GRADEAssessmentEngine:
    """
    Uses Claude Sonnet to perform GRADE assessments based on Core GRADE methodology
    """
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured in settings")
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        
        # Load Core GRADE knowledge from the documents
        self.core_grade_knowledge = self._load_core_grade_knowledge()
    
    def _load_core_grade_knowledge(self) -> str:
        """
        Load Core GRADE methodology knowledge from the documents
        """
        return """
        Core GRADE Knowledge Base:
        
        GRADE (Grading of Recommendations Assessment, Development and Evaluation) is a systematic approach to rating the certainty of evidence and the strength of recommendations.
        
        Starting Certainty:
        - Randomized controlled trials: HIGH certainty
        - Observational studies: LOW certainty
        
        Five domains for rating DOWN certainty:
        
        1. RISK OF BIAS
        - Inadequate randomization, allocation concealment
        - Lack of blinding (participants, providers, assessors)
        - Missing outcome data
        - Selective outcome reporting
        - Other sources of bias
        
        2. INCONSISTENCY  
        - Heterogeneity between studies (I² > 50% may be concerning)
        - Wide variation in effect estimates
        - Non-overlapping confidence intervals
        - Statistical tests for heterogeneity (Chi² test, tau²)
        
        3. INDIRECTNESS
        - Population differences (age, disease severity, comorbidities)
        - Intervention differences (dose, duration, formulation)
        - Comparison differences (different control interventions)
        - Outcome differences (surrogate vs patient-important outcomes)
        
        4. IMPRECISION
        - Wide confidence intervals
        - Small sample sizes
        - Few events
        - Confidence interval crosses minimal important difference (MID)
        - Optimal Information Size (OIS) not met
        
        5. PUBLICATION BIAS
        - Small studies with positive results
        - Industry funding
        - Asymmetric funnel plots
        - Missing studies in registries
        
        Two domains for rating UP certainty (observational studies only):
        
        1. LARGE EFFECT
        - RR > 2 or < 0.5 (rate up 1 level)
        - RR > 5 or < 0.2 (rate up 2 levels)
        
        2. DOSE-RESPONSE GRADIENT
        - Clear dose-response relationship
        - Rate up 1 level
        
        Final Certainty Levels:
        - HIGH: Very confident the true effect is close to estimate
        - MODERATE: Moderately confident; true effect likely close to estimate
        - LOW: Limited confidence; true effect may be substantially different
        - VERY LOW: Very little confidence; true effect likely substantially different
        
        Plain Language Statements:
        - High certainty: "Treatment improves/reduces outcome"
        - Moderate certainty: "Treatment probably improves/reduces outcome" or "Treatment likely improves/reduces outcome"
        - Low certainty: "Treatment may improve/reduce outcome"
        - Very low certainty: "We are very uncertain about whether treatment improves/reduces outcome"
        """
    
    def assess_outcome(self, outcome: Outcome, user) -> GRADEAssessment:
        """
        Perform GRADE assessment for a single outcome
        """
        start_time = time.time()
        
        # Gather evidence data
        evidence_data = self._gather_evidence_data(outcome)
        
        # Create AI prompt for assessment
        prompt = self._create_assessment_prompt(outcome, evidence_data)
        
        try:
            # Call Claude Sonnet
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,  # Low temperature for consistency
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            ai_response = response.content[0].text
            processing_time = time.time() - start_time
            
            # Parse AI response
            assessment_data = self._parse_assessment_response(ai_response)
            
            # Create or update GRADE assessment
            grade_assessment = self._create_grade_assessment(
                outcome, assessment_data, user, ai_response
            )
            
            # Log AI session
            self._log_ai_session(
                outcome.project, 
                'grade_assessment', 
                evidence_data, 
                ai_response, 
                processing_time, 
                user
            )
            
            return grade_assessment
            
        except Exception as e:
            # Log error session
            self._log_ai_session(
                outcome.project, 
                'grade_assessment', 
                evidence_data, 
                None, 
                time.time() - start_time, 
                user, 
                error=str(e)
            )
            raise Exception(f"GRADE assessment failed: {str(e)}")
    
    def _gather_evidence_data(self, outcome: Outcome) -> Dict:
        """
        Gather all relevant evidence data for the outcome
        """
        project = outcome.project
        studies = project.studies.all()
        
        evidence_data = {
            'outcome': {
                'name': outcome.name,
                'description': outcome.description,
                'outcome_type': outcome.outcome_type,
                'importance': outcome.importance,
                'measurement_scale': outcome.measurement_scale,
                'time_frame': outcome.time_frame,
                'minimal_important_difference': outcome.minimal_important_difference,
                'relative_effect': outcome.relative_effect,
                'relative_effect_type': outcome.relative_effect_type,
                'confidence_interval_lower': outcome.confidence_interval_lower,
                'confidence_interval_upper': outcome.confidence_interval_upper,
                'baseline_risk': outcome.baseline_risk,
                'intervention_risk': outcome.intervention_risk,
                'risk_difference': outcome.risk_difference,
                'number_of_studies': outcome.number_of_studies,
                'total_participants': outcome.total_participants,
            },
            'studies': [
                {
                    'title': study.title,
                    'study_type': study.study_type,
                    'total_participants': study.total_participants,
                    'year': study.year,
                    'industry_funded': study.industry_funded,
                    'funding_source': study.funding_source,
                    'follow_up_duration': study.follow_up_duration,
                }
                for study in studies
            ],
            'project': {
                'population': project.population,
                'intervention': project.intervention,
                'comparison': project.comparison,
                'manuscript_text': project.manuscript_text[:2000] if project.manuscript_text else "",  # First 2000 chars
            }
        }
        
        return evidence_data
    
    def _create_assessment_prompt(self, outcome: Outcome, evidence_data: Dict) -> str:
        """
        Create the prompt for Claude Sonnet to assess GRADE domains
        """
        prompt = f"""
        You are an expert in evidence-based medicine and the GRADE methodology. Please perform a comprehensive GRADE assessment for the following outcome based on the Core GRADE approach.

        {self.core_grade_knowledge}

        EVIDENCE TO ASSESS:
        
        Project Context:
        Population: {evidence_data['project']['population']}
        Intervention: {evidence_data['project']['intervention']}  
        Comparison: {evidence_data['project']['comparison']}
        
        Outcome Details:
        Name: {evidence_data['outcome']['name']}
        Description: {evidence_data['outcome']['description']}
        Type: {evidence_data['outcome']['outcome_type']}
        Importance: {evidence_data['outcome']['importance']}/9
        Time Frame: {evidence_data['outcome']['time_frame']}
        Measurement: {evidence_data['outcome']['measurement_scale']}
        MID: {evidence_data['outcome']['minimal_important_difference']}
        
        Effect Estimates:
        Relative Effect: {evidence_data['outcome']['relative_effect']} ({evidence_data['outcome']['relative_effect_type']})
        95% CI: ({evidence_data['outcome']['confidence_interval_lower']}, {evidence_data['outcome']['confidence_interval_upper']})
        Baseline Risk: {evidence_data['outcome']['baseline_risk']}
        Risk Difference: {evidence_data['outcome']['risk_difference']}
        
        Study Characteristics:
        Number of Studies: {evidence_data['outcome']['number_of_studies']}
        Total Participants: {evidence_data['outcome']['total_participants']}
        
        Individual Studies:
        {json.dumps(evidence_data['studies'], indent=2)}
        
        ASSESSMENT TASK:
        
        Please provide a comprehensive GRADE assessment by evaluating each of the five domains for rating down and two domains for rating up (if applicable). Follow this exact JSON format:
        
        {{
            "starting_certainty": "high" | "low",
            "starting_rationale": "Brief explanation of starting certainty",
            
            "risk_of_bias": {{
                "concern_level": "not_serious" | "serious" | "very_serious" | "extremely_serious",
                "rating_down": 0 | 1 | 2,
                "rationale": "Detailed rationale for risk of bias assessment"
            }},
            
            "inconsistency": {{
                "concern_level": "not_serious" | "serious" | "very_serious" | "extremely_serious", 
                "rating_down": 0 | 1 | 2,
                "rationale": "Detailed rationale for inconsistency assessment"
            }},
            
            "indirectness": {{
                "concern_level": "not_serious" | "serious" | "very_serious" | "extremely_serious",
                "rating_down": 0 | 1 | 2,
                "rationale": "Detailed rationale for indirectness assessment"
            }},
            
            "imprecision": {{
                "concern_level": "not_serious" | "serious" | "very_serious" | "extremely_serious",
                "rating_down": 0 | 1 | 2,
                "rationale": "Detailed rationale for imprecision assessment"
            }},
            
            "publication_bias": {{
                "concern_level": "not_serious" | "serious" | "very_serious" | "extremely_serious",
                "rating_down": 0 | 1 | 2,
                "rationale": "Detailed rationale for publication bias assessment"
            }},
            
            "large_effect": {{
                "present": true | false,
                "rating_up": 0 | 1 | 2,
                "rationale": "Assessment of large effect magnitude"
            }},
            
            "dose_response": {{
                "present": true | false,
                "rating_up": 0 | 1,
                "rationale": "Assessment of dose-response gradient"
            }},
            
            "final_certainty": "high" | "moderate" | "low" | "very_low",
            "overall_rationale": "Summary explanation of final certainty rating",
            "plain_language_statement": "Plain language summary following GRADE guidance"
        }}
        
        Be thorough in your rationale for each domain. Consider the specific evidence provided and apply Core GRADE principles rigorously.
        """
        
        return prompt
    
    def _parse_assessment_response(self, ai_response: str) -> Dict:
        """
        Parse the AI response into structured assessment data
        """
        try:
            # Try to extract JSON from the response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = ai_response[json_start:json_end]
            assessment_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = [
                'starting_certainty', 'risk_of_bias', 'inconsistency', 
                'indirectness', 'imprecision', 'publication_bias',
                'large_effect', 'dose_response', 'final_certainty'
            ]
            
            for field in required_fields:
                if field not in assessment_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return assessment_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in AI response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing AI response: {str(e)}")
    
    def _create_grade_assessment(self, outcome: Outcome, assessment_data: Dict, user, ai_response: str) -> GRADEAssessment:
        """
        Create or update GRADE assessment from parsed data
        """
        # Get or create assessment
        grade_assessment, created = GRADEAssessment.objects.get_or_create(
            outcome=outcome,
            defaults={'assessed_by': user}
        )
        
        if not created:
            grade_assessment.assessed_by = user
        
        # Map assessment data to model fields
        grade_assessment.starting_certainty = assessment_data['starting_certainty']
        
        # Risk of bias
        rob = assessment_data['risk_of_bias']
        grade_assessment.risk_of_bias = rob['concern_level']
        grade_assessment.risk_of_bias_rationale = rob['rationale']
        grade_assessment.risk_of_bias_rating_down = rob['rating_down']
        
        # Inconsistency
        inc = assessment_data['inconsistency']
        grade_assessment.inconsistency = inc['concern_level']
        grade_assessment.inconsistency_rationale = inc['rationale']
        grade_assessment.inconsistency_rating_down = inc['rating_down']
        
        # Indirectness
        ind = assessment_data['indirectness']
        grade_assessment.indirectness = ind['concern_level']
        grade_assessment.indirectness_rationale = ind['rationale']
        grade_assessment.indirectness_rating_down = ind['rating_down']
        
        # Imprecision
        imp = assessment_data['imprecision']
        grade_assessment.imprecision = imp['concern_level']
        grade_assessment.imprecision_rationale = imp['rationale']
        grade_assessment.imprecision_rating_down = imp['rating_down']
        
        # Publication bias
        pub = assessment_data['publication_bias']
        grade_assessment.publication_bias = pub['concern_level']
        grade_assessment.publication_bias_rationale = pub['rationale']
        grade_assessment.publication_bias_rating_down = pub['rating_down']
        
        # Large effect
        le = assessment_data['large_effect']
        grade_assessment.large_effect = le['present']
        grade_assessment.large_effect_rationale = le['rationale']
        grade_assessment.large_effect_rating_up = le['rating_up']
        
        # Dose response
        dr = assessment_data['dose_response']
        grade_assessment.dose_response = dr['present']
        grade_assessment.dose_response_rationale = dr['rationale']
        grade_assessment.dose_response_rating_up = dr['rating_up']
        
        # Store raw AI data
        grade_assessment.ai_assessment_data = {
            'ai_response': ai_response,
            'parsed_data': assessment_data
        }
        
        grade_assessment.save()
        
        # Create plain language statement if provided
        if 'plain_language_statement' in assessment_data:
            from ..models import PlainLanguageStatement
            plain_lang, _ = PlainLanguageStatement.objects.get_or_create(
                outcome=outcome,
                defaults={
                    'statement': assessment_data['plain_language_statement'],
                    'certainty_description': self._get_certainty_description(grade_assessment.final_certainty),
                    'generated_by_ai': True,
                    'ai_generation_data': {'source': 'grade_assessment'}
                }
            )
            
            if _:  # If created new
                plain_lang.statement = assessment_data['plain_language_statement']
                plain_lang.save()
        
        return grade_assessment
    
    def _get_certainty_description(self, certainty: str) -> str:
        """Get appropriate certainty description for plain language"""
        descriptions = {
            'high': 'confident',
            'moderate': 'probably',
            'low': 'may',
            'very_low': 'very uncertain'
        }
        return descriptions.get(certainty, 'uncertain')
    
    def _log_ai_session(self, project: GRADEProject, session_type: str, input_data: Dict, 
                       ai_response: str, processing_time: float, user, error: str = None):
        """
        Log AI analysis session for debugging and improvement
        """
        AIAnalysisSession.objects.create(
            project=project,
            session_type=session_type,
            input_data=input_data,
            ai_response={'response': ai_response} if ai_response else {},
            processing_time=processing_time,
            error_occurred=bool(error),
            error_message=error or '',
            created_by=user
        )
    
    def assess_all_outcomes(self, project: GRADEProject, user) -> List[GRADEAssessment]:
        """
        Assess all outcomes in a project
        """
        assessments = []
        
        for outcome in project.outcomes.filter(importance__gte=4):  # Only important and critical outcomes
            try:
                assessment = self.assess_outcome(outcome, user)
                assessments.append(assessment)
            except Exception as e:
                # Log error but continue with other outcomes
                print(f"Error assessing outcome {outcome.name}: {str(e)}")
                continue
        
        return assessments
    
    def batch_assess_with_retry(self, outcomes: List[Outcome], user, max_retries: int = 2) -> Dict[int, GRADEAssessment]:
        """
        Assess multiple outcomes with retry logic
        """
        results = {}
        
        for outcome in outcomes:
            retries = 0
            while retries <= max_retries:
                try:
                    assessment = self.assess_outcome(outcome, user)
                    results[outcome.id] = assessment
                    break
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        print(f"Failed to assess outcome {outcome.name} after {max_retries} retries: {str(e)}")
                    else:
                        time.sleep(2 ** retries)  # Exponential backoff
        
        return results
