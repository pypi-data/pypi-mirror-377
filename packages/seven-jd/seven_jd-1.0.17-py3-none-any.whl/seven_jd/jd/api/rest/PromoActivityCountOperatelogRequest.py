from seven_jd.jd.api.base import RestApi

class PromoActivityCountOperatelogRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.activityId = None
			self.skuId = None
			self.skuIdList = None
			self.operateLevel = None
			self.operateList = None
			self.operatorName = None
			self.multiActivityId = None
			self.storeId = None

		def getapiname(self):
			return 'jingdong.promo.activity.count.operatelog'

			





