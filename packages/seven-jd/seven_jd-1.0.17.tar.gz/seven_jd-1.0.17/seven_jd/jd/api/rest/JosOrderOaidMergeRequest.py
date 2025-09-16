from seven_jd.jd.api.base import RestApi

class JosOrderOaidMergeRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.request = None

		def getapiname(self):
			return 'jingdong.jos.order.oaid.merge'

			
	

class MergeItem(object):
		def __init__(self):
			"""
			"""
			self.orderId = None
			self.oaid = None


class Request(object):
		def __init__(self):
			"""
			"""
			self.mergeList = None





