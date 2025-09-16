from seven_jd.jd.api.base import RestApi

class EclpOrderAsynAddOrderRequest(RestApi):
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
			self.insuredFee = None
			self.thirdPayment = None
			self.monthlyAccount = None
			self.shipment = None
			self.sellerRemark = None
			self.thirdSite = None
			self.customsStatus = None
			self.customerName = None
			self.invoiceTitle = None
			self.invoiceContent = None
			self.goodsType = None
			self.goodsLevel = None
			self.customsPort = None
			self.billType = None
			self.orderPrice = None
			self.orderBatchNo = None
			self.orderBatchQty = None
			self.transactionSource = None
			self.countrycode = None
			self.goodsNo = None
			self.price = None
			self.quantity = None
			self.serialNo = None
			self.printName = None

		def getapiname(self):
			return 'jingdong.eclp.order.asynAddOrder'

			





