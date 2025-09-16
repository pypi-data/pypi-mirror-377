from seven_jd.jd.api.base import RestApi

class EclpRtwGetRtwDifListForMerchantRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.difStartTime = None
			self.difEndTime = None
			self.ownerNo = None
			self.difType = None
			self.eclpWarehouseNo = None
			self.pageNo = None
			self.pageSize = None
			self.manageStatus = None

		def getapiname(self):
			return 'jingdong.eclp.rtw.getRtwDifListForMerchant'

			





