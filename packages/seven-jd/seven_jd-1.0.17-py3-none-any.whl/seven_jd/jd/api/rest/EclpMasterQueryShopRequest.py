from seven_jd.jd.api.base import RestApi

class EclpMasterQueryShopRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.shopNos = None
			self.isvShopNos = None
			self.deptNo = None

		def getapiname(self):
			return 'jingdong.eclp.master.queryShop'

			





