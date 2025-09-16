"""Gerador de relatórios consolidados.

Este módulo contém a classe ReportGenerator que combina dados de diferentes
analisadores e gera relatórios consolidados.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ReportGenerator:
    """Gerador de relatórios consolidados.
    
    Args:
        config (dict, optional): Configurações personalizadas
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def calculate_quality_score(
        self, 
        violations: Dict, 
        templates: Dict, 
        errors: Dict
    ) -> int:
        """Calcula o score de qualidade do código (0-100).
        
        Args:
            violations (dict): Dados de violações
            templates (dict): Dados de templates
            errors (dict): Dados de erros
            
        Returns:
            int: Score de qualidade entre 0 e 100
        """
        score = 100
        
        # Penaliza violações de alta prioridade
        high_violations = violations.get('statistics', {}).get('high_priority', 0)
        score -= high_violations * 10
        
        # Penaliza erros
        total_errors = errors.get('metadata', {}).get('total_errors', 0)
        score -= total_errors * 2
        
        # Penaliza templates com muito CSS/JS inline
        high_templates = templates.get('statistics', {}).get('high_priority', 0)
        score -= high_templates * 5
        
        # Garante que o score não seja negativo
        return max(0, score)
    
    def generate_summary(self, violations: Dict, templates: Dict, errors: Dict) -> Dict:
        """Gera resumo executivo dos dados.
        
        Args:
            violations (dict): Dados de violações
            templates (dict): Dados de templates
            errors (dict): Dados de erros
            
        Returns:
            dict: Resumo executivo
        """
        v_stats = violations.get('statistics', {})
        t_stats = templates.get('statistics', {})
        e_stats = errors.get('statistics', {})
        
        return {
            'quality_score': self.calculate_quality_score(violations, templates, errors),
            'total_files': v_stats.get('total_files', 0),
            'violation_files': v_stats.get('violation_files', 0),
            'total_templates': t_stats.get('total_templates', 0),
            'total_errors': errors.get('metadata', {}).get('total_errors', 0),
            'high_priority_issues': (
                v_stats.get('high_priority', 0) + 
                t_stats.get('high_priority', 0) + 
                e_stats.get('high_priority', 0)
            ),
            'total_css_chars': t_stats.get('total_css_chars', 0),
            'total_js_chars': t_stats.get('total_js_chars', 0)
        }
    
    def generate_priorities(self, violations: Dict, templates: Dict, errors: Dict) -> list:
        """Gera lista de prioridades de ação.
        
        Args:
            violations (dict): Dados de violações
            templates (dict): Dados de templates
            errors (dict): Dados de erros
            
        Returns:
            list: Lista de prioridades ordenadas
        """
        priorities = []
        
        # Violações de alta prioridade
        high_violations = violations.get('statistics', {}).get('high_priority', 0)
        if high_violations > 0:
            priorities.append({
                'type': 'violations',
                'priority': 'high',
                'count': high_violations,
                'title': 'Violações de Alta Prioridade',
                'description': 'Arquivos com funções/classes muito grandes que precisam de refatoração urgente'
            })
        
        # Erros do Ruff
        total_errors = errors.get('metadata', {}).get('total_errors', 0)
        if total_errors > 0:
            priorities.append({
                'type': 'errors',
                'priority': 'high',
                'count': total_errors,
                'title': 'Erros do Ruff',
                'description': 'Problemas de sintaxe e estilo que devem ser corrigidos'
            })
        
        # Templates com muito CSS/JS
        high_templates = templates.get('statistics', {}).get('high_priority', 0)
        if high_templates > 0:
            priorities.append({
                'type': 'templates',
                'priority': 'medium',
                'count': high_templates,
                'title': 'Templates com Muito CSS/JS Inline',
                'description': 'Templates que precisam extrair código para arquivos externos'
            })
        
        # Ordena por prioridade e quantidade
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        priorities.sort(
            key=lambda x: (priority_order.get(x['priority'], 0), x['count']), 
            reverse=True
        )
        
        return priorities
    
    def generate_full_report(
        self, 
        violations: Dict, 
        templates: Dict, 
        errors: Dict,
        output_dir: Optional[str] = None
    ) -> Dict:
        """Gera relatório completo consolidado.
        
        Args:
            violations (dict): Dados de violações
            templates (dict): Dados de templates
            errors (dict): Dados de erros
            output_dir (str, optional): Diretório para salvar arquivos
            
        Returns:
            dict: Relatório completo
        """
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'CodeHealthAnalyzer v1.0.0'
            },
            'summary': self.generate_summary(violations, templates, errors),
            'priorities': self.generate_priorities(violations, templates, errors),
            'violations': violations,
            'templates': templates,
            'errors': errors
        }
        
        # Salva arquivos individuais se diretório especificado
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Salva relatórios individuais
            self._save_json(violations, output_path / 'violations_report.json')
            self._save_json(templates, output_path / 'templates_report.json')
            self._save_json(errors, output_path / 'errors_report.json')
            
            # Salva relatório consolidado
            self._save_json(report, output_path / 'full_report.json')
        
        return report
    
    def _save_json(self, data: Dict, file_path: Path):
        """Salva dados em arquivo JSON.
        
        Args:
            data (dict): Dados para salvar
            file_path (Path): Caminho do arquivo
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def generate_html_report(self, report: Dict, output_file: str):
        """Gera relatório em formato HTML.
        
        Args:
            report (dict): Relatório completo
            output_file (str): Caminho do arquivo HTML
        """
        summary = report['summary']
        priorities = report['priorities']
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Qualidade de Código</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
        .score {{ font-size: 3em; font-weight: bold; text-align: center; }}
        .score.good {{ color: #27ae60; }}
        .score.medium {{ color: #f39c12; }}
        .score.poor {{ color: #e74c3c; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .card {{ background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }}
        .priorities {{ margin: 20px 0; }}
        .priority {{ background: #fff; border-left: 4px solid #3498db; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .priority.high {{ border-left-color: #e74c3c; }}
        .priority.medium {{ border-left-color: #f39c12; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Relatório de Qualidade de Código</h1>
        <p>Gerado em: {report['metadata']['generated_at']}</p>
    </div>
    
    <div class="score {'good' if summary['quality_score'] >= 80 else 'medium' if summary['quality_score'] >= 60 else 'poor'}">
        Score: {summary['quality_score']}/100
    </div>
    
    <div class="summary">
        <div class="card">
            <h3>{summary['total_files']}</h3>
            <p>Arquivos Analisados</p>
        </div>
        <div class="card">
            <h3>{summary['violation_files']}</h3>
            <p>Arquivos com Violações</p>
        </div>
        <div class="card">
            <h3>{summary['total_templates']}</h3>
            <p>Templates</p>
        </div>
        <div class="card">
            <h3>{summary['total_errors']}</h3>
            <p>Erros Ruff</p>
        </div>
    </div>
    
    <h2>🎯 Prioridades de Ação</h2>
    <div class="priorities">
"""
        
        if not priorities:
            html_content += """
        <div class="priority">
            <h3>✅ Excelente!</h3>
            <p>Nenhuma ação urgente necessária. Seu código está em boa forma.</p>
        </div>
"""
        else:
            for priority in priorities:
                html_content += f"""
        <div class="priority {priority['priority']}">
            <h3>{priority['title']} ({priority['count']})</h3>
            <p>{priority['description']}</p>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)