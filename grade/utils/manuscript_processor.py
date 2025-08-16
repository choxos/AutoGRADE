"""
Manuscript processing utilities for extracting text from uploaded files
and parsing meta-analysis data.
"""
import os
import re
from typing import Dict, List, Optional, Union
from pathlib import Path

import PyPDF2
from docx import Document
import pandas as pd
from bs4 import BeautifulSoup
import markdown


class ManuscriptProcessor:
    """
    Processes uploaded manuscripts to extract text and identify meta-analysis data
    """
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.docx', '.txt', '.md']
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from various file formats
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif extension == '.docx':
            return self._extract_from_docx(file_path)
        elif extension == '.txt':
            return self._extract_from_txt(file_path)
        elif extension == '.md':
            return self._extract_from_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error extracting from PDF: {str(e)}")
        
        return text.strip()
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting from DOCX: {str(e)}")
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error extracting from TXT: {str(e)}")
    
    def _extract_from_markdown(self, file_path: Path) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                # Convert markdown to HTML then extract text
                html = markdown.markdown(md_content)
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text().strip()
        except Exception as e:
            raise Exception(f"Error extracting from Markdown: {str(e)}")
    
    def identify_meta_analysis_sections(self, text: str) -> Dict[str, str]:
        """
        Identify and extract key sections from a meta-analysis manuscript
        """
        sections = {
            'title': '',
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': '',
            'discussion': '',
            'conclusion': '',
            'references': '',
            'tables': '',
            'figures': ''
        }
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Try to identify sections using common headers
        section_patterns = {
            'abstract': r'(?i)\b(abstract|summary)\b',
            'introduction': r'(?i)\b(introduction|background)\b',
            'methods': r'(?i)\b(methods?|methodology|materials?\s+and\s+methods?)\b',
            'results': r'(?i)\bresults?\b',
            'discussion': r'(?i)\bdiscussion\b',
            'conclusion': r'(?i)\b(conclusion|conclusions)\b',
            'references': r'(?i)\b(references?|bibliography)\b'
        }
        
        lines = text.split('\n')
        current_section = 'introduction'  # Default section
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line) and len(line) < 100:
                    current_section = section_name
                    break
            
            # Add line to current section
            sections[current_section] += line + '\n'
        
        # Try to extract title (usually first non-empty line)
        for line in lines[:20]:  # Check first 20 lines
            line = line.strip()
            if line and len(line) > 10 and not any(word in line.lower() for word in ['page', 'doi', 'journal', 'volume']):
                sections['title'] = line
                break
        
        # Clean up sections
        for key in sections:
            sections[key] = sections[key].strip()
        
        return sections
    
    def extract_statistical_data(self, text: str) -> List[Dict]:
        """
        Extract statistical data that might represent effect estimates
        """
        statistical_data = []
        
        # Common patterns for effect estimates
        patterns = [
            # Risk ratios, odds ratios, hazard ratios
            r'(?i)(RR|OR|HR)\s*[=:]\s*([0-9.]+)(?:\s*\(([0-9.]+)[-–]\s*([0-9.]+)\))?',
            r'(?i)(risk\s+ratio|odds\s+ratio|hazard\s+ratio)\s*[=:]\s*([0-9.]+)(?:\s*\(([0-9.]+)[-–]\s*([0-9.]+)\))?',
            
            # Mean differences
            r'(?i)(MD|mean\s+difference)\s*[=:]\s*([-+]?[0-9.]+)(?:\s*\(([0-9.]+)[-–]\s*([0-9.]+)\))?',
            
            # P-values
            r'(?i)p\s*[=<>]\s*([0-9.]+)',
            
            # Confidence intervals
            r'(?i)95%?\s*CI\s*[=:]\s*\(?([0-9.]+)[-–,]\s*([0-9.]+)\)?',
            r'(?i)\(([0-9.]+)[-–]\s*([0-9.]+)\)',
            
            # Sample sizes
            r'(?i)n\s*[=:]\s*([0-9,]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                data_point = {
                    'pattern': pattern,
                    'match_text': match.group(0),
                    'groups': match.groups(),
                    'position': match.span()
                }
                statistical_data.append(data_point)
        
        return statistical_data
    
    def identify_study_characteristics(self, text: str) -> Dict[str, List[str]]:
        """
        Identify study characteristics like study types, populations, interventions
        """
        characteristics = {
            'study_types': [],
            'populations': [],
            'interventions': [],
            'comparisons': [],
            'outcomes': []
        }
        
        # Study type patterns
        study_type_patterns = [
            r'(?i)randomized\s+controlled\s+trial',
            r'(?i)RCT',
            r'(?i)cohort\s+study',
            r'(?i)case-control\s+study',
            r'(?i)cross-sectional\s+study',
            r'(?i)systematic\s+review',
            r'(?i)meta-analysis'
        ]
        
        for pattern in study_type_patterns:
            matches = re.findall(pattern, text)
            characteristics['study_types'].extend(matches)
        
        # Population patterns (basic extraction)
        population_patterns = [
            r'(?i)patients?\s+with\s+([a-z\s]+?)(?:\.|,|\s+were|\s+who)',
            r'(?i)participants?\s+with\s+([a-z\s]+?)(?:\.|,|\s+were|\s+who)',
            r'(?i)adults?\s+with\s+([a-z\s]+?)(?:\.|,|\s+were|\s+who)',
            r'(?i)children\s+with\s+([a-z\s]+?)(?:\.|,|\s+were|\s+who)',
        ]
        
        for pattern in population_patterns:
            matches = re.findall(pattern, text)
            characteristics['populations'].extend([match.strip() for match in matches])
        
        # Remove duplicates
        for key in characteristics:
            characteristics[key] = list(set(characteristics[key]))
        
        return characteristics
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\b(?:page|p\.)\s*\d+\b', '', text, flags=re.IGNORECASE)
        
        # Remove common PDF artifacts
        text = re.sub(r'\x0c', ' ', text)  # Form feed character
        
        return text.strip()
    
    def extract_tables_and_figures(self, text: str) -> Dict[str, List[str]]:
        """
        Extract table and figure references and content
        """
        extracted = {
            'table_references': [],
            'figure_references': [],
            'table_content': [],
            'figure_content': []
        }
        
        # Table references
        table_refs = re.findall(r'(?i)table\s+(\d+)', text)
        extracted['table_references'] = list(set(table_refs))
        
        # Figure references
        figure_refs = re.findall(r'(?i)figure\s+(\d+)', text)
        extracted['figure_references'] = list(set(figure_refs))
        
        # Try to extract table content (basic)
        table_sections = re.findall(r'(?i)table\s+\d+[^\n]*\n((?:[^\n]*\n)*?)(?=table\s+\d+|figure\s+\d+|$)', text)
        extracted['table_content'] = table_sections
        
        return extracted


class PICOExtractor:
    """
    Extract PICO elements from manuscript text using pattern matching
    """
    
    def extract_pico_elements(self, text: str, sections: Dict[str, str] = None) -> Dict[str, str]:
        """
        Extract PICO elements from manuscript text
        """
        pico = {
            'population': '',
            'intervention': '',
            'comparison': '',
            'outcomes': []
        }
        
        # Focus on abstract and methods sections if available
        search_text = text
        if sections:
            search_text = sections.get('abstract', '') + ' ' + sections.get('methods', '') + ' ' + sections.get('results', '')
        
        # Population extraction
        population_patterns = [
            r'(?i)patients?\s+with\s+([^,.]+)(?:\.|,)',
            r'(?i)participants?\s+with\s+([^,.]+)(?:\.|,)',
            r'(?i)adults?\s+(?:aged\s+\d+[^,.]*)?with\s+([^,.]+)(?:\.|,)',
            r'(?i)children\s+with\s+([^,.]+)(?:\.|,)',
            r'(?i)individuals?\s+with\s+([^,.]+)(?:\.|,)',
        ]
        
        for pattern in population_patterns:
            match = re.search(pattern, search_text)
            if match:
                pico['population'] = match.group(1).strip()
                break
        
        # Intervention extraction
        intervention_patterns = [
            r'(?i)(?:treatment\s+with|intervention\s+of|received)\s+([^,.]+)(?:\.|,)',
            r'(?i)([a-z\s]+)\s+vs\.?\s+',
            r'(?i)([a-z\s]+)\s+versus\s+',
            r'(?i)([a-z\s]+)\s+compared\s+(?:with|to)\s+',
        ]
        
        for pattern in intervention_patterns:
            match = re.search(pattern, search_text)
            if match:
                pico['intervention'] = match.group(1).strip()
                break
        
        # Comparison extraction
        comparison_patterns = [
            r'(?i)vs\.?\s+([^,.]+)(?:\.|,)',
            r'(?i)versus\s+([^,.]+)(?:\.|,)',
            r'(?i)compared\s+(?:with|to)\s+([^,.]+)(?:\.|,)',
            r'(?i)control\s+group\s+received\s+([^,.]+)(?:\.|,)',
            r'(?i)placebo(?:\s+group)?',
        ]
        
        for pattern in comparison_patterns:
            match = re.search(pattern, search_text)
            if match:
                if 'placebo' in pattern:
                    pico['comparison'] = 'placebo'
                else:
                    pico['comparison'] = match.group(1).strip()
                break
        
        # Outcomes extraction
        outcome_patterns = [
            r'(?i)primary\s+outcome[s]?\s*[:\-]?\s*([^.]+)\.',
            r'(?i)secondary\s+outcome[s]?\s*[:\-]?\s*([^.]+)\.',
            r'(?i)outcome[s]?\s+(?:measured|assessed|evaluated)\s+([^.]+)\.',
            r'(?i)endpoints?\s*[:\-]?\s*([^.]+)\.',
        ]
        
        for pattern in outcome_patterns:
            matches = re.findall(pattern, search_text)
            pico['outcomes'].extend([match.strip() for match in matches])
        
        # Remove duplicates from outcomes
        pico['outcomes'] = list(set(pico['outcomes']))
        
        return pico
