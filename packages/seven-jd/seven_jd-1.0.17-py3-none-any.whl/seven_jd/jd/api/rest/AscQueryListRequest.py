from seven_jd.jd.api.base import RestApi

class AscQueryListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.buId = None
			self.operatePin = None
			self.operateNick = None
			self.serviceId = None
			self.orderId = None
			self.applyTimeBegin = None
			self.applyTimeEnd = None
			self.finishTimeBegin = None
			self.finishTimeEnd = None
			self.verificationCode = None
			self.expressCode = None
			self.orderType = None
			self.processResult = None
			self.customerPin = None
			self.customerName = None
			self.customerTel = None
			self.approveTimeBegin = None
			self.approveTimeEnd = None
			self.pageNumber = None
			self.pageSize = None
			self.extJsonStr = None
			self.serviceStep = None
			self.serviceState = None
			self.serviceStatus = None
			self.updateTimeBegin = None
			self.updateTimeEnd = None
			self.remindFlag = None
			self.open_id_buyer = None
			self.xid_buyer = None

		def getapiname(self):
			return 'jingdong.asc.query.list'

			





