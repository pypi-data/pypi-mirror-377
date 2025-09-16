from seven_jd.jd.api.base import RestApi

class TemplateMarketInterfaceStrategyUpdateStrategyRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.venderId = None
			self.channelId = None
			self.subType = None
			self.property2 = None
			self.property1 = None
			self.conent = None
			self.startTime = None
			self.endTime = None
			self.strategy = None

		def getapiname(self):
			return 'jingdong.template.market.interface.strategy.updateStrategy'

			





