from seven_jd.jd.api.base import RestApi

class DataVenderSmsSendbymodelRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.expireTime = None
			self.smsModelId = None
			self.batchNo = None
			self.smsModelParams = None
			self.pin = None
			self.orderId = None
			self.phoneNo = None

		def getapiname(self):
			return 'jingdong.data.vender.sms.sendbymodel'

			





