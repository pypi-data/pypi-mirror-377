from seven_jd.jd.api.base import RestApi

class StationinfojosserviceUpdateRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.companyCode = None
			self.stationCode = None
			self.stationName = None
			self.stationAddress = None
			self.provinceId = None
			self.cityId = None
			self.countyId = None
			self.townId = None
			self.orgCode = None
			self.lat = None
			self.lng = None
			self.provinceName = None
			self.cityName = None
			self.countryName = None
			self.townName = None
			self.orgName = None
			self.areaCode = None
			self.areaName = None

		def getapiname(self):
			return 'jingdong.stationinfojosservice.update'

			





