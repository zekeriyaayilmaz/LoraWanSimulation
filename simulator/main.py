#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arazi Yönetim Sistemi - LoRaWAN Simülatörü
Sensör verilerini simüle eder ve veritabanına kaydeder
"""

import time
import random
import logging
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import schedule
import json
import os
from typing import Dict, List, Optional

# Konfigürasyon
from config import DatabaseConfig, SimulatorConfig
from sensor_simulator import SensorSimulator
from database_manager import DatabaseManager
from logger import setup_logger

class LoRaWANSimulator:
    """LoRaWAN sensör simülatörü ana sınıfı"""
    
    def __init__(self):
        self.logger = setup_logger('lorawan_simulator')
        self.db_manager = DatabaseManager()
        self.sensor_simulator = SensorSimulator()
        self.is_running = False
        
    def start(self):
        """Simülatörü başlat"""
        self.logger.info("🚀 LoRaWAN Simülatörü başlatılıyor...")
        
        try:
            # Veritabanı bağlantısını test et
            if not self.db_manager.test_connection():
                self.logger.error("❌ Veritabanı bağlantısı başarısız!")
                return False
            
            self.logger.info("✅ Veritabanı bağlantısı başarılı")
            
            # Aktif sensörleri al
            sensors = self.db_manager.get_active_sensors()
            if not sensors:
                self.logger.warning("⚠️ Aktif sensör bulunamadı!")
                return False
            
            self.logger.info(f"📡 {len(sensors)} aktif sensör bulundu")
            
            # Zamanlayıcıyı ayarla
            self._setup_scheduler()
            
            # İlk veri gönderimi
            self.generate_and_save_data()
            
            self.is_running = True
            self.logger.info("✅ Simülatör başarıyla başlatıldı")
            
            # Ana döngü
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Simülatör durduruluyor...")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ Hata: {e}")
            self.stop()
    
    def stop(self):
        """Simülatörü durdur"""
        self.is_running = False
        self.db_manager.close()
        self.logger.info("🛑 Simülatör durduruldu")
    
    def _setup_scheduler(self):
        """Zamanlayıcıyı ayarla"""
        # Her 15 dakikada bir veri gönder
        schedule.every(SimulatorConfig.DATA_INTERVAL_MINUTES).minutes.do(
            self.generate_and_save_data
        )
        
        # Her saat başı log
        schedule.every().hour.do(self._log_status)
        
        self.logger.info(f"⏰ Zamanlayıcı ayarlandı: {SimulatorConfig.DATA_INTERVAL_MINUTES} dakika")
    
    def generate_and_save_data(self):
        """Sensör verilerini üret ve kaydet"""
        try:
            # Aktif sensörleri al
            sensors = self.db_manager.get_active_sensors()
            
            for sensor in sensors:
                # Sensör verisi üret
                sensor_data = self.sensor_simulator.generate_sensor_data(sensor)
                
                # Veritabanına kaydet
                success = self.db_manager.save_sensor_data(sensor_data)
                
                if success:
                    self.logger.debug(
                        f"📊 {sensor['sensor_name']}: {sensor_data['value']} {sensor_data['unit']}"
                    )
                else:
                    self.logger.error(f"❌ Veri kaydedilemedi: {sensor['sensor_name']}")
            
            self.logger.info(f"✅ {len(sensors)} sensör verisi üretildi ve kaydedildi")
            
        except Exception as e:
            self.logger.error(f"❌ Veri üretme hatası: {e}")
    
    def _log_status(self):
        """Durum logu"""
        try:
            total_sensors = len(self.db_manager.get_active_sensors())
            total_records = self.db_manager.get_total_records()
            
            self.logger.info(
                f"📈 Durum: {total_sensors} aktif sensör, "
                f"{total_records} toplam kayıt"
            )
        except Exception as e:
            self.logger.error(f"❌ Durum logu hatası: {e}")

def main():
    """Ana fonksiyon"""
    print("🌾 Arazi Yönetim Sistemi - LoRaWAN Simülatörü")
    print("=" * 50)
    
    simulator = LoRaWANSimulator()
    simulator.start()

if __name__ == "__main__":
    main() 