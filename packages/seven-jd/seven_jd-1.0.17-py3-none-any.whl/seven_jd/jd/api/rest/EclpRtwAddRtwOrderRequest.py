from seven_jd.jd.api.base import RestApi

class EclpRtwAddRtwOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.eclpSoNo = None
			self.eclpRtwNo = None
			self.isvRtwNum = None
			self.warehouseNo = None
			self.logicParam = None
			self.reson = None
			self.orderType = None
			self.packageNo = None
			self.isvSoNo = None
			self.orderMark = None
			self.shipperName = None
			self.ownerNo = None
			self.orderInType = None
			self.receiveLevel = None
			self.sellerRemark = None
			self.salesMan = None
			self.salesBillingStaff = None
			self.drugElectronicSupervisionCode = None
			self.registerOrgNo = None
			self.registerOrgName = None
			self.customerName = None
			self.receivePriority = None
			self.sellerRtwType = None
			self.sellerRtwTypeName = None
			self.salesPlatformName = None
			self.spSoNo = None
			self.shopName = None
			self.workOrderNo = None
			self.senderName = None
			self.senderTelPhone = None
			self.senderMobilePhone = None
			self.customerId = None
			self.customField = None
			self.salesPlatformNo = None
			self.relatedOrderNo = None
			self.serialVersion = None
			self.serialBizType = None
			self.serialDetailMapJson = None
			self.isvGoodsNo = None
			self.planQty = None
			self.goodsLevel = None
			self.productionDate = None
			self.packageBatchNo = None
			self.eclpOutOrderNo = None
			self.sellerOutOrderNo = None
			self.unitPrice = None
			self.money = None
			self.mediumPackage = None
			self.bigPackage = None
			self.orderLine = None
			self.batAttrListJson = None
			self.deptGoodsNo = None
			self.planRtwReasonNo = None
			self.planRtwReasonDesc = None
			self.reserve1 = None

		def getapiname(self):
			return 'jingdong.eclp.rtw.addRtwOrder'

			





