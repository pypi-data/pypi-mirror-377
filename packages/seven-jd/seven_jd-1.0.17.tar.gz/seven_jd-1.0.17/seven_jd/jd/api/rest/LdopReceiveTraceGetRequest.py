from seven_jd.jd.api.base import RestApi

class LdopReceiveTraceGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.customerCode = None
			self.waybillCode = None

		def getapiname(self):
			return 'jingdong.ldop.receive.trace.get'

			





