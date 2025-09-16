from seven_jd.jd.api.base import RestApi

class LdopOmsPickupAttachmentQueryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.opeCode = None
			self.attachmentType = None
			self.busiId = None
			self.customerCode = None

		def getapiname(self):
			return 'jingdong.ldop.oms.pickup.attachment.query'

			





