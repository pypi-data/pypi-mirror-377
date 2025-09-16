from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvSmsSentRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.full_content = None
			self.receive_phone = None
			self.asset_token = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.sms.sent'

			





