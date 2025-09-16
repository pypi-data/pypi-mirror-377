from seven_jd.jd.api.base import RestApi

class MktFeatureProductQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.param1 = None
			self.param2 = None

		def getapiname(self):
			return 'jingdong.mkt.feature.product.query'

			
	

class Param1(object):
		def __init__(self):
			"""
			"""


class Param2(object):
		def __init__(self):
			"""
			"""
			self.requestId = None





