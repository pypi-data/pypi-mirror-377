from seven_jd.jd.api.base import RestApi

class EclpOrderAddOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.isvUUID = None
			self.isvSource = None
			self.shopNo = None
			self.bdOwnerNo = None
			self.departmentNo = None
			self.warehouseNo = None
			self.shipperNo = None
			self.salesPlatformOrderNo = None
			self.salePlatformSource = None
			self.salesPlatformCreateTime = None
			self.soType = None
			self.consigneeName = None
			self.consigneeMobile = None
			self.consigneePhone = None
			self.consigneeEmail = None
			self.expectDate = None
			self.addressProvince = None
			self.addressCity = None
			self.addressCounty = None
			self.addressTown = None
			self.consigneeAddress = None
			self.consigneePostcode = None
			self.receivable = None
			self.consigneeRemark = None
			self.orderMark = None
			self.thirdWayBill = None
			self.packageMark = None
			self.businessType = None
			self.destinationCode = None
			self.destinationName = None
			self.sendWebsiteCode = None
			self.sendWebsiteName = None
			self.sendMode = None
			self.receiveMode = None
			self.appointDeliveryTime = None
			self.insuredPriceFlag = None
			self.insuredValue = None
			self.thirdPayment = None
			self.monthlyAccount = None
			self.shipment = None
			self.sellerRemark = None
			self.thirdSite = None
			self.gatherCenterName = None
			self.customsStatus = None
			self.customerName = None
			self.invoiceTitle = None
			self.invoiceContent = None
			self.goodsType = None
			self.goodsLevel = None
			self.customsPort = None
			self.billType = None
			self.orderPrice = None
			self.wlyInfo = None
			self.customerId = None
			self.urgency = None
			self.customerNo = None
			self.storeName = None
			self.invoiceState = None
			self.invoiceType = None
			self.invoiceNo = None
			self.invoiceTax = None
			self.bankName = None
			self.bankAccount = None
			self.address = None
			self.phoneNumber = None
			self.signType = None
			self.signIDCode = None
			self.supplierNo = None
			self.agingType = None
			self.sellerNote = None
			self.supervisionCode = None
			self.invoiceChecker = None
			self.paymentType = None
			self.saleType = None
			self.inStorageNo = None
			self.inStorageTime = None
			self.inStorageRemark = None
			self.grossReturnName = None
			self.grossReturnPhone = None
			self.grossReturnMobile = None
			self.grossReturnAddress = None
			self.isvPackTypeNo = None
			self.addrAnalysis = None
			self.printExtendInfo = None
			self.logicParam = None
			self.combineNo = None
			self.activationService = None
			self.randomInspection = None
			self.VIPDeliWarehouse = None
			self.customField = None
			self.longitude = None
			self.latitude = None
			self.agingProductType = None
			self.crossDockPriority = None
			self.isvCompanyNo = None
			self.orderPriority = None
			self.orderBatchNo = None
			self.orderBatchQty = None
			self.productCode = None
			self.vehicleType = None
			self.isvSoType = None
			self.checkDelivery = None
			self.isvSoTypeName = None
			self.quarantineCert = None
			self.deliveryService = None
			self.selfDeliverySiteId = None
			self.deliveryIntoWarehouse = None
			self.deliveryWarehouseType = None
			self.unPack = None
			self.deliveryBeforeCommand = None
			self.pickUpCode = None
			self.isvShopNo = None
			self.expecTransport = None
			self.inDependent = None
			self.storeBrand = None
			self.storeId = None
			self.unloadFlag = None
			self.relationNo = None
			self.deliveryProductCode = None
			self.sellerWarehouseNo = None
			self.peaceMindReceive = None
			self.yardInner = None
			self.warehouseProductNo = None
			self.deliveryProductNo = None
			self.payTime = None
			self.goodsNo = None
			self.skuGoodsLevel = None
			self.goodsName = None
			self.type = None
			self.unit = None
			self.remark = None
			self.rate = None
			self.amount = None
			self.price = None
			self.quantity = None
			self.pAttributes = None
			self.isvLotattrs = None
			self.isvGoodsNo = None
			self.installVenderId = None
			self.orderLine = None
			self.batAttrs = None
			self.productionDate = None
			self.expirationDate = None
			self.packBatchNo = None
			self.poNo = None
			self.lot = None
			self.serialNo = None
			self.jdPackageType = None
			self.serviceProductJson = None
			self.payAmount = None
			self.sellerGoodsRemark = None
			self.leftExpirationPercent = None
			self.leftExpirationPercentOperate = None
			self.batAttrRangeJson = None
			self.cloudPrintInfoJson = None

		def getapiname(self):
			return 'jingdong.eclp.order.addOrder'

			





