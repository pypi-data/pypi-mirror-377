from seven_jd.jd.api.base import RestApi

class DataVenderIsvstrategyListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.page_size = None
			self.state = None
			self.page = None
			self.application_domain = None

		def getapiname(self):
			return 'jingdong.data.vender.isvstrategy.list'

			





