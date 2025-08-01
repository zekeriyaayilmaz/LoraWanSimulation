#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arazi Yönetim Sistemi - Konfigürasyon
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """Veritabanı konfigürasyonu"""
    
    # Veritabanı bağlantı bilgileri
    HOST = 'localhost'
    PORT = 3306
    DATABASE = 'arazi_yonetim_sistemi'
    USERNAME = 'root'
    PASSWORD = ''  # XAMPP'ta varsayılan olarak boş
    
    # Bağlantı ayarları
    CHARSET = 'utf8mb4'
    COLLATION = 'utf8mb4_unicode_ci'
    
    # Pool ayarları
    POOL_SIZE = 5
    POOL_RESET_SESSION = True
    
    @classmethod
    def get_connection_config(cls) -> Dict[str, Any]:
        """Veritabanı bağlantı konfigürasyonunu döndür"""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'database': cls.DATABASE,
            'user': cls.USERNAME,
            'password': cls.PASSWORD,
            'charset': cls.CHARSET,
            'collation': cls.COLLATION,
            'pool_size': cls.POOL_SIZE,
            'pool_reset_session': cls.POOL_RESET_SESSION,
            'autocommit': True,
            'raise_on_warnings': True
        }

class SimulatorConfig:
    """Simülatör konfigürasyonu"""
    
    # Veri gönderim aralığı (dakika)
    DATA_INTERVAL_MINUTES = 15
    
    # Simülasyon ayarları
    ENABLE_RANDOM_VARIATIONS = True
    ENABLE_SEASONAL_CHANGES = True
    ENABLE_WEATHER_EFFECTS = True
    
    # Sensör veri aralıkları
    SENSOR_RANGES = {
        'soil_moisture': {
            'min': 15,
            'max': 85,
            'critical_min': 25,
            'critical_max': 85,
            'unit': '%',
            'variation': 5  # ±5% rastgele değişim
        },
        'soil_ph': {
            'min': 5.0,
            'max': 8.0,
            'critical_min': 5.5,
            'critical_max': 7.5,
            'unit': 'pH',
            'variation': 0.3
        },
        'air_temperature': {
            'min': 5,
            'max': 35,
            'critical_min': 2,
            'critical_max': 40,
            'unit': '°C',
            'variation': 3
        },
        'air_humidity': {
            'min': 30,
            'max': 90,
            'critical_min': 20,
            'critical_max': 95,
            'unit': '%',
            'variation': 8
        },
        'light_intensity': {
            'min': 1000,
            'max': 80000,
            'critical_min': 500,
            'critical_max': 90000,
            'unit': 'lux',
            'variation': 5000
        },
        'rainfall': {
            'min': 0,
            'max': 25,
            'critical_min': 0,
            'critical_max': 50,
            'unit': 'mm',
            'variation': 2
        },
        'wind_speed': {
            'min': 0,
            'max': 80,
            'critical_min': 3.6,
            'critical_max': 36,
            'unit': 'km/h',
            'variation': 3
        }
    }
    
    # Simülasyon senaryoları (olasılık dağılımı)
    SCENARIOS = {
        'normal': 0.75,      # %75 normal koşullar
        'drought': 0.10,     # %10 kuraklık
        'rainy': 0.10,       # %10 yağışlı
        'extreme_temp': 0.05 # %5 aşırı sıcaklık
    }
    
    # Zaman bazlı değişimler
    TIME_EFFECTS = {
        'hourly': {
            'temperature': {
                'min_hour': 6,   # En düşük sıcaklık saati
                'max_hour': 14,  # En yüksek sıcaklık saati
                'variation': 8   # Günlük sıcaklık değişimi (°C)
            },
            'light': {
                'sunrise_hour': 6,
                'sunset_hour': 18,
                'max_intensity': 80000
            }
        },
        'seasonal': {
            'spring': {'months': [3, 4, 5], 'temp_modifier': 0},
            'summer': {'months': [6, 7, 8], 'temp_modifier': 8},
            'autumn': {'months': [9, 10, 11], 'temp_modifier': 2},
            'winter': {'months': [12, 1, 2], 'temp_modifier': -5}
        }
    }

class LogConfig:
    """Log konfigürasyonu"""
    
    # Log seviyesi
    LEVEL = 'INFO'
    
    # Log dosyası
    LOG_FILE = '../logs/simulator.log'
    
    # Log formatı
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Maksimum dosya boyutu (MB)
    MAX_FILE_SIZE = 10
    
    # Yedek dosya sayısı
    BACKUP_COUNT = 5

class AlertConfig:
    """Alarm konfigürasyonu"""
    
    # Alarm kontrol aralığı (dakika)
    CHECK_INTERVAL_MINUTES = 5
    
    # Email ayarları
    EMAIL_ENABLED = False
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_FROM = 'alerts@arazi-yonetim.com'
    EMAIL_TO = 'admin@example.com'
    
    # SMS ayarları
    SMS_ENABLED = False
    SMS_PROVIDER = 'twilio'
    SMS_FROM = '+1234567890'
    SMS_TO = '+905551234567'

# Ortam değişkenlerinden konfigürasyon yükleme
def load_from_env():
    """Ortam değişkenlerinden konfigürasyon yükle"""
    
    # Veritabanı ayarları
    if os.getenv('DB_HOST'):
        DatabaseConfig.HOST = os.getenv('DB_HOST')
    if os.getenv('DB_PORT'):
        DatabaseConfig.PORT = int(os.getenv('DB_PORT'))
    if os.getenv('DB_NAME'):
        DatabaseConfig.DATABASE = os.getenv('DB_NAME')
    if os.getenv('DB_USER'):
        DatabaseConfig.USERNAME = os.getenv('DB_USER')
    if os.getenv('DB_PASS'):
        DatabaseConfig.PASSWORD = os.getenv('DB_PASS')
    
    # Simülatör ayarları
    if os.getenv('SIM_INTERVAL'):
        SimulatorConfig.DATA_INTERVAL_MINUTES = int(os.getenv('SIM_INTERVAL'))
    
    # Log ayarları
    if os.getenv('LOG_LEVEL'):
        LogConfig.LEVEL = os.getenv('LOG_LEVEL')

# Konfigürasyonu yükle
load_from_env() 