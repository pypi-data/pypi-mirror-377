from seven_jd.jd.api.base import RestApi

class EclpOrderExtQueryOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.isvUUID = None
			self.spSoNos = None
			self.isvSource = None
			self.departmentNo = None

		def getapiname(self):
			return 'jingdong.eclp.order.ext.queryOrder'

			





