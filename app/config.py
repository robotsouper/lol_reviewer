import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    RIOT_API_KEY = os.getenv('RIOT_API_KEY')
    RATE_LIMIT_PER_SECOND = 20
    RATE_LIMIT_PER_TWO_MINUTES = 100
    CACHE_TTL_PUUID = 3600  # 1 hour
    CACHE_TTL_MATCH_IDS = 300  # 5 minutes
    CACHE_TTL_MATCH_DETAILS = 1800  # 30 minutes
    MAX_MATCHES = 20
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    ENV = 'production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
