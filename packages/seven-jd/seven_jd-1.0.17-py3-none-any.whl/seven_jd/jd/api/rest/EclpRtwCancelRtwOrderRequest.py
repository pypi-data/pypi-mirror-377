from seven_jd.jd.api.base import RestApi

class EclpRtwCancelRtwOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.isvRtwNum = None
			self.eclpRtwNum = None
			self.cancelReson = None
			self.ownerNo = None
			self.orderInType = None

		def getapiname(self):
			return 'jingdong.eclp.rtw.cancelRtwOrder'

			





