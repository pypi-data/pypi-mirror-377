from seven_jd.jd.api.base import RestApi

class EclpOrderGetOrderTrackMessageRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderNo = None

		def getapiname(self):
			return 'jingdong.eclp.order.getOrderTrackMessage'

			





