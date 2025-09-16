from seven_jd.jd.api.base import RestApi

class EclpRtwAcceptReturnOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deliveryNo = None
			self.receiptNo = None
			self.packageCodes = None
			self.sourceNo = None
			self.ownerNo = None
			self.billType = None
			self.warehouseNo = None
			self.tenantId = None
			self.skuNo = None
			self.skuName = None
			self.expectedQty = None
			self.isvLotattrs = None
			self.checkLotattrs = None

		def getapiname(self):
			return 'jingdong.eclp.rtw.acceptReturnOrder'

			





