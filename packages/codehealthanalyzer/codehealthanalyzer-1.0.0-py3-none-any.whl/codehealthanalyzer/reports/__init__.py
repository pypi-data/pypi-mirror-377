"""Módulo de geração de relatórios.

Contém classes para gerar relatórios em diferentes formatos (JSON, HTML, Markdown)
e calcular métricas de qualidade de código.
"""

from .generator import ReportGenerator
from .formatter import ReportFormatter

__all__ = ['ReportGenerator', 'ReportFormatter']