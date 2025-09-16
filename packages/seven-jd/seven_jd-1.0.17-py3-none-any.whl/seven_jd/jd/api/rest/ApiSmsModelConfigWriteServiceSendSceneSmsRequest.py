from seven_jd.jd.api.base import RestApi

class ApiSmsModelConfigWriteServiceSendSceneSmsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.clientSource = None
			self.id = None
			self.paramMap = None

		def getapiname(self):
			return 'jingdong.api.SmsModelConfigWriteService.sendSceneSms'

			
	

class ClientSource(object):
		def __init__(self):
			"""
			"""





