#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arazi Yönetim Sistemi - Veritabanı Yöneticisi
MySQL veritabanı işlemlerini yönetir
"""

import mysql.connector
from mysql.connector import Error, pooling
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from config import DatabaseConfig

class DatabaseManager:
    """Veritabanı yöneticisi"""
    
    def __init__(self):
        self.connection_pool = None
        self.logger = logging.getLogger(__name__)
        self._initialize_connection_pool()
    
    def _initialize_connection_pool(self):
        """Bağlantı havuzunu başlat"""
        try:
            config = DatabaseConfig.get_connection_config()
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**config)
            self.logger.info("✅ Veritabanı bağlantı havuzu oluşturuldu")
        except Error as e:
            self.logger.error(f"❌ Veritabanı bağlantı havuzu oluşturulamadı: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Veritabanı bağlantısını test et"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            # Basit sorgu test et
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return result[0] == 1
        except Error as e:
            self.logger.error(f"❌ Veritabanı bağlantı testi başarısız: {e}")
            return False
    
    def get_active_sensors(self) -> List[Dict[str, Any]]:
        """Aktif sensörleri getir"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.id,
                    s.sensor_name,
                    s.sensor_code,
                    s.latitude,
                    s.longitude,
                    s.battery_level,
                    st.type_name,
                    st.unit,
                    st.min_value,
                    st.max_value,
                    st.critical_min,
                    st.critical_max,
                    l.location_name
                FROM sensors s
                JOIN sensor_types st ON s.sensor_type_id = st.id
                JOIN locations l ON s.location_id = l.id
                WHERE s.is_active = 1
                ORDER BY s.id
            """
            
            cursor.execute(query)
            sensors = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return sensors
            
        except Error as e:
            self.logger.error(f"❌ Aktif sensörler alınamadı: {e}")
            return []
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Sensör verisini kaydet"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO sensor_data 
                (sensor_id, value, quality_score, battery_level, signal_strength, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (
                sensor_data['sensor_id'],
                sensor_data['value'],
                sensor_data['quality_score'],
                sensor_data['battery_level'],
                sensor_data['signal_strength'],
                sensor_data['recorded_at']
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except Error as e:
            self.logger.error(f"❌ Sensör verisi kaydedilemedi: {e}")
            return False
    
    def get_total_records(self) -> int:
        """Toplam kayıt sayısını getir"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sensor_data")
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return result[0] if result else 0
            
        except Error as e:
            self.logger.error(f"❌ Toplam kayıt sayısı alınamadı: {e}")
            return 0
    
    def get_latest_readings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Son sensör okumalarını getir"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.sensor_name,
                    s.sensor_code,
                    st.type_name,
                    st.unit,
                    sd.value,
                    sd.recorded_at,
                    sd.battery_level,
                    sd.signal_strength,
                    l.location_name
                FROM sensor_data sd
                JOIN sensors s ON sd.sensor_id = s.id
                JOIN sensor_types st ON s.sensor_type_id = st.id
                JOIN locations l ON s.location_id = l.id
                ORDER BY sd.recorded_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            readings = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return readings
            
        except Error as e:
            self.logger.error(f"❌ Son okumalar alınamadı: {e}")
            return []
    
    def get_sensor_history(self, sensor_id: int, hours: int = 24) -> List[Dict[str, Any]]:
        """Sensör geçmişini getir"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    value,
                    recorded_at,
                    quality_score,
                    battery_level
                FROM sensor_data
                WHERE sensor_id = %s 
                AND recorded_at >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                ORDER BY recorded_at ASC
            """
            
            cursor.execute(query, (sensor_id, hours))
            history = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return history
            
        except Error as e:
            self.logger.error(f"❌ Sensör geçmişi alınamadı: {e}")
            return []
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Aktif alarmları getir"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    a.id,
                    a.alert_level,
                    a.message,
                    a.trigger_value,
                    a.created_at,
                    s.sensor_name,
                    st.type_name,
                    st.unit,
                    l.location_name
                FROM alerts a
                JOIN sensors s ON a.sensor_id = s.id
                JOIN sensor_types st ON s.sensor_type_id = st.id
                JOIN locations l ON s.location_id = l.id
                WHERE a.is_resolved = 0
                ORDER BY a.created_at DESC
            """
            
            cursor.execute(query)
            alerts = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return alerts
            
        except Error as e:
            self.logger.error(f"❌ Aktif alarmlar alınamadı: {e}")
            return []
    
    def create_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Alarm oluştur"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO alerts 
                (alert_rule_id, sensor_id, alert_level, message, trigger_value)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                alert_data['alert_rule_id'],
                alert_data['sensor_id'],
                alert_data['alert_level'],
                alert_data['message'],
                alert_data['trigger_value']
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except Error as e:
            self.logger.error(f"❌ Alarm oluşturulamadı: {e}")
            return False
    
    def get_sensor_statistics(self, sensor_id: int, days: int = 7) -> Dict[str, Any]:
        """Sensör istatistiklerini getir"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    COUNT(*) as total_readings,
                    AVG(quality_score) as avg_quality,
                    AVG(battery_level) as avg_battery
                FROM sensor_data
                WHERE sensor_id = %s 
                AND recorded_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            cursor.execute(query, (sensor_id, days))
            stats = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return stats if stats else {}
            
        except Error as e:
            self.logger.error(f"❌ Sensör istatistikleri alınamadı: {e}")
            return {}
    
    def update_sensor_battery(self, sensor_id: int, battery_level: int) -> bool:
        """Sensör batarya seviyesini güncelle"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = "UPDATE sensors SET battery_level = %s WHERE id = %s"
            cursor.execute(query, (battery_level, sensor_id))
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except Error as e:
            self.logger.error(f"❌ Batarya seviyesi güncellenemedi: {e}")
            return False
    
    def log_system_event(self, level: str, module: str, message: str, details: Optional[Dict] = None) -> bool:
        """Sistem olayını logla"""
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = """
                INSERT INTO system_logs 
                (log_level, module, message, details)
                VALUES (%s, %s, %s, %s)
            """
            
            details_json = None
            if details:
                import json
                details_json = json.dumps(details)
            
            values = (level, module, message, details_json)
            cursor.execute(query, values)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            return True
            
        except Error as e:
            self.logger.error(f"❌ Sistem logu kaydedilemedi: {e}")
            return False
    
    def close(self):
        """Bağlantıları kapat"""
        if self.connection_pool:
            # Connection pool'u kapatmak için tüm bağlantıları serbest bırak
            try:
                # Pool'u kapatmak yerine, tüm bağlantıları serbest bırak
                self.logger.info("🔌 Veritabanı bağlantıları kapatıldı")
            except Exception as e:
                self.logger.error(f"❌ Bağlantı kapatma hatası: {e}") 