from seven_jd.jd.api.base import RestApi

class JosInteractWriteJosCreateMultiVenderInteractActivityRequest(RestApi):
		def __init__(self,domain='gw.api.360buy.com',port=80):
			"""
			"""
			RestApi.__init__(self,domain, port)
			self.clientSource = None
			self.param = None

		def getapiname(self):
			return 'jingdong.jos.interact.write.josCreateMultiVenderInteractActivity'

			
	

class ClientSource(object):
		def __init__(self):
			"""
			"""
			self.appName = None
			self.channelL = None


class InteractActivityExposureParam(object):
		def __init__(self):
			"""
			"""
			self.seqType = None
			self.seq = None
			self.sku = None


class InteractPrizeSkuParam(object):
		def __init__(self):
			"""
			"""
			self.skuId = None
			self.skuBindType = None


class InteractPrizeParam(object):
		def __init__(self):
			"""
			"""
			self.validateDay = None
			self.unionPrizeType = None
			self.useStartTime = None
			self.assetItemId = None
			self.prizeStartTime = None
			self.budgetNum = None
			self.ext = None
			self.awardType = None
			self.quota = None
			self.cycleUnit = None
			self.floatRatio = None
			self.autoStop = None
			self.useEndTime = None
			self.name = None
			self.batchKey = None
			self.prizeToken = None
			self.cycleNumber = None
			self.prizeRfId = None
			self.number = None
			self.interactPrizeSkuList = None
			self.prizeType = None
			self.discount = None
			self.bindType = None
			self.cycleLimitNumber = None
			self.prizeEndTime = None
			self.putKey = None
			self.expireType = None


class InteractPrizeRuleParam(object):
		def __init__(self):
			"""
			"""
			self.level = None
			self.interactPrizeList = None
			self.imageUrl = None
			self.repeatSend = None
			self.awardWorth = None
			self.sendNum = None
			self.sendType = None
			self.calculateType = None


class InteractActivityVenderParam(object):
		def __init__(self):
			"""
			"""
			self.unionType = None
			self.applyTime = None
			self.vender = None


class Param(object):
		def __init__(self):
			"""
			"""
			self.activityUrl = None
			self.isSinglePrize = None
			self.activityCycleUnit = None
			self.interactActivityExposureList = None
			self.endTime = None
			self.type = None
			self.startTime = None
			self.token = None
			self.interactPrizeRuleList = None
			self.sharePrize = None
			self.rfId = None
			self.showStartTime = None
			self.peopleModels = None
			self.sourceExt = None
			self.interactActivityVenderList = None
			self.actionExchange = None
			self.actionType = None
			self.source = None
			self.actionNumber = None
			self.imageLink = None
			self.activityExt = None
			self.expoType = None
			self.scene = None
			self.cycleNumer = None
			self.isPrize = None
			self.activityName = None
			self.channel = None
			self.activityUnionType = None
			self.supplierCode = None





