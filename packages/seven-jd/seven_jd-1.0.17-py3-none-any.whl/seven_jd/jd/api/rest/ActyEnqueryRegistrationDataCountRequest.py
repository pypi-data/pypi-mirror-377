from seven_jd.jd.api.base import RestApi

class ActyEnqueryRegistrationDataCountRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.skuId = None
			self.orderId = None
			self.beginDate = None
			self.endDate = None

		def getapiname(self):
			return 'jingdong.acty.enqueryRegistrationDataCount'

			





