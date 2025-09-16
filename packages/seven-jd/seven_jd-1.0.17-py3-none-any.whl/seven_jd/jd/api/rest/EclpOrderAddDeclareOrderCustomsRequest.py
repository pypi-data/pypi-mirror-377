from seven_jd.jd.api.base import RestApi

class EclpOrderAddDeclareOrderCustomsRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.platformId = None
			self.platformName = None
			self.appType = None
			self.logisticsNo = None
			self.billSerialNo = None
			self.billNo = None
			self.freight = None
			self.insuredFee = None
			self.netWeight = None
			self.weight = None
			self.packNo = None
			self.worth = None
			self.goodsName = None
			self.orderNo = None
			self.shipper = None
			self.shipperAddress = None
			self.shipperTelephone = None
			self.shipperCountry = None
			self.consigneeCountry = None
			self.consigneeProvince = None
			self.consigneeCity = None
			self.consigneeDistrict = None
			self.consingee = None
			self.consigneeAddress = None
			self.consigneeTelephone = None
			self.buyerIdType = None
			self.buyerIdNumber = None
			self.customsId = None
			self.customsCode = None
			self.deptNo = None
			self.isvSource = None
			self.pattern = None
			self.isvUUID = None
			self.platformType = None
			self.salesPlatformCreateTime = None
			self.postType = None
			self.istax = None
			self.logisticsCode = None
			self.logisticsName = None
			self.isDelivery = None
			self.ebpCode = None
			self.ebpName = None
			self.ebcCode = None
			self.ebcName = None
			self.ebpCiqCode = None
			self.ebpCiqName = None
			self.ebcCiqCode = None
			self.ebcCiqName = None
			self.spSoNo = None

		def getapiname(self):
			return 'jingdong.eclp.order.addDeclareOrderCustoms'

			





