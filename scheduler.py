import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import and_
from app import app, db
from models import ScheduledConversion
from routes import perform_conversion
from conversor_sites.config import Settings
import uuid

class ConversionScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        """Inicia o scheduler em uma thread separada"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.thread.start()
            logging.info("Scheduler de conversões iniciado")
    
    def stop(self):
        """Para o scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Scheduler de conversões parado")
    
    def _scheduler_loop(self):
        """Loop principal do scheduler"""
        while self.running:
            try:
                with app.app_context():
                    self._process_scheduled_conversions()
                time.sleep(30)  # Verifica a cada 30 segundos
            except Exception as e:
                logging.error(f"Erro no scheduler: {e}")
                time.sleep(60)  # Espera mais tempo em caso de erro
    
    def _process_scheduled_conversions(self):
        """Processa conversões agendadas que estão prontas para executar"""
        now = datetime.utcnow()
        
        # Busca conversões agendadas que devem executar agora
        scheduled_conversions = ScheduledConversion.query.filter(
            and_(
                ScheduledConversion.status == 'scheduled',
                ScheduledConversion.next_run <= now
            )
        ).all()
        
        for conversion in scheduled_conversions:
            try:
                self._execute_conversion(conversion)
            except Exception as e:
                logging.error(f"Erro ao executar conversão {conversion.id}: {e}")
                conversion.status = 'failed'
                conversion.error_message = str(e)
                conversion.updated_at = datetime.utcnow()
                db.session.commit()
    
    def _execute_conversion(self, conversion: ScheduledConversion):
        """Executa uma conversão agendada"""
        logging.info(f"Executando conversão agendada {conversion.id}: {conversion.name}")
        
        # Atualiza status para running
        conversion.status = 'running'
        conversion.last_run = datetime.utcnow()
        conversion.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Prepara configurações
        settings_dict = conversion.get_settings_dict()
        settings_dict['url'] = conversion.url
        settings = Settings.from_sources(settings_dict)
        
        # Gera ID único para esta execução
        task_id = str(uuid.uuid4())
        
        try:
            # Executa a conversão usando a mesma função do routes.py
            perform_conversion(task_id, conversion.url, settings)
            
            # Verifica o resultado
            from routes import conversion_status
            if task_id in conversion_status:
                result = conversion_status[task_id]
                if result.get('status') == 'completed':
                    conversion.status = 'completed'
                    conversion.result_pdf_path = result.get('pdf_file')
                    conversion.result_html_path = result.get('html_file')
                    conversion.error_message = None
                    logging.info(f"Conversão {conversion.id} concluída com sucesso")
                else:
                    conversion.status = 'failed'
                    conversion.error_message = result.get('message', 'Erro desconhecido')
                    logging.error(f"Conversão {conversion.id} falhou: {conversion.error_message}")
                
                # Remove do status global para limpar memória
                del conversion_status[task_id]
            else:
                conversion.status = 'failed'
                conversion.error_message = 'Resultado não encontrado'
        
        except Exception as e:
            conversion.status = 'failed'
            conversion.error_message = str(e)
            logging.error(f"Erro na execução da conversão {conversion.id}: {e}")
        
        # Calcula próxima execução se for recorrente
        if conversion.frequency != 'once':
            conversion.next_run = self._calculate_next_run(conversion.scheduled_time, conversion.frequency)
            conversion.status = 'scheduled'  # Reagenda para próxima execução
        
        conversion.updated_at = datetime.utcnow()
        db.session.commit()
    
    def _calculate_next_run(self, base_time: datetime, frequency: str) -> datetime:
        """Calcula a próxima execução baseada na frequência"""
        now = datetime.utcnow()
        
        if frequency == 'daily':
            next_run = base_time + timedelta(days=1)
            while next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        elif frequency == 'weekly':
            next_run = base_time + timedelta(weeks=1)
            while next_run <= now:
                next_run += timedelta(weeks=1)
            return next_run
        elif frequency == 'monthly':
            # Aproximação: adiciona 30 dias
            next_run = base_time + timedelta(days=30)
            while next_run <= now:
                next_run += timedelta(days=30)
            return next_run
        
        return base_time

# Instância global do scheduler
scheduler = ConversionScheduler()

def init_scheduler():
    """Inicializa o scheduler quando a aplicação inicia"""
    with app.app_context():
        # Atualiza conversões que estavam rodando para failed (recuperação de crash)
        ScheduledConversion.query.filter_by(status='running').update({
            'status': 'failed',
            'error_message': 'Aplicação reiniciada durante execução',
            'updated_at': datetime.utcnow()
        })
        db.session.commit()
        
        # Recalcula next_run para conversões agendadas
        scheduled_conversions = ScheduledConversion.query.filter_by(status='scheduled').all()
        for conversion in scheduled_conversions:
            if not conversion.next_run or conversion.next_run <= datetime.utcnow():
                if conversion.frequency == 'once':
                    conversion.next_run = conversion.scheduled_time
                else:
                    conversion.next_run = scheduler._calculate_next_run(
                        conversion.scheduled_time, conversion.frequency
                    )
                conversion.updated_at = datetime.utcnow()
        
        db.session.commit()
    
    # Inicia o scheduler
    scheduler.start()