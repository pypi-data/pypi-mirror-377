from seven_jd.jd.api.base import RestApi

class EclpCoEvaluateB2BLwbFreightMainRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.orderNo = None
			self.deptNo = None
			self.senderNickName = None
			self.senderName = None
			self.senderMobile = None
			self.senderPhone = None
			self.senderProvince = None
			self.senderCity = None
			self.senderCounty = None
			self.senderTown = None
			self.senderProvinceName = None
			self.senderCityName = None
			self.senderCountyName = None
			self.senderTownName = None
			self.senderAddress = None
			self.receiverNickName = None
			self.receiverName = None
			self.receiverMobile = None
			self.receiverPhone = None
			self.receiverProvince = None
			self.receiverCity = None
			self.receiverCounty = None
			self.receiverTown = None
			self.receiverProvinceName = None
			self.receiverCityName = None
			self.receiverCountyName = None
			self.receiverTownName = None
			self.remark = None
			self.grossWeight = None
			self.grossVolume = None
			self.createTime = None
			self.createUser = None
			self.receivable = None
			self.isCod = None
			self.vehicleTypeName = None
			self.vehicleTypeNo = None
			self.vehicleQty = None
			self.expressItemName = None
			self.expressItemQty = None
			self.signReceiptFlag = None
			self.deliveryReceiptFlag = None
			self.deliveryIntoWarehouse = None
			self.loadFlag = None
			self.unloadFlag = None
			self.receiptFlag = None
			self.fcFlag = None
			self.guaranteeValue = None
			self.pickupBeginTime = None
			self.pickupEndTime = None
			self.bussinessType = None
			self.deliveryType = None
			self.senderCompany = None
			self.receiverCompany = None
			self.receiverAddress = None
			self.warehouseCode = None
			self.projectName = None
			self.actualSpId = None
			self.coldChainOn = None
			self.temptureNum = None
			self.qingzhenOn = None
			self.yiwuranOn = None
			self.inStorageNo = None
			self.inStorageTime = None
			self.inStorageRemark = None
			self.heavyUpstair = None
			self.wayBillCode = None

		def getapiname(self):
			return 'jingdong.eclp.co.evaluateB2BLwbFreightMain'

			





