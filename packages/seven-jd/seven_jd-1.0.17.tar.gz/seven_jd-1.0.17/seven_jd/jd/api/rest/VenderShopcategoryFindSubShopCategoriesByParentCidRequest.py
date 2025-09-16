from seven_jd.jd.api.base import RestApi

class VenderShopcategoryFindSubShopCategoriesByParentCidRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.parent_cid = None

		def getapiname(self):
			return 'jingdong.vender.shopcategory.findSubShopCategoriesByParentCid'

			





