from seven_jd.jd.api.base import RestApi

class DataVenderUserpackIsvSensitiveWordCheckRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sms_content = None

		def getapiname(self):
			return 'jingdong.data.vender.userpack.isv.sensitive.word.check'

			





