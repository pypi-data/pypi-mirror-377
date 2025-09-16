from seven_jd.jd.api.base import RestApi

class EclpGoodsQueryShopGoodsInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.size = None
			self.current = None
			self.deptNo = None
			self.goodsNo = None
			self.shopNo = None
			self.spGoodsNo = None
			self.isvGoodsNo = None
			self.shopGoodsNoLT = None

		def getapiname(self):
			return 'jingdong.eclp.goods.queryShopGoodsInfo'

			





