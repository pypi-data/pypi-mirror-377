"""Formatador de relatórios em diferentes formatos.

Este módulo contém a classe ReportFormatter que converte dados de relatórios
em diferentes formatos de saída (JSON, Markdown, CSV, etc.).
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ReportFormatter:
    """Formatador de relatórios.
    
    Args:
        config (dict, optional): Configurações de formatação
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def to_json(self, data: Dict, output_file: str = None) -> str:
        """Converte dados para formato JSON.
        
        Args:
            data (dict): Dados para converter
            output_file (str, optional): Arquivo de saída
            
        Returns:
            str: JSON formatado
        """
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str
    
    def to_markdown(self, data: Dict, output_file: str = None) -> str:
        """Converte dados para formato Markdown.
        
        Args:
            data (dict): Dados para converter
            output_file (str, optional): Arquivo de saída
            
        Returns:
            str: Markdown formatado
        """
        md_content = self._generate_markdown(data)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        return md_content
    
    def to_csv(self, data: Dict, output_file: str) -> None:
        """Converte dados para formato CSV.
        
        Args:
            data (dict): Dados para converter
            output_file (str): Arquivo de saída CSV
        """
        # Extrai dados tabulares dos relatórios
        rows = self._extract_tabular_data(data)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    
    def _generate_markdown(self, data: Dict) -> str:
        """Gera conteúdo Markdown a partir dos dados."""
        md = "# 📊 Relatório de Qualidade de Código\n\n"
        
        # Metadata
        if 'metadata' in data:
            md += f"**Gerado em:** {data['metadata'].get('generated_at', 'N/A')}\n\n"
        
        # Summary
        if 'summary' in data:
            summary = data['summary']
            md += "## 📈 Resumo Executivo\n\n"
            md += f"- **Score de Qualidade:** {summary.get('quality_score', 0)}/100\n"
            md += f"- **Arquivos Analisados:** {summary.get('total_files', 0)}\n"
            md += f"- **Arquivos com Violações:** {summary.get('violation_files', 0)}\n"
            md += f"- **Templates:** {summary.get('total_templates', 0)}\n"
            md += f"- **Erros Ruff:** {summary.get('total_errors', 0)}\n"
            md += f"- **Issues de Alta Prioridade:** {summary.get('high_priority_issues', 0)}\n\n"
        
        # Priorities
        if 'priorities' in data and data['priorities']:
            md += "## 🎯 Prioridades de Ação\n\n"
            for priority in data['priorities']:
                icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority.get('priority', 'low'), '⚪')
                md += f"### {icon} {priority.get('title', 'N/A')} ({priority.get('count', 0)})\n\n"
                md += f"{priority.get('description', 'N/A')}\n\n"
        
        # Violations
        if 'violations' in data and data['violations'].get('violations'):
            md += "## 🚨 Violações de Tamanho\n\n"
            for violation in data['violations']['violations'][:10]:  # Top 10
                md += f"### {violation.get('file', 'N/A')}\n\n"
                md += f"- **Tipo:** {violation.get('type', 'N/A')}\n"
                md += f"- **Linhas:** {violation.get('lines', 0)}\n"
                md += f"- **Prioridade:** {violation.get('priority', 'N/A')}\n"
                md += f"- **Categoria:** {violation.get('category', 'N/A')}\n"
                if violation.get('violations'):
                    md += "- **Violações:**\n"
                    for v in violation['violations']:
                        md += f"  - {v}\n"
                md += "\n"
        
        # Templates
        if 'templates' in data and data['templates'].get('templates'):
            md += "## 🎨 Templates com CSS/JS Inline\n\n"
            for template in data['templates']['templates'][:10]:  # Top 10
                md += f"### {template.get('file', 'N/A')}\n\n"
                md += f"- **CSS:** {template.get('css', 0)} caracteres\n"
                md += f"- **JavaScript:** {template.get('js', 0)} caracteres\n"
                md += f"- **Prioridade:** {template.get('priority', 'N/A')}\n"
                md += f"- **Categoria:** {template.get('category', 'N/A')}\n"
                if template.get('recommendations'):
                    md += "- **Recomendações:**\n"
                    for rec in template['recommendations']:
                        md += f"  - {rec}\n"
                md += "\n"
        
        # Errors
        if 'errors' in data and data['errors'].get('errors'):
            md += "## ⚠️ Erros do Ruff\n\n"
            for error_file in data['errors']['errors'][:10]:  # Top 10
                md += f"### {error_file.get('file', 'N/A')}\n\n"
                md += f"- **Total de Erros:** {error_file.get('error_count', 0)}\n"
                md += f"- **Prioridade:** {error_file.get('priority', 'N/A')}\n"
                md += f"- **Categoria:** {error_file.get('category', 'N/A')}\n"
                if error_file.get('errors'):
                    md += "- **Erros:**\n"
                    for err in error_file['errors'][:5]:  # Top 5 erros por arquivo
                        md += f"  - Linha {err.get('line', 0)}: `{err.get('code', 'N/A')}` - {err.get('message', 'N/A')}\n"
                md += "\n"
        
        return md
    
    def _extract_tabular_data(self, data: Dict) -> List[Dict]:
        """Extrai dados em formato tabular para CSV."""
        rows = []
        
        # Adiciona violações
        if 'violations' in data and data['violations'].get('violations'):
            for violation in data['violations']['violations']:
                rows.append({
                    'type': 'violation',
                    'file': violation.get('file', ''),
                    'category': violation.get('category', ''),
                    'priority': violation.get('priority', ''),
                    'lines': violation.get('lines', 0),
                    'details': '; '.join(violation.get('violations', []))
                })
        
        # Adiciona templates
        if 'templates' in data and data['templates'].get('templates'):
            for template in data['templates']['templates']:
                rows.append({
                    'type': 'template',
                    'file': template.get('file', ''),
                    'category': template.get('category', ''),
                    'priority': template.get('priority', ''),
                    'css_chars': template.get('css', 0),
                    'js_chars': template.get('js', 0),
                    'details': '; '.join(template.get('recommendations', []))
                })
        
        # Adiciona erros
        if 'errors' in data and data['errors'].get('errors'):
            for error_file in data['errors']['errors']:
                for error in error_file.get('errors', []):
                    rows.append({
                        'type': 'error',
                        'file': error_file.get('file', ''),
                        'category': error_file.get('category', ''),
                        'priority': error_file.get('priority', ''),
                        'line': error.get('line', 0),
                        'code': error.get('code', ''),
                        'message': error.get('message', '')
                    })
        
        return rows
    
    def generate_summary_table(self, data: Dict) -> str:
        """Gera tabela resumo em formato texto.
        
        Args:
            data (dict): Dados do relatório
            
        Returns:
            str: Tabela formatada
        """
        if 'summary' not in data:
            return "Dados de resumo não disponíveis."
        
        summary = data['summary']
        
        table = """
┌─────────────────────────────┬─────────┐
│ Métrica                     │ Valor   │
├─────────────────────────────┼─────────┤
│ Score de Qualidade          │ {score:>7} │
│ Arquivos Analisados         │ {files:>7} │
│ Arquivos com Violações      │ {violations:>7} │
│ Templates                   │ {templates:>7} │
│ Erros Ruff                  │ {errors:>7} │
│ Issues de Alta Prioridade   │ {high:>7} │
│ CSS Inline (chars)          │ {css:>7} │
│ JavaScript Inline (chars)   │ {js:>7} │
└─────────────────────────────┴─────────┘
""".format(
            score=f"{summary.get('quality_score', 0)}/100",
            files=summary.get('total_files', 0),
            violations=summary.get('violation_files', 0),
            templates=summary.get('total_templates', 0),
            errors=summary.get('total_errors', 0),
            high=summary.get('high_priority_issues', 0),
            css=f"{summary.get('total_css_chars', 0):,}",
            js=f"{summary.get('total_js_chars', 0):,}"
        )
        
        return table