from seven_jd.jd.api.base import RestApi

class TraceO2oTracebywaybillserviceRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.waybillCode = None
			self.source = None

		def getapiname(self):
			return 'jingdong.trace.o2o.tracebywaybillservice'

			





