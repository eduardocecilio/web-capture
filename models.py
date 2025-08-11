from datetime import datetime
import json
from app import db

class ScheduledConversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    
    # Configurações de conversão (JSON)
    settings = db.Column(db.Text, nullable=False, default='{}')
    
    # Agendamento
    scheduled_time = db.Column(db.DateTime, nullable=False)
    frequency = db.Column(db.String(20), default='once')  # once, daily, weekly, monthly
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, running, completed, failed
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    
    # Resultados
    result_pdf_path = db.Column(db.String(500))
    result_html_path = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_settings_dict(self):
        """Retorna as configurações como dicionário"""
        try:
            return json.loads(self.settings) if self.settings else {}
        except json.JSONDecodeError:
            return {}
    
    def set_settings_dict(self, settings_dict):
        """Define as configurações a partir de um dicionário"""
        self.settings = json.dumps(settings_dict)
    
    def to_dict(self):
        """Converte para dicionário para JSON"""
        return {
            'id': self.id,
            'url': self.url,
            'name': self.name,
            'settings': self.get_settings_dict(),
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'frequency': self.frequency,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'result_pdf_path': self.result_pdf_path,
            'result_html_path': self.result_html_path,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }