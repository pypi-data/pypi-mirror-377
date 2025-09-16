from seven_jd.jd.api.base import RestApi

class SmsJosModelTypeListServiceRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.pageNumber = None
			self.pageSize = None

		def getapiname(self):
			return 'jingdong.sms.jos.ModelTypeListService'

			





