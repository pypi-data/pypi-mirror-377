from seven_jd.jd.api.base import RestApi

class JzyxMktDataQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.param1 = None

		def getapiname(self):
			return 'jingdong.jzyx.mkt.data.query'

			
	

class Param1(object):
		def __init__(self):
			"""
			"""
			self.requestId = None
			self.stringSubs = None
			self.param = None





