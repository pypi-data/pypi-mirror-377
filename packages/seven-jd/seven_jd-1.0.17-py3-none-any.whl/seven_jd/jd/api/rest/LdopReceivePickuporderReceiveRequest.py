from seven_jd.jd.api.base import RestApi

class LdopReceivePickuporderReceiveRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.pickupAddress = None
			self.pickupName = None
			self.pickupTel = None
			self.customerTel = None
			self.customerCode = None
			self.backAddress = None
			self.customerContract = None
			self.desp = None
			self.orderId = None
			self.weight = None
			self.remark = None
			self.volume = None
			self.valueAddService = None
			self.guaranteeValue = None
			self.guaranteeValueAmount = None
			self.pickupStartTime = None
			self.pickupEndTime = None
			self.productId = None
			self.productName = None
			self.productCount = None
			self.snCode = None
			self.skuAddService = None
			self.skuCheckOutShapes = None
			self.skuCheckAttachFile = None
			self.antiTearingCode = None
			self.promiseTimeType = None
			self.guaranteeSettleType = None
			self.packingSettleType = None
			self.freightSettleType = None
			self.allowedRepeatOrderType = None
			self.salePlatform = None
			self.settleType = None

		def getapiname(self):
			return 'jingdong.ldop.receive.pickuporder.receive'

			





