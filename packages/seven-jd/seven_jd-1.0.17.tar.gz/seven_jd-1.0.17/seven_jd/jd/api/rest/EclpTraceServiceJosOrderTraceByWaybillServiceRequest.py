from seven_jd.jd.api.base import RestApi

class EclpTraceServiceJosOrderTraceByWaybillServiceRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.waybillId = None
			self.carrierCode = None
			self.role = None
			self.userId = None

		def getapiname(self):
			return 'jingdong.eclp.trace.service.jos.OrderTraceByWaybillService'

			





