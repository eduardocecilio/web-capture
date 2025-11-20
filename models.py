from datetime import datetime
from app import db


class Conversion(db.Model):
    """Histórico de conversões"""
    __tablename__ = 'conversions'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False)
    title = db.Column(db.String(255))
    status = db.Column(db.String(20), default='completed')  # completed, failed
    blob_url = db.Column(db.String(500))  # URL do PDF no Vercel Blob ou acesso local
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário para JSON"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'status': self.status,
            'blob_url': self.blob_url,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Conversion {self.id}: {self.title}>'

            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'result_pdf_path': self.result_pdf_path,
            'result_html_path': self.result_html_path,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }