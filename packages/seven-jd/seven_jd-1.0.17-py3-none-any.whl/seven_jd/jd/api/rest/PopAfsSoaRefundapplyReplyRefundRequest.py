from seven_jd.jd.api.base import RestApi

class PopAfsSoaRefundapplyReplyRefundRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.status = None
			self.id = None
			self.checkUserName = None
			self.remark = None
			self.rejectType = None
			self.outWareStatus = None

		def getapiname(self):
			return 'jingdong.pop.afs.soa.refundapply.replyRefund'

			





