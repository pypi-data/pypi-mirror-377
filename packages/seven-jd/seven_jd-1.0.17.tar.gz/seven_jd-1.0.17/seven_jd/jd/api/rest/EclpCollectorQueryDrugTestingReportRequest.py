from seven_jd.jd.api.base import RestApi

class EclpCollectorQueryDrugTestingReportRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.status = None
			self.drugBatchNo = None
			self.goodsNo = None
			self.isvGoodsNo = None

		def getapiname(self):
			return 'jingdong.eclp.collector.queryDrugTestingReport'

			





