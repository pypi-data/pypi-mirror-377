from seven_jd.jd.api.base import RestApi

class SellerPromotionV2GetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.ip = None
			self.port = None
			self.promo_id = None
			self.promo_type = None

		def getapiname(self):
			return 'jingdong.seller.promotion.v2.get'

			





