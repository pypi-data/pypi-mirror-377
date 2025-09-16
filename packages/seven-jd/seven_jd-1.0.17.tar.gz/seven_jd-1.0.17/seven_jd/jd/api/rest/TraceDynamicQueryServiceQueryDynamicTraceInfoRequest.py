from seven_jd.jd.api.base import RestApi

class TraceDynamicQueryServiceQueryDynamicTraceInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.customerCode = None
			self.waybillCode = None

		def getapiname(self):
			return 'jingdong.trace.dynamicQueryService.queryDynamicTraceInfo'

			





