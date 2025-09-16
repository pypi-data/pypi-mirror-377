from seven_jd.jd.api.base import RestApi

class JingdongDataVenderIsvstrategyUpdateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.partition = None
			self.applicationDomain = None
			self.name = None
			self.description = None
			self.strategyId = None
			self.strategyParam = None
			self.strategy = None

		def getapiname(self):
			return 'jingdong.jingdong.data.vender.isvstrategy.update'

			





