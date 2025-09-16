from seven_jd.jd.api.base import RestApi

class EclpMasterInsertCategoryRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.categoryNo = None
			self.categoryName = None
			self.superior = None
			self.sortNo = None
			self.memo = None
			self.operateUser = None
			self.operateTime = None

		def getapiname(self):
			return 'jingdong.eclp.master.insertCategory'

			





