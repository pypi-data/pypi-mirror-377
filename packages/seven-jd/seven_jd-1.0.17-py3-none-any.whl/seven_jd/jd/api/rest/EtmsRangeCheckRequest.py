from seven_jd.jd.api.base import RestApi

class EtmsRangeCheckRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.salePlat = None
			self.customerCode = None
			self.orderId = None
			self.goodsType = None
			self.wareHouseCode = None
			self.receiveAddress = None
			self.transType = None
			self.senderProvinceId = None
			self.senderCityId = None
			self.senderCountyId = None
			self.senderTownId = None
			self.receiverProvinceId = None
			self.receiverCityId = None
			self.receiverCountyId = None
			self.receiverTownId = None
			self.sendTime = None
			self.isCod = None
			self.siteId = None
			self.siteName = None
			self.addedService = None
			self.promiseTimeType = None
			self.senderAddress = None
			self.pickupSiteId = None
			self.pickupSiteCode = None
			self.siteCode = None
			self.senderProvince = None
			self.senderCity = None
			self.senderCounty = None
			self.senderTown = None
			self.receiverProvince = None
			self.receiverCity = None
			self.receiverCounty = None
			self.receiverTown = None
			self.settleType = None
			self.requireDeliveryPresortMode = None
			self.receiveOAID = None

		def getapiname(self):
			return 'jingdong.etms.range.check'

			





