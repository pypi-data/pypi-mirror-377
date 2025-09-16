from seven_jd.jd.api.base import RestApi

class MarketVenderMediaMessageQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.activityId = None
			self.venderId = None
			self.appKey = None

		def getapiname(self):
			return 'jingdong.market.vender.media.message.query'

			





