from seven_jd.jd.api.base import RestApi

class PopMarketWritePromotionGiftApproveRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.ip = None
			self.port = None
			self.request_id = None
			self.promoId = None

		def getapiname(self):
			return 'jingdong.pop.market.write.promotion.gift.approve'

			





