from seven_jd.jd.api.base import RestApi

class ComJdInteractCenterApiWriteEvaluateActivityWriteServiceCreateActivityWithResultRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.appName = None
			self.channel = None
			self.skuName = None
			self.cate3rdName = None
			self.cate1stName = None
			self.cate3rdCode = None
			self.price = None
			self.cate2ndName = None
			self.skuId = None
			self.wareId = None
			self.cate1stCode = None
			self.cate2ndCode = None
			self.supplierCode = None
			self.endTime = None
			self.modifier = None
			self.startTime = None
			self.pictureRequirement = None
			self.shopName = None
			self.validateDay = None
			self.assetItemId = None
			self.type = None
			self.discount = None
			self.awardType = None
			self.quota = None
			self.rulePrice = None
			self.floatRatio = None
			self.nums = None
			self.batchKey = None
			self.expireType = None
			self.name = None
			self.vedioRequirement = None
			self.wordRequirement = None

		def getapiname(self):
			return 'jingdong.com.jd.interact.center.api.write.EvaluateActivityWriteService.createActivityWithResult'

			





