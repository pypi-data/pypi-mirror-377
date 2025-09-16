from seven_jd.jd.api.base import RestApi

class VcItemShopProductsSearchRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderType = None
			self.productId = None
			self.createdEndTime = None
			self.modifiedStartTime = None
			self.skuStatus = None
			self.pageSize = None
			self.pageNum = None
			self.thirdCategoryId = None
			self.rootCategoryId = None
			self.skuName = None
			self.lastCategoryId = None
			self.createdStartTime = None
			self.brandId = None
			self.secondCategoryId = None
			self.modifiedEndTime = None

		def getapiname(self):
			return 'jingdong.vc.item.shop.products.search'

			





