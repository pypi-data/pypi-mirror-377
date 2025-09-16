from seven_jd.jd.api.base import RestApi

class EclpCoCreateWbOrderRequest(RestApi):
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
			self.spId = None
			self.saleOrderNo = None
			self.packageServiceOn = None
			self.deliveryMthd = None
			self.providerCode = None
			self.packageNo = None
			self.clientNo = None
			self.orderType = None
			self.siteCollect = None
			self.siteDelivery = None
			self.quarantineCert = None
			self.selfCollectSiteId = None
			self.selfDeliverySiteId = None
			self.expectedArrivalStartTime = None
			self.expectedArrivalEndTime = None
			self.vehicleOrderNo = None
			self.messageSign = None
			self.checkPreSort = None
			self.receiverNameSplit = None
			self.receiverCompanySplit = None
			self.receiverMobileSplit = None
			self.receiverPhoneSplit = None
			self.receiverProvinceNameSplit = None
			self.receiverProvinceSplit = None
			self.receiverCityNameSplit = None
			self.receiverCitySplit = None
			self.receiverCountyNameSplit = None
			self.receiverCountySplit = None
			self.receiverTownNameSplit = None
			self.receiverTownSplit = None
			self.receiverAddressSplit = None
			self.expectedArrivalStartTimeSplit = None
			self.expectedArrivalEndTimeSplit = None
			self.orderNoSplit = None
			self.expressItemNameSplit = None
			self.grossVolumeSplit = None
			self.grossWeightSplit = None
			self.expressItemQtySplit = None
			self.temptureNumSplit = None
			self.quarantineCertSplit = None
			self.deliveryIntoWarehouseSplit = None
			self.inStorageNoSplit = None
			self.inStorageTimeSplit = None
			self.inStorageRemarkSplit = None
			self.loadFlagSplit = None
			self.unloadFlagSplit = None
			self.remarkSplit = None
			self.packageModelNosSplit = None
			self.qingzhenOnSplit = None
			self.yiwuranOnSplit = None
			self.receiverNickNameSplit = None
			self.guaranteeValueSplit = None
			self.heavyUpstairSplit = None
			self.hospitalServicesYYSplit = None
			self.isvOrderAmount = None
			self.tracker = None
			self.deliveryMode = None
			self.warehouseServiceType = None
			self.homeDeliveryOn = None
			self.siteCode = None
			self.referCancelDate = None
			self.rebackConfluenceOn = None
			self.expressDeliveryOn = None
			self.expectPickupDate = None
			self.expectDeliveryDate = None
			self.warehousePlatformName = None
			self.temporaryStorage = None
			self.predictReceiptDate = None
			self.extendFieldStr = None
			self.peaceMindReceive = None
			self.backInfoOn = None
			self.backName = None
			self.backMobile = None
			self.backPhone = None
			self.backProvinceName = None
			self.backCityName = None
			self.backCountyName = None
			self.backTownName = None
			self.backAddress = None
			self.importFlag = None
			self.fileWithCargo = None
			self.hospitalServicesYY = None
			self.param = None

		def getapiname(self):
			return 'jingdong.eclp.co.createWbOrder'

			





