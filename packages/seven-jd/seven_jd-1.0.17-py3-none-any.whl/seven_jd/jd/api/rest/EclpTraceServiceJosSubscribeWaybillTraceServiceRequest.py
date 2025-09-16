from seven_jd.jd.api.base import RestApi

class EclpTraceServiceJosSubscribeWaybillTraceServiceRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.source = None
			self.waybillId = None
			self.carrierCode = None
			self.sign = None
			self.t = None

		def getapiname(self):
			return 'jingdong.eclp.trace.service.jos.SubscribeWaybillTraceService'

			





