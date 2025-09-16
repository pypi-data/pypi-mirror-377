from seven_jd.jd.api.base import RestApi

class ApiSmsModelConfigReadServiceGetSmsModelConfigByParamsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.pageNumber = None
			self.serveType = None
			self.pageSize = None
			self.businessType = None
			self.name = None

		def getapiname(self):
			return 'jingdong.api.SmsModelConfigReadService.getSmsModelConfigByParams'

			





