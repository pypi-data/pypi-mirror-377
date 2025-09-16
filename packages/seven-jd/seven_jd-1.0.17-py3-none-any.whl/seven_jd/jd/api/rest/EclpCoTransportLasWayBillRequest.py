from seven_jd.jd.api.base import RestApi

class EclpCoTransportLasWayBillRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.orderNo = None
			self.senderName = None
			self.senderMobile = None
			self.senderPhone = None
			self.senderAddress = None
			self.receiverName = None
			self.receiverMobile = None
			self.receiverPhone = None
			self.receiverAddress = None
			self.remark = None
			self.isFragile = None
			self.senderTc = None
			self.predictDate = None
			self.isJDOrder = None
			self.isCod = None
			self.receiveable = None
			self.onDoorPickUp = None
			self.pickUpDate = None
			self.isGuarantee = None
			self.guaranteeValue = None
			self.receiptFlag = None
			self.paperFrom = None
			self.rtnReceiverName = None
			self.rtnReceiverMobile = None
			self.rtnReceiverAddress = None
			self.rtnReceiverPhone = None
			self.productType = None
			self.pickUpForNew = None
			self.pickUpAbnormalNumber = None
			self.pickUpReceiverName = None
			self.pickUpReceiverMobile = None
			self.pickUpReceiverPhone = None
			self.pickUpReceiverCode = None
			self.pickUpReceiverAddress = None
			self.isSignPrint = None
			self.sameCityDelivery = None
			self.lasDischarge = None
			self.thirdPayment = None
			self.extendFieldStr = None
			self.servProductName = None
			self.servProductSku = None
			self.servProductNum = None
			self.servCode = None
			self.saleOrderNo = None
			self.upstairsFlag = None
			self.weight = None
			self.length = None
			self.width = None
			self.height = None
			self.installFlag = None
			self.thirdCategoryNo = None
			self.brandNo = None
			self.productSku = None
			self.packageName = None
			self.reverseLwb = None
			self.getOldService = None
			self.openBoxService = None
			self.deliveryInstallService = None
			self.packageIdentityCode = None
			self.price = None
			self.lasInstall = None

		def getapiname(self):
			return 'jingdong.eclp.co.transportLasWayBill'

			





