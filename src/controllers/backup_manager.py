import os
import shutil
from datetime import datetime

class BackupManager:
    def __init__(self, backup_dir='backup'):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, db_path):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'backup_{timestamp}.sqlite')
        
        shutil.copy2(db_path, backup_path)
        
        backup_info = {
            'timestamp': timestamp,
            'path': backup_path,
            'size': os.path.getsize(backup_path)
        }
        
        return backup_info
    
    def list_backups(self):
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('backup_') and filename.endswith('.sqlite'):
                filepath = os.path.join(self.backup_dir, filename)
                timestamp = filename.replace('backup_', '').replace('.sqlite', '')
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'timestamp': timestamp,
                    'size': os.path.getsize(filepath)
                })
        
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    
    def restore_backup(self, backup_path, db_path):
        shutil.copy2(backup_path, db_path)
    
    def clean_old_backups(self, keep_days=30):
        cutoff_date = datetime.now() - datetime.timedelta(days=keep_days)
        
        for backup in self.list_backups():
            backup_date = datetime.strptime(backup['timestamp'], '%Y%m%d_%H%M%S')
            if backup_date < cutoff_date:
                os.remove(backup['path'])
