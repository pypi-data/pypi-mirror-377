from seven_jd.jd.api.base import RestApi

class DataVenderIsvstrategyCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.application_domain = None
			self.name = None
			self.description = None
			self.strategy_param = None
			self.strategy = None

		def getapiname(self):
			return 'jingdong.data.vender.isvstrategy.create'

			





