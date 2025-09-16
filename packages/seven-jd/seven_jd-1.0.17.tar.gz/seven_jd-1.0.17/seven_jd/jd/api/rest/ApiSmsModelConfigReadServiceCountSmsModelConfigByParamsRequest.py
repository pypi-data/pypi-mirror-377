from seven_jd.jd.api.base import RestApi

class ApiSmsModelConfigReadServiceCountSmsModelConfigByParamsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.serveType = None
			self.name = None
			self.businessType = None

		def getapiname(self):
			return 'jingdong.api.SmsModelConfigReadService.countSmsModelConfigByParams'

			





