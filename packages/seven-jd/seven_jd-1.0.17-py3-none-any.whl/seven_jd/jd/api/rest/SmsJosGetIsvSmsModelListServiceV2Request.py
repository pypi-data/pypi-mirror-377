from seven_jd.jd.api.base import RestApi

class SmsJosGetIsvSmsModelListServiceV2Request(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.pageNumber = None
			self.createTimeEnd = None
			self.pageSize = None
			self.createTimeStart = None
			self.modifiedStart = None
			self.modifiedEnd = None

		def getapiname(self):
			return 'jingdong.sms.jos.GetIsvSmsModelListService.v2'

			





