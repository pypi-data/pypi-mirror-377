from seven_jd.jd.api.base import RestApi

class Eclp2WmsInsideServiceLcLcJosQueryServiceFindLcVasListRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.lcNo = None

		def getapiname(self):
			return 'jingdong.eclp2.wms.inside.service.lc.LcJosQueryService.findLcVasList'

			





