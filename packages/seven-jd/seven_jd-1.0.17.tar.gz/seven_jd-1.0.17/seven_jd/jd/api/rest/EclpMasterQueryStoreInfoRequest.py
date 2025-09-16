from seven_jd.jd.api.base import RestApi

class EclpMasterQueryStoreInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.page = None
			self.pageSize = None
			self.sellerNo = None
			self.storeNo = None

		def getapiname(self):
			return 'jingdong.eclp.master.queryStoreInfo'

			





