from seven_jd.jd.api.base import RestApi

class SmsJosCreateIsvSmsModelServiceRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.detail = None
			self.name = None
			self.isvAppKey = None
			self.modelTypeId = None
			self.operators = None

		def getapiname(self):
			return 'jingdong.sms.jos.createIsvSmsModelService'

			





