"""
IBus 配置导出器

负责配置的导入、导出、备份和恢复功能。
"""

import os
import json
import shutil
import zipfile
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum

from .settings_schema import ConfigKeys, validate_config, DEFAULT_CONFIG


class ExportFormat(Enum):
    """导出格式枚举"""
    JSON = 'json'
    GZIP = 'gzip'
    ZIP = 'zip'
    TAR = 'tar'


class BackupError(Exception):
    """备份错误"""
    pass


class ConfigExporter:
    """配置导出器类"""
    
    def __init__(self, config_manager: Optional[Any] = None):
        """
        初始化配置导出器
        
        Args:
            config_manager: ConfigManager 实例（可选）
        """
        self.config_manager = config_manager
        self._backup_dir: Optional[str] = None
        self._init_backup_dir()
        logger = logging.getLogger('ibus-config-exporter')
        logger.info("ConfigExporter initialized")
    
    def _init_backup_dir(self) -> None:
        """初始化备份目录"""
        try:
            home = os.path.expanduser('~')
            backup_path = os.path.join(home, '.config', 'ibus', 'backup')
            self._backup_dir = os.path.join(backup_path, f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(self._backup_dir, exist_ok=True)
            logger = logging.getLogger('ibus-config-exporter')
            logger.info(f"Backup directory initialized: {self._backup_dir}")
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to initialize backup directory: {e}")
    
    # ========== 导出功能 ==========
    
    def export(self, format: ExportFormat = ExportFormat.JSON, filename: Optional[str] = None) -> str:
        """
        导出配置
        
        Args:
            format: 导出格式
            filename: 文件名（可选）
            
        Returns:
            导出文件路径
        """
        try:
            # 获取所有配置
            config = self._get_all_config()
            
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = 'ibus_config'
                filename_map = {
                    ExportFormat.JSON: f'{base_name}_{timestamp}.json',
                    ExportFormat.GZIP: f'{base_name}_{timestamp}.json.gz',
                    ExportFormat.ZIP: f'{base_name}_{timestamp}.zip',
                    ExportFormat.TAR: f'{base_name}_{timestamp}.tar',
                }
                filename = filename_map[format]
            
            # 创建临时文件
            temp_file = f"/tmp/{filename}"
            
            # 根据格式导出
            if format == ExportFormat.JSON:
                self._export_json(config, temp_file)
            elif format == ExportFormat.GZIP:
                self._export_gzip(config, temp_file)
            elif format == ExportFormat.ZIP:
                self._export_zip(config, temp_file)
            elif format == ExportFormat.TAR:
                self._export_tar(config, temp_file)
            else:
                raise BackupError(f"Unsupported format: {format}")
            
            # 复制到备份目录
            backup_file = os.path.join(self._backup_dir, filename)
            shutil.copy(temp_file, backup_file)
            
            # 清理临时文件
            os.remove(temp_file)
            
            logger = logging.getLogger('ibus-config-exporter')
            logger.info(f"Configuration exported to: {backup_file}")
            return backup_file
        
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to export configuration: {e}")
            raise BackupError(f"Export failed: {e}")
    
    def _get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        if self.config_manager:
            return self.config_manager.get_all()
        else:
            return DEFAULT_CONFIG.copy()
    
    def _export_json(self, config: Dict[str, Any], filepath: str) -> None:
        """导出为 JSON 格式"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _export_gzip(self, config: Dict[str, Any], filepath: str) -> None:
        """导出为 GZIP 格式"""
        import gzip
        temp_file = filepath + '.tmp'
        self._export_json(config, temp_file)
        
        with gzip.open(filepath, 'wt', encoding='utf-8') as f:
            with open(temp_file, 'r', encoding='utf-8') as src:
                f.write(src.read())
        
        os.remove(temp_file)
    
    def _export_zip(self, config: Dict[str, Any], filepath: str) -> None:
        """导出为 ZIP 格式"""
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            config_data = json.dumps(config, ensure_ascii=False, indent=2).encode('utf-8')
            zf.writestr('config.json', config_data)
    
    def _export_tar(self, config: Dict[str, Any], filepath: str) -> None:
        """导出为 TAR 格式"""
        import tarfile
        import io
        
        tar = tarfile.open(filepath, 'w:gz')
        config_data = json.dumps(config, ensure_ascii=False, indent=2).encode('utf-8')
        info = tarfile.TarInfo(name='config.json')
        info.size = len(config_data)
        tar.addfile(info, io.BytesIO(config_data))
        tar.close()
    
    # ========== 导入功能 ==========
    
    def import_config(self, filepath: str) -> bool:
        """
        导入配置
        
        Args:
            filepath: 配置文件路径
            
        Returns:
            是否成功
        """
        try:
            logger = logging.getLogger('ibus-config-exporter')
            logger.info(f"Importing configuration from: {filepath}")
            
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return False
            
            # 检测文件类型
            if filepath.endswith('.json'):
                return self._import_json(filepath)
            elif filepath.endswith('.json.gz'):
                return self._import_gzip(filepath)
            elif filepath.endswith('.zip'):
                return self._import_zip(filepath)
            elif filepath.endswith('.tar'):
                return self._import_tar(filepath)
            else:
                logger.error(f"Unsupported file format: {filepath}")
                return False
        
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    def _import_json(self, filepath: str) -> bool:
        """导入 JSON 格式配置"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证并应用配置
            success = True
            for key, value in config.items():
                if not validate_config(key, value):
                    logger = logging.getLogger('ibus-config-exporter')
                    logger.warning(f"Invalid config value: {key} = {value}")
                    success = False
                else:
                    if self.config_manager:
                        self.config_manager.set(key, value)
            
            if self.config_manager:
                self.config_manager.save_all()
            
            logger = logging.getLogger('ibus-config-exporter')
            logger.info(f"Configuration imported successfully: {filepath}")
            return success
        
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to import JSON config: {e}")
            return False
    
    def _import_gzip(self, filepath: str) -> bool:
        """导入 GZIP 格式配置"""
        import gzip
        temp_file = filepath + '.tmp'
        
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                config = json.loads(f.read())
            
            return self._import_json(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def _import_zip(self, filepath: str) -> bool:
        """导入 ZIP 格式配置"""
        import zipfile
        
        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                with zf.open('config.json') as f:
                    config = json.loads(f.read().decode('utf-8'))
            
            return self._import_json('/tmp/temp_config.json')
        finally:
            # 清理临时文件
            if os.path.exists('/tmp/temp_config.json'):
                os.remove('/tmp/temp_config.json')
    
    def _import_tar(self, filepath: str) -> bool:
        """导入 TAR 格式配置"""
        import tarfile
        
        try:
            with tarfile.open(filepath, 'r:gz') as tar:
                with tar.extractfile('config.json') as f:
                    if f:
                        config = json.loads(f.read().decode('utf-8'))
                    
                        # 创建临时文件
                        temp_file = '/tmp/temp_config.json'
                        with open(temp_file, 'w', encoding='utf-8') as tmp:
                            json.dump(config, tmp, ensure_ascii=False, indent=2)
                        
                        return self._import_json(temp_file)
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to import TAR config: {e}")
        
        return False
    
    # ========== 备份功能 ==========
    
    def create_backup(self) -> str:
        """
        创建配置备份
        
        Returns:
            备份文件路径
        """
        logger = logging.getLogger('ibus-config-exporter')
        logger.info("Creating configuration backup...")
        
        try:
            backup_file = os.path.join(self._backup_dir, f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
            config = self._get_all_config()
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Backup created: {backup_file}")
            return backup_file
        
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to create backup: {e}")
            raise BackupError(f"Backup failed: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        列出所有备份
        
        Returns:
            备份信息列表
        """
        try:
            if not self._backup_dir or not os.path.exists(self._backup_dir):
                return []
            
            backups = []
            for filename in os.listdir(self._backup_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self._backup_dir, filename)
                    stat = os.stat(filepath)
                    
                    # 提取时间戳
                    timestamp = filename.replace('backup_', '').replace('.json', '')
                    
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'created': timestamp,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
            
            # 按创建时间排序
            backups.sort(key=lambda x: x['created'], reverse=True)
            
            return backups
        
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        恢复备份
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否成功
        """
        try:
            logger = logging.getLogger('ibus-config-exporter')
            logger.info(f"Restoring backup from: {backup_path}")
            
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # 读取备份
            with open(backup_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置
            validation_result = self._validate_config(config)
            if not validation_result['valid']:
                logger.error(f"Configuration validation failed: {validation_result['errors']}")
                return False
            
            # 应用配置
            if self.config_manager:
                for key, value in config.items():
                    self.config_manager.set(key, value)
                
                self.config_manager.save_all()
                self.config_manager.reload()
            
            logger.info(f"Backup restored successfully: {backup_path}")
            return True
        
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        删除备份
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否成功
        """
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                logger = logging.getLogger('ibus-config-exporter')
                logger.info(f"Backup deleted: {backup_path}")
                return True
            else:
                logger = logging.getLogger('ibus-config-exporter')
                logger.error(f"Backup file not found: {backup_path}")
                return False
        
        except Exception as e:
            logger = logging.getLogger('ibus-config-exporter')
            logger.error(f"Failed to delete backup: {e}")
            return False
    
    # ========== 配置验证 ==========
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证配置
        
        Args:
            config: 配置字典
            
        Returns:
            验证结果
        """
        errors = []
        
        for key, value in config.items():
            if not validate_config(key, value):
                errors.append({
                    'key': key,
                    'value': value,
                    'error': f"Invalid configuration: {key} = {value}"
                })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'config_count': len(config)
        }
    
    # ========== 批量操作 ==========
    
    def export_multiple(self, configs: List[Dict[str, Any]], format: ExportFormat = ExportFormat.JSON) -> List[str]:
        """
        批量导出配置
        
        Args:
            configs: 配置列表
            format: 导出格式
            
        Returns:
            导出文件路径列表
        """
        results = []
        
        for i, config in enumerate(configs):
            filename = f'config_{i}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format.value}'
            filepath = os.path.join(self._backup_dir, filename)
            
            # 创建备份目录如果不存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 导出
            if format == ExportFormat.JSON:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            elif format == ExportFormat.GZIP:
                import gzip
                temp_file = filepath + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                with gzip.open(filepath, 'wt', encoding='utf-8') as gz:
                    with open(temp_file, 'r') as src:
                        gz.write(src.read())
                os.remove(temp_file)
            elif format == ExportFormat.ZIP:
                import zipfile
                with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
                    config_data = json.dumps(config, ensure_ascii=False, indent=2).encode('utf-8')
                    zf.writestr('config.json', config_data)
            
            results.append(filepath)
        
        return results
    
    def get_backup_info(self) -> Dict[str, Any]:
        """
        获取备份信息
        
        Returns:
            备份信息
        """
        backups = self.list_backups()
        
        return {
            'backup_dir': self._backup_dir,
            'backup_count': len(backups),
            'backups': backups,
        }
