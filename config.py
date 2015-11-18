import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'de.vsecreet' 
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SUBJECT_PREFIX = '[Insightv0.1]'
	MAIL_SENDER = 'Election Insight Admin' 
	ADMIN = os.environ.get('INSIGHT_ADMIN')

	@staticmethod
	def init_app(app): 
		pass


class DevelopmentConfig(Config): 
	DEBUG = True
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
	        'sqlite:///' + os.path.join(basedir, 'data-staging_rev6.sqlite')



class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
	 'sqlite:///' + os.path.join(basedir, 'data-staging_rev6.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}




