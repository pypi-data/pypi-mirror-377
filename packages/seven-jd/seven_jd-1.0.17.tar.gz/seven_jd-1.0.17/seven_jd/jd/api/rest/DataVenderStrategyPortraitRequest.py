from seven_jd.jd.api.base import RestApi

class DataVenderStrategyPortraitRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.strategy_id = None
			self.field = None
			self.strategy_param = None

		def getapiname(self):
			return 'jingdong.data.vender.strategy.portrait'

			





