#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arazi Yönetim Sistemi - Sensör Simülatörü
Gerçekçi sensör verileri üretir
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from config import SimulatorConfig

class SensorSimulator:
    """Sensör veri simülatörü"""
    
    def __init__(self):
        self.current_scenario = 'normal'
        self.last_values = {}  # Son değerleri sakla
        self.trend_direction = {}  # Trend yönü
        
    def generate_sensor_data(self, sensor: Dict[str, Any]) -> Dict[str, Any]:
        """Sensör verisi üret"""
        
        sensor_type = sensor['type_name']
        sensor_id = sensor['id']
        
        # Senaryo seç
        self._select_scenario()
        
        # Temel değer üret
        base_value = self._generate_base_value(sensor_type)
        
        # Zaman etkilerini uygula
        time_adjusted_value = self._apply_time_effects(sensor_type, base_value)
        
        # Trend ve korelasyon uygula
        trend_adjusted_value = self._apply_trends(sensor_type, time_adjusted_value, sensor_id)
        
        # Rastgele değişim ekle
        final_value = self._add_random_variation(sensor_type, trend_adjusted_value)
        
        # Sınırlar içinde tut
        final_value = self._clamp_value(sensor_type, final_value)
        
        # Son değeri sakla
        self.last_values[sensor_id] = final_value
        
        # Sensör durumu hesapla
        sensor_status = self._calculate_sensor_status(sensor_type, final_value)
        
        return {
            'sensor_id': sensor_id,
            'value': round(final_value, 3),
            'unit': SimulatorConfig.SENSOR_RANGES[sensor_type]['unit'],
            'quality_score': self._calculate_quality_score(),
            'battery_level': self._simulate_battery_level(sensor_id),
            'signal_strength': self._simulate_signal_strength(),
            'recorded_at': datetime.now(),
            'status': sensor_status
        }
    
    def _select_scenario(self):
        """Simülasyon senaryosu seç"""
        rand = random.random()
        cumulative = 0
        
        for scenario, probability in SimulatorConfig.SCENARIOS.items():
            cumulative += probability
            if rand <= cumulative:
                self.current_scenario = scenario
                break
    
    def _generate_base_value(self, sensor_type: str) -> float:
        """Temel sensör değeri üret"""
        ranges = SimulatorConfig.SENSOR_RANGES[sensor_type]
        
        if self.current_scenario == 'normal':
            # Normal dağılım
            mean = (ranges['min'] + ranges['max']) / 2
            std = (ranges['max'] - ranges['min']) / 6
            return random.gauss(mean, std)
            
        elif self.current_scenario == 'drought':
            # Kuraklık - nem düşük, sıcaklık yüksek
            if sensor_type == 'soil_moisture':
                return random.uniform(ranges['min'], ranges['min'] + 10)
            elif sensor_type == 'air_temperature':
                return random.uniform(ranges['max'] - 5, ranges['max'])
            else:
                # Normal dağılım döndür
                mean = (ranges['min'] + ranges['max']) / 2
                std = (ranges['max'] - ranges['min']) / 6
                return random.gauss(mean, std)
                
        elif self.current_scenario == 'rainy':
            # Yağışlı - nem yüksek, sıcaklık düşük
            if sensor_type == 'soil_moisture':
                return random.uniform(ranges['max'] - 10, ranges['max'])
            elif sensor_type == 'air_temperature':
                return random.uniform(ranges['min'], ranges['min'] + 5)
            elif sensor_type == 'rainfall':
                return random.uniform(5, ranges['max'])
            else:
                # Normal dağılım döndür
                mean = (ranges['min'] + ranges['max']) / 2
                std = (ranges['max'] - ranges['min']) / 6
                return random.gauss(mean, std)
                
        elif self.current_scenario == 'extreme_temp':
            # Aşırı sıcaklık
            if sensor_type == 'air_temperature':
                return random.uniform(ranges['max'] - 2, ranges['max'] + 5)
            elif sensor_type == 'soil_moisture':
                return random.uniform(ranges['min'], ranges['min'] + 15)
            else:
                # Normal dağılım döndür
                mean = (ranges['min'] + ranges['max']) / 2
                std = (ranges['max'] - ranges['min']) / 6
                return random.gauss(mean, std)
        
        return random.uniform(ranges['min'], ranges['max'])
    
    def _apply_time_effects(self, sensor_type: str, base_value: float) -> float:
        """Zaman etkilerini uygula"""
        now = datetime.now()
        hour = now.hour
        month = now.month
        
        # Saatlik etkiler
        if sensor_type == 'air_temperature':
            temp_effects = SimulatorConfig.TIME_EFFECTS['hourly']['temperature']
            min_hour = temp_effects['min_hour']
            max_hour = temp_effects['max_hour']
            variation = temp_effects['variation']
            
            # Günlük sıcaklık döngüsü
            if min_hour <= hour <= max_hour:
                # Gündüz - sıcaklık artıyor
                progress = (hour - min_hour) / (max_hour - min_hour)
                temp_modifier = math.sin(progress * math.pi) * variation / 2
            else:
                # Gece - sıcaklık düşüyor
                if hour < min_hour:
                    progress = hour / min_hour
                else:
                    progress = (hour - max_hour) / (24 - max_hour)
                temp_modifier = -math.cos(progress * math.pi) * variation / 2
            
            base_value += temp_modifier
            
        elif sensor_type == 'light_intensity':
            light_effects = SimulatorConfig.TIME_EFFECTS['hourly']['light']
            sunrise = light_effects['sunrise_hour']
            sunset = light_effects['sunset_hour']
            max_intensity = light_effects['max_intensity']
            
            if sunrise <= hour <= sunset:
                # Gündüz - ışık var
                if hour <= (sunrise + sunset) / 2:
                    # Sabah - ışık artıyor
                    progress = (hour - sunrise) / ((sunrise + sunset) / 2 - sunrise)
                else:
                    # Öğleden sonra - ışık azalıyor
                    progress = 1 - (hour - (sunrise + sunset) / 2) / (sunset - (sunrise + sunset) / 2)
                
                intensity = math.sin(progress * math.pi) * max_intensity
                base_value = max(base_value, intensity)
            else:
                # Gece - çok az ışık
                base_value = random.uniform(0, 100)
        
        # Mevsimsel etkiler
        for season, config in SimulatorConfig.TIME_EFFECTS['seasonal'].items():
            if month in config['months']:
                if sensor_type == 'air_temperature':
                    base_value += config['temp_modifier']
                break
        
        return base_value
    
    def _apply_trends(self, sensor_type: str, value: float, sensor_id: int) -> float:
        """Trend ve korelasyon uygula"""
        
        # Trend yönünü belirle (eğer yoksa)
        if sensor_id not in self.trend_direction:
            self.trend_direction[sensor_id] = random.choice([-1, 1])
        
        # Son değerle karşılaştır
        if sensor_id in self.last_values:
            last_value = self.last_values[sensor_id]
            difference = value - last_value
            
            # Trend devam ediyor mu kontrol et
            if (difference > 0 and self.trend_direction[sensor_id] > 0) or \
               (difference < 0 and self.trend_direction[sensor_id] < 0):
                # Trend devam ediyor - biraz daha güçlendir
                trend_strength = random.uniform(0.1, 0.3)
                value += self.trend_direction[sensor_id] * trend_strength
            else:
                # Trend değişti - yeni yön belirle
                self.trend_direction[sensor_id] = random.choice([-1, 1])
        
        # Sensörler arası korelasyon
        if sensor_type == 'air_temperature' and 'soil_moisture' in self.last_values:
            # Sıcaklık artarsa nem azalır
            temp_change = value - (self.last_values.get(sensor_id, value))
            if abs(temp_change) > 2:
                # Sıcaklık değişimi büyükse nem etkilenir
                pass  # Bu kısım daha karmaşık korelasyon için
        
        return value
    
    def _add_random_variation(self, sensor_type: str, value: float) -> float:
        """Rastgele değişim ekle"""
        if not SimulatorConfig.ENABLE_RANDOM_VARIATIONS:
            return value
        
        variation = SimulatorConfig.SENSOR_RANGES[sensor_type]['variation']
        random_change = random.uniform(-variation, variation)
        
        return value + random_change
    
    def _clamp_value(self, sensor_type: str, value: float) -> float:
        """Değeri sınırlar içinde tut"""
        ranges = SimulatorConfig.SENSOR_RANGES[sensor_type]
        return max(ranges['min'], min(ranges['max'], value))
    
    def _calculate_sensor_status(self, sensor_type: str, value: float) -> str:
        """Sensör durumunu hesapla"""
        ranges = SimulatorConfig.SENSOR_RANGES[sensor_type]
        
        if sensor_type == 'soil_moisture':
            # Toprak nemi için özel mantık: Optimal: 40-70%, Warning: 25-40% veya 70-85%, Critical: <25% veya >85%
            if value < 25 or value > 85:
                return 'critical'
            elif (value >= 25 and value < 40) or (value > 70 and value <= 85):
                return 'warning'
            else:
                return 'normal'
        else:
            # Diğer sensörler için genel mantık
            if value < ranges['critical_min'] or value > ranges['critical_max']:
                return 'critical'
            elif value < (ranges['critical_min'] * 1.2) or value > (ranges['critical_max'] * 0.8):
                return 'warning'
            else:
                return 'normal'
    
    def _calculate_quality_score(self) -> int:
        """Veri kalitesi skoru hesapla"""
        # %95-100 arası normal kalite
        base_score = random.uniform(95, 100)
        
        # Senaryoya göre kalite düşür
        if self.current_scenario == 'extreme_temp':
            base_score -= random.uniform(5, 15)
        elif self.current_scenario == 'drought':
            base_score -= random.uniform(2, 8)
        
        return max(50, min(100, int(base_score)))
    
    def _simulate_battery_level(self, sensor_id: int) -> int:
        """Batarya seviyesi simüle et"""
        # Başlangıçta %100, zamanla azalır
        if sensor_id not in self.last_values:
            return 100
        
        # Her veri gönderiminde %0.1 azalır
        current_battery = getattr(self, f'_battery_{sensor_id}', 100)
        current_battery -= random.uniform(0.05, 0.15)
        
        # Minimum %10'da kalır
        current_battery = max(10, current_battery)
        setattr(self, f'_battery_{sensor_id}', current_battery)
        
        return int(current_battery)
    
    def _simulate_signal_strength(self) -> int:
        """Sinyal gücü simüle et"""
        # RSSI değeri: -120 ile -30 arası
        base_rssi = random.uniform(-80, -40)
        
        # Hava durumuna göre değişim
        if self.current_scenario == 'rainy':
            base_rssi -= random.uniform(5, 15)
        elif self.current_scenario == 'extreme_temp':
            base_rssi -= random.uniform(2, 8)
        
        return int(max(-120, min(-30, base_rssi)))
    
    def get_scenario_info(self) -> Dict[str, Any]:
        """Mevcut senaryo bilgilerini döndür"""
        return {
            'current_scenario': self.current_scenario,
            'probability': SimulatorConfig.SCENARIOS[self.current_scenario],
            'description': self._get_scenario_description()
        }
    
    def _get_scenario_description(self) -> str:
        """Senaryo açıklaması"""
        descriptions = {
            'normal': 'Normal hava koşulları',
            'drought': 'Kuraklık dönemi - düşük nem, yüksek sıcaklık',
            'rainy': 'Yağışlı dönem - yüksek nem, düşük sıcaklık',
            'extreme_temp': 'Aşırı sıcaklık - kritik değerler'
        }
        return descriptions.get(self.current_scenario, 'Bilinmeyen senaryo') 