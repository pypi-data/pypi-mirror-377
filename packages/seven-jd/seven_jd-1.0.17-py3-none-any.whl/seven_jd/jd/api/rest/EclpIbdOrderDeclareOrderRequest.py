from seven_jd.jd.api.base import RestApi

class EclpIbdOrderDeclareOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.customsOrder = None
			self.goodsList = None

		def getapiname(self):
			return 'jingdong.eclp.ibd.order.declareOrder'

			
	

class CustomsOrder(object):
		def __init__(self):
			"""
			"""
			self.isvUUID = None
			self.isvSource = None
			self.platformId = None
			self.platformName = None
			self.platformType = None
			self.spSoNo = None
			self.deptNo = None
			self.inJdwms = None
			self.salesPlatformCreateTime = None
			self.venderId = None
			self.venderName = None
			self.consigneeName = None
			self.consigneeMobile = None
			self.consigneePhone = None
			self.consigneeEmail = None
			self.consigneeAddress = None
			self.consigneePostcode = None
			self.consigneeCountry = None
			self.addressProvince = None
			self.addressCity = None
			self.addressCounty = None
			self.addressTown = None
			self.soType = None
			self.expectDate = None
			self.invoiceTitle = None
			self.invoiceContent = None
			self.declareOrder = None
			self.ccProvider = None
			self.ccProviderName = None
			self.postType = None
			self.pattern = None
			self.customs = None
			self.warehouseNo = None
			self.ebpCode = None
			self.ebpName = None
			self.ebcCode = None
			self.ebcName = None
			self.delivery = None
			self.discount = None
			self.discountNote = None
			self.istax = None
			self.taxTotal = None
			self.freight = None
			self.otherPrice = None
			self.goodsValue = None
			self.weight = None
			self.netWeight = None
			self.batchNumbers = None
			self.buyerRegNo = None
			self.buyerPhone = None
			self.buyerName = None
			self.buyerIdType = None
			self.buyerIdNumber = None
			self.senderName = None
			self.senderCompanyName = None
			self.senderCountry = None
			self.senderZip = None
			self.senderCity = None
			self.senderProvince = None
			self.senderTel = None
			self.senderAddr = None
			self.customsRemark = None
			self.declarePaymentList = None
			self.paymentType = None
			self.payCode = None
			self.payName = None
			self.payTransactionId = None
			self.currency = None
			self.paymentConfirmTime = None
			self.shouldPay = None
			self.receiveNo = None
			self.payRemark = None
			self.declareWaybill = None
			self.logisticsCode = None
			self.logisticsName = None
			self.bdOwnerNo = None
			self.logisticsNo = None
			self.packNo = None
			self.logisticsRemark = None
			self.isDelivery = None
			self.receivable = None
			self.consigneeRemark = None
			self.insuredPriceFlag = None
			self.insuredValue = None
			self.insuredFee = None
			self.shopNo = None
			self.isSupervise = None
			self.initalRequest = None
			self.initalResponse = None
			self.payTransactionIdYh = None
			self.isvParentId = None
			self.isvOrderIdList = None
			self.totalAmount = None
			self.verDept = None
			self.payType = None
			self.recpAccount = None
			self.recpCode = None
			self.recpName = None
			self.consNameEN = None
			self.consAddressEN = None
			self.senderNameEN = None
			self.senderCityEN = None
			self.senderAddrEN = None
			self.consigneeIdType = None
			self.wrapType = None


class Goods(object):
		def __init__(self):
			"""
			"""
			self.gnum = None
			self.isvGoodsNo = None
			self.spGoodsNo = None
			self.quantity = None
			self.price = None
			self.goodsRemark = None
			self.itemLink = None





