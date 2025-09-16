from seven_jd.jd.api.base import RestApi

class EclpCloudReceiveOrderInfoRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.machiningNo = None
			self.machiningType = None
			self.ownerNo = None
			self.skuNo = None
			self.productLevel = None
			self.qty = None
			self.destOwnerNo = None
			self.destSkuNo = None
			self.destQty = None
			self.destProductLevel = None
			self.warehouseNo = None
			self.tenantId = None

		def getapiname(self):
			return 'jingdong.eclp.cloud.receiveOrderInfo'

			





