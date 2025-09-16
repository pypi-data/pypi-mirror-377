from seven_jd.jd.api.base import RestApi

class EclpGoodsQueryGoodsRecordRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNo = None
			self.isvGoodsNo = None
			self.goodsNo = None
			self.pageNo = None
			self.pageSize = None
			self.startDate = None
			self.endDate = None

		def getapiname(self):
			return 'jingdong.eclp.goods.queryGoodsRecord'

			





