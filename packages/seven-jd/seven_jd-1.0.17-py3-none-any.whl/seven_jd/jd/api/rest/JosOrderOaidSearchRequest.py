from seven_jd.jd.api.base import RestApi

class JosOrderOaidSearchRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.request = None

		def getapiname(self):
			return 'jingdong.jos.order.oaid.search'

			
	

class Request(object):
		def __init__(self):
			"""
			"""
			self.receiverName = None
			self.receiverMobile = None
			self.startDate = None
			self.endDate = None
			self.sceneId = None





