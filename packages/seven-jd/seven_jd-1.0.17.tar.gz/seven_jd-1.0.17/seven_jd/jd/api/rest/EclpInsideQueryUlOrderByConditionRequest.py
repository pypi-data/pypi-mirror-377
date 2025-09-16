from seven_jd.jd.api.base import RestApi

class EclpInsideQueryUlOrderByConditionRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.pageSize = None
			self.pageNum = None
			self.ulNo = None
			self.outUlNo = None
			self.deptNo = None
			self.warehouseNo = None
			self.allowReturnDest = None

		def getapiname(self):
			return 'jingdong.eclp.inside.queryUlOrderByCondition'

			





