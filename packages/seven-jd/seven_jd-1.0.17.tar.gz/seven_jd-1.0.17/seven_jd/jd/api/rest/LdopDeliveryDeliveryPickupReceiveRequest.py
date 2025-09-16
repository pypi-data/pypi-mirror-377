from seven_jd.jd.api.base import RestApi

class LdopDeliveryDeliveryPickupReceiveRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.josPin = None
			self.salePlat = None
			self.customerCode = None
			self.orderId = None
			self.thrOrderId = None
			self.senderName = None
			self.senderAddress = None
			self.senderTel = None
			self.senderMobile = None
			self.receiveName = None
			self.receiveAddress = None
			self.receiveTel = None
			self.receiveMobile = None
			self.province = None
			self.city = None
			self.county = None
			self.town = None
			self.packageCount = None
			self.weight = None
			self.vloumLong = None
			self.vloumWidth = None
			self.vloumHeight = None
			self.vloumn = None
			self.description = None
			self.goodsMoney = None
			self.collectionValue = None
			self.collectionMoney = None
			self.guaranteeValue = None
			self.guaranteeValueAmount = None
			self.signReturn = None
			self.aging = None
			self.goodsType = None
			self.warehouseCode = None
			self.remark = None
			self.idNumber = None
			self.addedService = None
			self.senderCompany = None
			self.receiveCompany = None
			self.senderIdNumber = None
			self.senderIdType = None
			self.sendAndPickupType = None
			self.backName = None
			self.backMobileNo = None
			self.backTelNo = None
			self.backProvinceName = None
			self.backCityName = None
			self.backCountry = None
			self.backTown = None
			self.backDetailAddress = None
			self.productType = None
			self.pickUpStartTime = None
			self.pickUpEndTime = None
			self.open_id_seller = None
			self.xid_seller = None
			self.customerTel = None
			self.backAddress = None
			self.customerContract = None
			self.pickupOrderId = None
			self.pickupWeight = None
			self.pickupRemark = None
			self.pickupVolume = None
			self.isGuaranteeValue = None
			self.pickupGuaranteeValueAmount = None
			self.pickupGoodsType = None
			self.pickupBizType = None
			self.valueAddService = None
			self.pickupSenderIdNumber = None
			self.pickupSenderIdType = None
			self.productId = None
			self.snCode = None
			self.productName = None
			self.productCount = None
			self.skuAddService = None
			self.skuCheckOutShapes = None
			self.skuCheckAttachFile = None
			self.skuServiceRequirements = None
			self.promiseTimeType = None
			self.guaranteeSettleType = None
			self.packingSettleType = None
			self.freightSettleType = None

		def getapiname(self):
			return 'jingdong.ldop.delivery.deliveryPickupReceive'

			





