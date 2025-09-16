from seven_jd.jd.api.base import RestApi

class DataVenderStrategyCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.name = None
			self.description = None
			self.strategy = None
			self.strategy_param = None
			self.application_domain = None
			self.partition = None

		def getapiname(self):
			return 'jingdong.data.vender.strategy.create'

			





