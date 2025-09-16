from seven_jd.jd.api.base import RestApi

class ConsultationSendSmsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.orderNo = None

		def getapiname(self):
			return 'jingdong.consultation.sendSms'

			





