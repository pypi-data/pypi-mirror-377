from seven_jd.jd.api.base import RestApi

class DataVenderStrategyDeleteRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.strategy_id = None

		def getapiname(self):
			return 'jingdong.data.vender.strategy.delete'

			





