from seven_jd.jd.api.base import RestApi

class EtmsWaybillcodeGetRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.preNum = None
			self.customerCode = None
			self.orderType = None

		def getapiname(self):
			return 'jingdong.etms.waybillcode.get'

			





