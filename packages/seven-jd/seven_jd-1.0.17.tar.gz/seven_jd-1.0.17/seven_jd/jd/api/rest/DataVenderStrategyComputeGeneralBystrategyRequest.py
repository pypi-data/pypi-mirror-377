from seven_jd.jd.api.base import RestApi

class DataVenderStrategyComputeGeneralBystrategyRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.strategy = None
			self.strategy_param = None
			self.pin_type = None
			self.partition = None

		def getapiname(self):
			return 'jingdong.data.vender.strategy.compute.general.bystrategy'

			





