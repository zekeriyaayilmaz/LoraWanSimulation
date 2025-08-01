#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arazi Yönetim Sistemi - Logger
Log yönetimi için yardımcı fonksiyonlar
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

from config import LogConfig

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Logger kurulumu"""
    
    # Log seviyesini belirle
    log_level = level or LogConfig.LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Logger oluştur
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Eğer handler zaten varsa, tekrar ekleme
    if logger.handlers:
        return logger
    
    # Log dizinini oluştur
    log_dir = os.path.dirname(LogConfig.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Dosya handler'ı oluştur
    file_handler = logging.handlers.RotatingFileHandler(
        LogConfig.LOG_FILE,
        maxBytes=LogConfig.MAX_FILE_SIZE * 1024 * 1024,  # MB to bytes
        backupCount=LogConfig.BACKUP_COUNT,
        encoding='utf-8'
    )
    
    # Console handler'ı oluştur
    console_handler = logging.StreamHandler()
    
    # Formatter oluştur
    formatter = logging.Formatter(LogConfig.FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Handler'ları ekle
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Mevcut logger'ı al"""
    return logging.getLogger(name)

def log_sensor_data(logger: logging.Logger, sensor_data: dict):
    """Sensör verisi logla"""
    logger.info(
        f"Sensör {sensor_data['sensor_id']}: "
        f"{sensor_data['value']} {sensor_data['unit']} "
        f"(Kalite: {sensor_data['quality_score']}%, "
        f"Batarya: {sensor_data['battery_level']}%)"
    )

def log_alert(logger: logging.Logger, alert_data: dict):
    """Alarm logla"""
    logger.warning(
        f"ALARM: {alert_data['alert_level'].upper()} - "
        f"{alert_data['message']} "
        f"(Sensör: {alert_data['sensor_id']})"
    )

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Hata logla"""
    logger.error(
        f"HATA {context}: {type(error).__name__}: {str(error)}"
    )

def log_performance(logger: logging.Logger, operation: str, duration: float):
    """Performans logla"""
    logger.info(f"PERFORMANS: {operation} - {duration:.3f}s")

def create_daily_logger(name: str) -> logging.Logger:
    """Günlük log dosyası oluştur"""
    
    # Günlük log dosya adı
    today = datetime.now().strftime('%Y-%m-%d')
    daily_log_file = f"logs/{name}_{today}.log"
    
    # Log dizinini oluştur
    log_dir = os.path.dirname(daily_log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Logger oluştur
    logger = logging.getLogger(f"{name}_daily")
    logger.setLevel(logging.INFO)
    
    # Eğer handler zaten varsa, tekrar ekleme
    if logger.handlers:
        return logger
    
    # Dosya handler'ı oluştur
    file_handler = logging.FileHandler(daily_log_file, encoding='utf-8')
    
    # Formatter oluştur
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Handler'ı ekle
    logger.addHandler(file_handler)
    
    return logger

def log_system_start(logger: logging.Logger):
    """Sistem başlangıç logu"""
    logger.info("🚀 Arazi Yönetim Sistemi başlatılıyor...")
    logger.info(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"⚙️ Log seviyesi: {LogConfig.LEVEL}")

def log_system_stop(logger: logging.Logger):
    """Sistem durdurma logu"""
    logger.info("🛑 Arazi Yönetim Sistemi durduruluyor...")
    logger.info(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def log_database_connection(logger: logging.Logger, success: bool, details: str = ""):
    """Veritabanı bağlantı logu"""
    if success:
        logger.info(f"✅ Veritabanı bağlantısı başarılı {details}")
    else:
        logger.error(f"❌ Veritabanı bağlantısı başarısız {details}")

def log_sensor_activity(logger: logging.Logger, sensor_count: int, data_count: int):
    """Sensör aktivite logu"""
    logger.info(
        f"📊 Sensör aktivitesi: {sensor_count} sensör, "
        f"{data_count} veri kaydı"
    )

def log_scenario_change(logger: logging.Logger, old_scenario: str, new_scenario: str):
    """Senaryo değişikliği logu"""
    logger.info(
        f"🌤️ Senaryo değişikliği: {old_scenario} → {new_scenario}"
    )

def log_configuration(logger: logging.Logger, config_data: dict):
    """Konfigürasyon logu"""
    logger.info("⚙️ Sistem konfigürasyonu:")
    for key, value in config_data.items():
        logger.info(f"   {key}: {value}")

def log_memory_usage(logger: logging.Logger):
    """Bellek kullanımı logla"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        logger.info(f"💾 Bellek kullanımı: {memory_mb:.1f} MB")
    except ImportError:
        logger.debug("psutil kütüphanesi bulunamadı - bellek kullanımı loglanamıyor")

def log_disk_usage(logger: logging.Logger, path: str = "."):
    """Disk kullanımı logla"""
    try:
        import psutil
        disk_usage = psutil.disk_usage(path)
        total_gb = disk_usage.total / 1024 / 1024 / 1024
        used_gb = disk_usage.used / 1024 / 1024 / 1024
        free_gb = disk_usage.free / 1024 / 1024 / 1024
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        logger.info(
            f"💿 Disk kullanımı ({path}): "
            f"{used_gb:.1f}GB / {total_gb:.1f}GB "
            f"({usage_percent:.1f}%) - {free_gb:.1f}GB boş"
        )
    except ImportError:
        logger.debug("psutil kütüphanesi bulunamadı - disk kullanımı loglanamıyor")
    except Exception as e:
        logger.error(f"Disk kullanımı alınamadı: {e}")

def log_network_status(logger: logging.Logger):
    """Ağ durumu logla"""
    try:
        import psutil
        network_stats = psutil.net_io_counters()
        bytes_sent_mb = network_stats.bytes_sent / 1024 / 1024
        bytes_recv_mb = network_stats.bytes_recv / 1024 / 1024
        
        logger.info(
            f"🌐 Ağ trafiği: "
            f"Gönderilen: {bytes_sent_mb:.1f}MB, "
            f"Alınan: {bytes_recv_mb:.1f}MB"
        )
    except ImportError:
        logger.debug("psutil kütüphanesi bulunamadı - ağ durumu loglanamıyor")
    except Exception as e:
        logger.error(f"Ağ durumu alınamadı: {e}")

def log_system_health(logger: logging.Logger):
    """Sistem sağlığı logla"""
    logger.info("🏥 Sistem sağlığı kontrolü:")
    log_memory_usage(logger)
    log_disk_usage(logger)
    log_network_status(logger) 