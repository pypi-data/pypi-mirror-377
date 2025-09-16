from seven_jd.jd.api.base import RestApi

class LdopReceiveOrderInterceptRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.vendorCode = None
			self.deliveryId = None
			self.interceptReason = None
			self.cancelOperatorCodeType = None
			self.cancelTime = None
			self.cancelOperator = None

		def getapiname(self):
			return 'jingdong.ldop.receive.order.intercept'

			





