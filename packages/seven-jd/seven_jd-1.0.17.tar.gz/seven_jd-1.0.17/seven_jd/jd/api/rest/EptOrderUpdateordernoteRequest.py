from seven_jd.jd.api.base import RestApi

class EptOrderUpdateordernoteRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderId = None
			self.note = None

		def getapiname(self):
			return 'jingdong.ept.order.updateordernote'

			





