from seven_jd.jd.api.base import RestApi

class DataVenderMarketingActivityCreateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.mode = None
			self.mkt_activity_des = None
			self.mkt_activity_id = None
			self.start_time = None
			self.end_time = None
			self.state = None
			self.mkt_activity_name = None

		def getapiname(self):
			return 'jingdong.data.vender.marketing.activity.create'

			





