from seven_jd.jd.api.base import RestApi

class ComJdExpressDispatcherApiServiceFetchGoodsCalendarApiFetchGoodsBackwardCalendarRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.districtName = None
			self.fullAddress = None
			self.districtCode = None
			self.townName = None
			self.cityName = None
			self.provinceCode = None
			self.cityCode = None
			self.provinceName = None
			self.orderId = None
			self.detailAddress = None
			self.townCode = None

		def getapiname(self):
			return 'jingdong.com.jd.express.dispatcher.api.service.FetchGoodsCalendarApi.fetchGoodsBackwardCalendar'

			





