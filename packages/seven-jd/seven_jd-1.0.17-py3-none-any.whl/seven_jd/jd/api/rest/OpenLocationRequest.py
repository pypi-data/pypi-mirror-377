from seven_jd.jd.api.base import RestApi

class OpenLocationRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.lng = None
			self.pin = None
			self.ip = None
			self.lat = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.open.location'

			





