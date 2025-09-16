from seven_jd.jd.api.base import RestApi

class LdopReceivePickuporderReceiveOldRequest(RestApi):
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

		def getapiname(self):
			return 'jingdong.ldop.receive.pickuporder.receive.old'

			





