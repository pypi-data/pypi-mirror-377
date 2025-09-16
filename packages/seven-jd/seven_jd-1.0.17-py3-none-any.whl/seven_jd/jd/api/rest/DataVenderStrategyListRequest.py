from seven_jd.jd.api.base import RestApi

class DataVenderStrategyListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.state = None
			self.page = None
			self.page_size = None
			self.application_domain = None

		def getapiname(self):
			return 'jingdong.data.vender.strategy.list'

			





