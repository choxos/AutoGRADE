"""
Django views for the AutoGRADE application
Handles web interface for manuscript upload, GRADE assessment, and SoF table generation
"""
import json
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    GRADEProject, Outcome, Study, GRADEAssessment,
    SummaryOfFindingsTable, PlainLanguageStatement, AIAnalysisSession
)
from .forms import GRADEProjectForm, OutcomeForm, StudyForm
from .utils.manuscript_processor import ManuscriptProcessor
from .utils.pico_extractor import AIPICOExtractor
from .utils.grade_engine import GRADEAssessmentEngine
from .utils.sof_generator import SoFTableGenerator


@login_required
def dashboard(request):
    """
    Main dashboard showing user's projects and recent activity
    """
    user_projects = GRADEProject.objects.filter(created_by=request.user).order_by('-created_at')
    recent_assessments = GRADEAssessment.objects.filter(
        assessed_by=request.user
    ).order_by('-assessed_at')[:5]
    
    context = {
        'projects': user_projects[:10],  # Latest 10 projects
        'recent_assessments': recent_assessments,
        'total_projects': user_projects.count(),
        'total_outcomes': Outcome.objects.filter(project__created_by=request.user).count(),
    }
    
    return render(request, 'grade/dashboard.html', context)


@login_required
def project_list(request):
    """
    List all projects for the user with search and filtering
    """
    projects = GRADEProject.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(population__icontains=search_query) |
            Q(intervention__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(projects, 12)  # 12 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'grade/project_list.html', context)


@login_required
def project_create(request):
    """
    Create a new GRADE project
    """
    if request.method == 'POST':
        form = GRADEProjectForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create project
                project = form.save(commit=False)
                project.created_by = request.user
                project.save()
                
                # Process manuscript if uploaded
                if project.manuscript_file:
                    try:
                        processor = ManuscriptProcessor()
                        file_path = project.manuscript_file.path
                        extracted_text = processor.extract_text(file_path)
                        project.manuscript_text = extracted_text
                        project.save()
                        
                        # Extract PICO using AI if enabled
                        if extracted_text:
                            try:
                                pico_extractor = AIPICOExtractor()
                                pico_result = pico_extractor.extract_and_create_complete_project(
                                    extracted_text, project, request.user
                                )
                                messages.success(request, 'Project created successfully! PICO elements and outcomes have been automatically extracted.')
                            except Exception as e:
                                messages.warning(request, f'Project created, but AI extraction failed: {str(e)}')
                        
                    except Exception as e:
                        messages.warning(request, f'Project created, but manuscript processing failed: {str(e)}')
                else:
                    messages.success(request, 'Project created successfully!')
                
                return redirect('grade:project_detail', project_id=project.id)
                
            except Exception as e:
                messages.error(request, f'Error creating project: {str(e)}')
    else:
        form = GRADEProjectForm()
    
    context = {
        'form': form,
    }
    return render(request, 'grade/project_create.html', context)


@login_required
def project_detail(request, project_id):
    """
    Detailed view of a GRADE project
    """
    project = get_object_or_404(GRADEProject, id=project_id, created_by=request.user)
    
    # Get outcomes ordered by importance
    critical_outcomes = project.outcomes.filter(importance__gte=7).order_by('-importance', 'name')
    important_outcomes = project.outcomes.filter(importance__range=(4, 6)).order_by('-importance', 'name')
    other_outcomes = project.outcomes.filter(importance__lt=4).order_by('-importance', 'name')
    
    # Get studies
    studies = project.studies.all().order_by('-year', 'title')
    
    # Get SoF table if exists
    sof_table = getattr(project, 'sof_table', None)
    
    # Get recent AI sessions
    recent_sessions = project.ai_sessions.order_by('-created_at')[:5]
    
    context = {
        'project': project,
        'critical_outcomes': critical_outcomes,
        'important_outcomes': important_outcomes,
        'other_outcomes': other_outcomes,
        'studies': studies,
        'sof_table': sof_table,
        'recent_sessions': recent_sessions,
        'has_outcomes': project.outcomes.exists(),
        'has_assessments': GRADEAssessment.objects.filter(outcome__project=project).exists(),
    }
    
    return render(request, 'grade/project_detail.html', context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_project_list(request):
    """
    API endpoint to list user's projects
    """
    projects = GRADEProject.objects.filter(created_by=request.user).order_by('-created_at')
    
    data = []
    for project in projects:
        data.append({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'population': project.population,
            'intervention': project.intervention,
            'comparison': project.comparison,
            'created_at': project.created_at.isoformat(),
            'outcomes_count': project.outcomes.count(),
            'has_sof_table': hasattr(project, 'sof_table'),
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_project_detail(request, project_id):
    """
    API endpoint to get project details
    """
    project = get_object_or_404(GRADEProject, id=project_id, created_by=request.user)
    
    outcomes_data = []
    for outcome in project.outcomes.all():
        outcome_data = {
            'id': outcome.id,
            'name': outcome.name,
            'description': outcome.description,
            'importance': outcome.importance,
            'outcome_type': outcome.outcome_type,
            'grade_assessment': None,
        }
        
        # Add GRADE assessment if available
        try:
            assessment = outcome.grade_assessment
            outcome_data['grade_assessment'] = {
                'final_certainty': assessment.final_certainty,
                'starting_certainty': assessment.starting_certainty,
                'assessed_at': assessment.assessed_at.isoformat(),
            }
        except GRADEAssessment.DoesNotExist:
            pass
        
        outcomes_data.append(outcome_data)
    
    data = {
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'population': project.population,
        'intervention': project.intervention,
        'comparison': project.comparison,
        'created_at': project.created_at.isoformat(),
        'outcomes': outcomes_data,
        'has_sof_table': hasattr(project, 'sof_table'),
    }
    
    return Response(data)


def home(request):
    """
    Home page view
    """
    if request.user.is_authenticated:
        return redirect('grade:dashboard')
    
    context = {
        'total_projects': GRADEProject.objects.count(),
        'total_assessments': GRADEAssessment.objects.count(),
    }
    
    return render(request, 'grade/home.html', context)
