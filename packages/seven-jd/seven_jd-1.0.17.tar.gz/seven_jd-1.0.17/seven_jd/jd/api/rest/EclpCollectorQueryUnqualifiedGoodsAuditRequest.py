from seven_jd.jd.api.base import RestApi

class EclpCollectorQueryUnqualifiedGoodsAuditRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.beginTime = None
			self.endTime = None
			self.deptNo = None
			self.goodsLevel = None

		def getapiname(self):
			return 'jingdong.eclp.collector.queryUnqualifiedGoodsAudit'

			





