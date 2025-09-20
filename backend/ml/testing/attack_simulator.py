import numpy as np
import time
import random
from typing import List, Dict, Any

class AttackSimulator:
    def __init__(self):
        self.attack_patterns = {
            'sql_injection': self._generate_sql_injection,
            'xss_attack': self._generate_xss_attack,
            'ddos_attack': self._generate_ddos_attack,
            'bot_scraping': self._generate_bot_scraping,
            'brute_force': self._generate_brute_force
        }
    
    def simulate_attack(self, attack_type: str, intensity: int = 10) -> List[Dict[str, Any]]:
        if attack_type not in self.attack_patterns:
            raise ValueError(f"Unknown attack type: {attack_type}")
        return self.attack_patterns[attack_type](intensity)
    
    def _generate_sql_injection(self, count: int) -> List[Dict[str, Any]]:
        attacks = []
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM admin --",
            "admin'/**/OR/**/1=1#"
        ]
        
        for i in range(count):
            attacks.append({
                'timestamp': time.time() + i,
                'ip': f"192.168.1.{random.randint(100, 200)}",
                'method': 'POST',
                'path': f"/login?user={random.choice(sql_payloads)}",
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'country': 'US',
                'packet_count': random.randint(5, 15),
                'byte_count': random.randint(500, 2000),
                'duration': random.uniform(0.1, 0.5)
            })
        return attacks
    
    def _generate_xss_attack(self, count: int) -> List[Dict[str, Any]]:
        attacks = []
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert(document.cookie)",
            "<img src=x onerror=alert(1)>",
            "<iframe src=javascript:alert('XSS')></iframe>"
        ]
        
        for i in range(count):
            attacks.append({
                'timestamp': time.time() + i,
                'ip': f"10.0.0.{random.randint(50, 100)}",
                'method': 'GET',
                'path': f"/search?q={random.choice(xss_payloads)}",
                'user_agent': 'Mozilla/5.0 (compatible; MSIE 9.0)',
                'country': 'CN',
                'packet_count': random.randint(3, 8),
                'byte_count': random.randint(300, 1000),
                'duration': random.uniform(0.05, 0.2)
            })
        return attacks
    
    def _generate_ddos_attack(self, count: int) -> List[Dict[str, Any]]:
        attacks = []
        for i in range(count):
            attacks.append({
                'timestamp': time.time() + i * 0.01,
                'ip': f"172.16.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'method': 'GET',
                'path': '/',
                'user_agent': f'Bot-{random.randint(1000, 9999)}',
                'country': random.choice(['RU', 'CN', 'KP']),
                'packet_count': random.randint(100, 500),
                'byte_count': random.randint(10000, 50000),
                'duration': random.uniform(0.001, 0.01)
            })
        return attacks
    
    def _generate_bot_scraping(self, count: int) -> List[Dict[str, Any]]:
        attacks = []
        bot_agents = [
            'python-requests/2.28.1',
            'curl/7.68.0',
            'Scrapy/2.6.1',
            'wget/1.20.3'
        ]
        
        for i in range(count):
            attacks.append({
                'timestamp': time.time() + i * 2,
                'ip': f"198.51.100.{random.randint(1, 50)}",
                'method': 'GET',
                'path': f"/page{random.randint(1, 1000)}",
                'user_agent': random.choice(bot_agents),
                'country': 'US',
                'packet_count': random.randint(2, 5),
                'byte_count': random.randint(200, 800),
                'duration': random.uniform(0.1, 0.3)
            })
        return attacks
    
    def _generate_brute_force(self, count: int) -> List[Dict[str, Any]]:
        attacks = []
        for i in range(count):
            attacks.append({
                'timestamp': time.time() + i * 0.5,
                'ip': f"203.0.113.{random.randint(10, 20)}",
                'method': 'POST',
                'path': "/login",
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64)',
                'country': 'RU',
                'packet_count': random.randint(8, 12),
                'byte_count': random.randint(400, 800),
                'duration': random.uniform(0.2, 0.8)
            })
        return attacks