from seven_jd.jd.api.base import RestApi

class InteractCenterApiServiceReadGetPersonLabelListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.appName = None
			self.channel = None

		def getapiname(self):
			return 'jingdong.interact.center.api.service.read.getPersonLabelList'

			





