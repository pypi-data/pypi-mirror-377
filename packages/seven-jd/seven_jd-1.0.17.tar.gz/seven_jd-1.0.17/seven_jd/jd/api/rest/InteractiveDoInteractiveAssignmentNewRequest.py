from seven_jd.jd.api.base import RestApi

class InteractiveDoInteractiveAssignmentNewRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.sysParam = None
			self.interactiveAssignmentParam = None

		def getapiname(self):
			return 'jingdong.interactive.doInteractiveAssignmentNew'

			
	

class ClientInfo(object):
		def __init__(self):
			"""
			"""
			self.extParam = None
			self.appName = None
			self.jda = None
			self.ip = None
			self.idfa = None
			self.d_model = None
			self.site = None
			self.partner = None
			self.imei = None
			self.aid = None


class SysParam(object):
		def __init__(self):
			"""
			"""
			self.sysExt = None
			self.sysCode = None
			self.htCode = None
			self.clientInfo = None
			self.forceBot = None
			self.sourceCode = None
			self.privateKey = None
			self.vtCode = None
			self.mcChannel = None
			self.page = None


class InteractiveAssignmentParam(object):
		def __init__(self):
			"""
			"""
			self.ext = None
			self.itemId = None
			self.actionType = None
			self.pin = None
			self.bizExtParams = None
			self.encryptProjectId = None
			self.encryptAssignmentId = None
			self.completionFlag = None
			self.open_id_buyer = None
			self.xid_buyer = None





