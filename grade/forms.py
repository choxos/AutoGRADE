"""
Django forms for the AutoGRADE application
Basic forms for existing models only
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    GRADEProject, Outcome, Study, GRADEAssessment
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
            'importance': forms.Select(attrs={'class': 'form-select'}),
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
