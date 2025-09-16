from seven_jd.jd.api.base import RestApi

class PopOrderGetRemarkByModifyTimeRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.startTime = None
			self.endTime = None
			self.page = None
			self.sortTime = None

		def getapiname(self):
			return 'jingdong.pop.order.getRemarkByModifyTime'

			





