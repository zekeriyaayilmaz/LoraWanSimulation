#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arazi Yönetim Sistemi - Simülatör Test
"""

import sys
import os

# Simulator dizinini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Import testleri"""
    try:
        from config import DatabaseConfig, SimulatorConfig
        print("✅ Config import başarılı")
        
        from sensor_simulator import SensorSimulator
        print("✅ SensorSimulator import başarılı")
        
        from database_manager import DatabaseManager
        print("✅ DatabaseManager import başarılı")
        
        from logger import setup_logger
        print("✅ Logger import başarılı")
        
        return True
    except Exception as e:
        print(f"❌ Import hatası: {e}")
        return False

def test_sensor_simulator():
    """Sensör simülatör testi"""
    try:
        from sensor_simulator import SensorSimulator
        
        # Test sensör verisi
        test_sensor = {
            'id': 1,
            'type_name': 'soil_moisture',
            'sensor_name': 'Test Sensör',
            'sensor_code': 'TEST001'
        }
        
        simulator = SensorSimulator()
        sensor_data = simulator.generate_sensor_data(test_sensor)
        
        print(f"✅ Sensör verisi üretildi: {sensor_data['value']} {sensor_data['unit']}")
        return True
    except Exception as e:
        print(f"❌ Sensör simülatör hatası: {e}")
        return False

def test_database_connection():
    """Veritabanı bağlantı testi"""
    try:
        from database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        success = db_manager.test_connection()
        
        if success:
            print("✅ Veritabanı bağlantısı başarılı")
            
            # Aktif sensörleri test et
            sensors = db_manager.get_active_sensors()
            print(f"✅ {len(sensors)} aktif sensör bulundu")
            
            # Bağlantıyı kapat
            try:
                db_manager.close()
            except Exception as e:
                print(f"⚠️ Bağlantı kapatma uyarısı: {e}")
            
            return True
        else:
            print("❌ Veritabanı bağlantısı başarısız")
            return False
    except Exception as e:
        print(f"❌ Veritabanı test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 Arazi Yönetim Sistemi - Simülatör Test")
    print("=" * 50)
    
    # Import testleri
    if not test_imports():
        return
    
    # Sensör simülatör testi
    if not test_sensor_simulator():
        return
    
    # Veritabanı testi
    if not test_database_connection():
        return
    
    print("\n🎉 Tüm testler başarılı! Simülatör çalıştırılabilir.")

if __name__ == "__main__":
    main() 