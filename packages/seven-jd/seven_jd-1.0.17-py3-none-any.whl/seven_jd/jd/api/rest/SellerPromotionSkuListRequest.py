from seven_jd.jd.api.base import RestApi

class SellerPromotionSkuListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.ware_id = None
			self.sku_id = None
			self.promo_id = None
			self.bind_type = None
			self.page = None
			self.size = None

		def getapiname(self):
			return 'jingdong.seller.promotion.sku.list'

			





