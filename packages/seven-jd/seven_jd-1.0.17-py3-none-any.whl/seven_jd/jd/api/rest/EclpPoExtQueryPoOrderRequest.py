from seven_jd.jd.api.base import RestApi

class EclpPoExtQueryPoOrderRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.poOrderNo = None
			self.queryItemFlag = None
			self.queryBoxFlag = None
			self.queryQcFlag = None
			self.queryPoRejectFlag = None
			self.queryBatAttrFlag = None

		def getapiname(self):
			return 'jingdong.eclp.po.ext.queryPoOrder'

			





