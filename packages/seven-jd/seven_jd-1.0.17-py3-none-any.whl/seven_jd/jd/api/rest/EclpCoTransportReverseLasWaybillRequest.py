from seven_jd.jd.api.base import RestApi

class EclpCoTransportReverseLasWaybillRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.orderNo = None
			self.salePlatform = None
			self.customerPin = None
			self.associateSoNo = None
			self.senderName = None
			self.senderMobile = None
			self.senderPhone = None
			self.senderAddress = None
			self.receiverName = None
			self.receiverMobile = None
			self.receiverPhone = None
			self.receiverAddress = None
			self.isFragile = None
			self.pickupReturnReason = None
			self.isGuarantee = None
			self.guaranteeValue = None
			self.isDoorToDoorRecycle = None
			self.weight = None
			self.length = None
			self.width = None
			self.height = None
			self.packageName = None
			self.packageQty = None
			self.productSku = None
			self.lasDisassemble = None
			self.lasBale = None
			self.thirdCategoryNo = None

		def getapiname(self):
			return 'jingdong.eclp.co.transportReverseLasWaybill'

			





