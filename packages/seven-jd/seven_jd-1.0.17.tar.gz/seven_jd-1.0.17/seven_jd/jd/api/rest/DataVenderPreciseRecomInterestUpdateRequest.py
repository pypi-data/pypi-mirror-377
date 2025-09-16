from seven_jd.jd.api.base import RestApi

class DataVenderPreciseRecomInterestUpdateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.activity_id = None
			self.interest_id = None
			self.content = None
			self.interest_type = None
			self.interest_level = None
			self.enabled = None
			self.start_time = None
			self.end_time = None
			self.strategy_id = None
			self.strategy_type = None
			self.strategy_level = None
			self.rate = None
			self.basic = None

		def getapiname(self):
			return 'jingdong.data.vender.precise.recom.interest.update'

			





