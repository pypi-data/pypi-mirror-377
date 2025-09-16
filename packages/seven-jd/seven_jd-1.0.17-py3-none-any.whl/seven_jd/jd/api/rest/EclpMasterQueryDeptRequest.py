from seven_jd.jd.api.base import RestApi

class EclpMasterQueryDeptRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.deptNos = None

		def getapiname(self):
			return 'jingdong.eclp.master.queryDept'

			





