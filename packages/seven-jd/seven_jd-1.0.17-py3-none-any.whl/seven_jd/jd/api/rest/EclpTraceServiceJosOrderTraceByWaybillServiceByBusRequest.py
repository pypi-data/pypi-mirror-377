from seven_jd.jd.api.base import RestApi

class EclpTraceServiceJosOrderTraceByWaybillServiceByBusRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.userId = None
			self.venderId = None
			self.role = None
			self.businessType = None
			self.carrierCode = None
			self.waybillId = None

		def getapiname(self):
			return 'jingdong.eclp.trace.service.jos.orderTraceByWaybillServiceByBus'

			





