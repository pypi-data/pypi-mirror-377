from seven_jd.jd.api.base import RestApi

class DataVenderSmsEffectGetrtRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.search_id = None
			self.activity_record_id = None

		def getapiname(self):
			return 'jingdong.data.vender.sms.effect.getrt'

			





