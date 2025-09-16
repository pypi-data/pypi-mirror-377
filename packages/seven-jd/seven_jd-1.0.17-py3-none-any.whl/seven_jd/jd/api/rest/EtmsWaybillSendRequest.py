from seven_jd.jd.api.base import RestApi

class EtmsWaybillSendRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deliveryId = None
			self.salePlat = None
			self.customerCode = None
			self.orderId = None
			self.thrOrderId = None
			self.selfPrintWayBill = None
			self.pickMethod = None
			self.packageRequired = None
			self.senderName = None
			self.senderAddress = None
			self.senderTel = None
			self.senderMobile = None
			self.senderPostcode = None
			self.receiveName = None
			self.receiveAddress = None
			self.province = None
			self.city = None
			self.county = None
			self.town = None
			self.provinceId = None
			self.cityId = None
			self.countyId = None
			self.townId = None
			self.siteType = None
			self.siteId = None
			self.siteName = None
			self.receiveTel = None
			self.receiveMobile = None
			self.postcode = None
			self.packageCount = None
			self.weight = None
			self.vloumLong = None
			self.vloumWidth = None
			self.vloumHeight = None
			self.vloumn = None
			self.description = None
			self.collectionValue = None
			self.collectionMoney = None
			self.guaranteeValue = None
			self.guaranteeValueAmount = None
			self.signReturn = None
			self.aging = None
			self.transType = None
			self.remark = None
			self.goodsType = None
			self.orderType = None
			self.shopCode = None
			self.orderSendTime = None
			self.warehouseCode = None
			self.areaProvId = None
			self.areaCityId = None
			self.shipmentStartTime = None
			self.shipmentEndTime = None
			self.idNumber = None
			self.addedService = None
			self.extendField1 = None
			self.extendField2 = None
			self.extendField3 = None
			self.extendField4 = None
			self.extendField5 = None
			self.senderCompany = None
			self.receiveCompany = None
			self.freightPre = None
			self.goods = None
			self.goodsCount = None
			self.promiseTimeType = None
			self.freight = None
			self.unpackingInspection = None
			self.fileUrl = None
			self.customerBoxCode = None
			self.customerBoxNumber = None
			self.pickUpStartTime = None
			self.pickUpEndTime = None
			self.receiveOAID = None

		def getapiname(self):
			return 'jingdong.etms.waybill.send'

			





