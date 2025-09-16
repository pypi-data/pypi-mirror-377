from seven_jd.jd.api.base import RestApi

class EclpAfsCreateServiceOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.isvUUId = None
			self.isvSource = None
			self.shopNo = None
			self.departmentNo = None
			self.shipperNo = None
			self.eclpOrderId = None
			self.salePlatformSource = None
			self.salesPlatformCreateTime = None
			self.sourceType = None
			self.pickupType = None
			self.isInvoice = None
			self.invoiceNo = None
			self.isPackage = None
			self.isTestReport = None
			self.customerName = None
			self.customerTel = None
			self.provinceNo = None
			self.provinceName = None
			self.cityName = None
			self.cityNo = None
			self.countyName = None
			self.countyNo = None
			self.townName = None
			self.townNo = None
			self.customerAddress = None
			self.pickupAddress = None
			self.operatorId = None
			self.operatorName = None
			self.operateTime = None
			self.pickupNo = None
			self.questionDesc = None
			self.applyReason = None
			self.amsAuditComment = None
			self.waybill = None
			self.pickwaretype = None
			self.isvGoodsNo = None
			self.quantity = None
			self.weight = None
			self.sn = None
			self.attachmentDetails = None
			self.wareType = None
			self.isCreatePickup = None
			self.businessPhone = None
			self.outPickupType = None
			self.afterSalesChangeNo = None
			self.spOrderId = None

		def getapiname(self):
			return 'jingdong.eclp.afs.createServiceOrder'

			





