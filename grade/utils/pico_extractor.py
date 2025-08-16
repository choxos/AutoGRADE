"""
AI-powered PICO extraction using Claude Sonnet API
Extracts Population, Intervention, Comparison, and Outcome elements from manuscripts
"""
import json
import time
from typing import Dict, List, Optional
from django.conf import settings
import anthropic

from ..models import GRADEProject, AIAnalysisSession


class AIPICOExtractor:
    """
    Uses Claude Sonnet to extract PICO elements from manuscript text
    """
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured in settings")
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
    
    def extract_pico(self, manuscript_text: str, project: GRADEProject, user) -> Dict:
        """
        Extract PICO elements from manuscript text using AI
        """
        start_time = time.time()
        
        # Create prompt for PICO extraction
        prompt = self._create_pico_prompt(manuscript_text)
        
        try:
            # Call Claude Sonnet
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            ai_response = response.content[0].text
            processing_time = time.time() - start_time
            
            # Parse AI response
            pico_data = self._parse_pico_response(ai_response)
            
            # Log AI session
            self._log_ai_session(
                project, 
                'pico_extraction', 
                {'manuscript_length': len(manuscript_text)}, 
                ai_response, 
                processing_time, 
                user
            )
            
            return pico_data
            
        except Exception as e:
            # Log error session
            self._log_ai_session(
                project, 
                'pico_extraction', 
                {'manuscript_length': len(manuscript_text)}, 
                None, 
                time.time() - start_time, 
                user, 
                error=str(e)
            )
            raise Exception(f"PICO extraction failed: {str(e)}")
    
    def _create_pico_prompt(self, manuscript_text: str) -> str:
        """
        Create the prompt for Claude Sonnet to extract PICO elements
        """
        # Truncate text if too long
        max_chars = 15000
        if len(manuscript_text) > max_chars:
            manuscript_text = manuscript_text[:max_chars] + "...[truncated]"
        
        prompt = f"""
        You are an expert in evidence-based medicine and systematic review methodology. Please carefully analyze the following manuscript and extract the PICO (Population, Intervention, Comparison, Outcome) elements.

        Focus on identifying:
        - Population: The target patient population or participants
        - Intervention: The primary intervention being studied  
        - Comparison: The control or comparator intervention
        - Outcomes: All important outcomes measured (distinguish between primary and secondary)

        MANUSCRIPT TEXT:
        {manuscript_text}

        Please provide a comprehensive PICO extraction in the following JSON format:

        {{
            "population": {{
                "description": "Clear description of the target population",
                "age_range": "Age range if specified",
                "condition": "Primary condition or disease",
                "setting": "Healthcare setting (e.g., hospital, community, ICU)",
                "inclusion_criteria": ["Key inclusion criteria"],
                "exclusion_criteria": ["Key exclusion criteria"]
            }},
            
            "intervention": {{
                "name": "Primary intervention name",
                "description": "Detailed description of the intervention",
                "dose_or_intensity": "Dosage, frequency, or intensity if specified",
                "duration": "Treatment duration",
                "administration": "How the intervention is delivered"
            }},
            
            "comparison": {{
                "name": "Comparator name",
                "description": "Description of the control/comparator",
                "type": "placebo" | "active_control" | "standard_care" | "no_treatment",
                "details": "Additional details about the comparator"
            }},
            
            "outcomes": {{
                "primary": [
                    {{
                        "name": "Primary outcome name",
                        "description": "Detailed description",
                        "measurement": "How it's measured",
                        "timeframe": "When it's assessed",
                        "type": "beneficial" | "harmful" | "burden"
                    }}
                ],
                "secondary": [
                    {{
                        "name": "Secondary outcome name", 
                        "description": "Detailed description",
                        "measurement": "How it's measured",
                        "timeframe": "When it's assessed",
                        "type": "beneficial" | "harmful" | "burden"
                    }}
                ]
            }},
            
            "study_design": {{
                "type": "systematic_review" | "meta_analysis" | "rct" | "cohort" | "other",
                "description": "Brief description of study design",
                "search_strategy": "Search strategy if systematic review/meta-analysis",
                "databases_searched": ["List of databases if applicable"],
                "date_range": "Search date range if applicable"
            }},
            
            "statistical_methods": {{
                "effect_measure": "RR" | "OR" | "HR" | "MD" | "SMD" | "other",
                "pooling_method": "Fixed effects" | "Random effects" | "both" | "not_applicable",
                "heterogeneity_assessment": "Methods used to assess heterogeneity",
                "sensitivity_analysis": "Sensitivity analyses performed"
            }},
            
            "quality_assessment": {{
                "tools_used": ["Risk of bias tools used"],
                "grade_assessment": "Whether GRADE was mentioned/used",
                "quality_summary": "Summary of quality assessment approach"
            }},
            
            "key_findings": {{
                "number_of_studies": "Number of included studies if meta-analysis",
                "total_participants": "Total number of participants",
                "main_results": "Brief summary of main findings",
                "certainty_assessment": "Any mention of certainty/quality of evidence"
            }},
            
            "confidence": {{
                "population": 0.0-1.0,
                "intervention": 0.0-1.0, 
                "comparison": 0.0-1.0,
                "outcomes": 0.0-1.0,
                "overall": 0.0-1.0
            }},
            
            "extraction_notes": "Any important notes or limitations in the extraction"
        }}

        Be thorough and precise in your extraction. If information is not clearly available, indicate this rather than making assumptions. Provide confidence scores (0.0-1.0) for how certain you are about each extracted element.
        """
        
        return prompt
    
    def _parse_pico_response(self, ai_response: str) -> Dict:
        """
        Parse the AI response into structured PICO data
        """
        try:
            # Try to extract JSON from the response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = ai_response[json_start:json_end]
            pico_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['population', 'intervention', 'comparison', 'outcomes']
            
            for field in required_fields:
                if field not in pico_data:
                    raise ValueError(f"Missing required field: {field}")
            
            return pico_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in AI response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing AI response: {str(e)}")
    
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
    
    def extract_outcomes_from_pico(self, pico_data: Dict, project: GRADEProject, user) -> List:
        """
        Create Outcome objects from extracted PICO data
        """
        from ..models import Outcome
        
        created_outcomes = []
        
        # Process primary outcomes
        for outcome_data in pico_data.get('outcomes', {}).get('primary', []):
            outcome = Outcome.objects.create(
                project=project,
                name=outcome_data.get('name', ''),
                description=outcome_data.get('description', ''),
                outcome_type=outcome_data.get('type', 'beneficial'),
                importance=8,  # Primary outcomes are typically critical
                measurement_scale=outcome_data.get('measurement', ''),
                time_frame=outcome_data.get('timeframe', ''),
            )
            created_outcomes.append(outcome)
        
        # Process secondary outcomes
        for outcome_data in pico_data.get('outcomes', {}).get('secondary', []):
            outcome = Outcome.objects.create(
                project=project,
                name=outcome_data.get('name', ''),
                description=outcome_data.get('description', ''),
                outcome_type=outcome_data.get('type', 'beneficial'),
                importance=5,  # Secondary outcomes are typically important but not critical
                measurement_scale=outcome_data.get('measurement', ''),
                time_frame=outcome_data.get('timeframe', ''),
            )
            created_outcomes.append(outcome)
        
        return created_outcomes
    
    def update_project_from_pico(self, project: GRADEProject, pico_data: Dict) -> GRADEProject:
        """
        Update project fields from extracted PICO data
        """
        # Update population
        pop_data = pico_data.get('population', {})
        if pop_data.get('description'):
            project.population = pop_data['description']
        
        # Update intervention
        int_data = pico_data.get('intervention', {})
        if int_data.get('description'):
            project.intervention = int_data['description']
        elif int_data.get('name'):
            project.intervention = int_data['name']
        
        # Update comparison
        comp_data = pico_data.get('comparison', {})
        if comp_data.get('description'):
            project.comparison = comp_data['description']
        elif comp_data.get('name'):
            project.comparison = comp_data['name']
        
        # Store full PICO data
        project.ai_extracted_pico = pico_data
        
        project.save()
        return project
    
    def extract_and_create_complete_project(self, manuscript_text: str, project: GRADEProject, user) -> Dict:
        """
        Complete workflow: extract PICO, update project, create outcomes
        """
        # Extract PICO elements
        pico_data = self.extract_pico(manuscript_text, project, user)
        
        # Update project from PICO
        project = self.update_project_from_pico(project, pico_data)
        
        # Create outcome objects
        outcomes = self.extract_outcomes_from_pico(pico_data, project, user)
        
        return {
            'pico_data': pico_data,
            'project': project,
            'outcomes': outcomes,
            'success': True
        }
