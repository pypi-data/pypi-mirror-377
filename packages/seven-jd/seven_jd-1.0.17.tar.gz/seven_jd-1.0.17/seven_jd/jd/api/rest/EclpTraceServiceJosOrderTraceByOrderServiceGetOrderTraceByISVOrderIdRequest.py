from seven_jd.jd.api.base import RestApi

class EclpTraceServiceJosOrderTraceByOrderServiceGetOrderTraceByISVOrderIdRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.role = None
			self.orderId = None
			self.carrierCode = None
			self.businessType = None
			self.userId = None

		def getapiname(self):
			return 'jingdong.eclp.trace.service.jos.OrderTraceByOrderService.getOrderTraceByISVOrderId'

			





