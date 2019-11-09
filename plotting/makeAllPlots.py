#
# read MC file root files and histogram by group 
#

from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, TLegend, TAxis, THStack
import tdrstyle
from ROOT import gSystem, gStyle, gROOT, kTRUE
gROOT.SetBatch(True) # don't pop up any plots
gStyle.SetOptStat(0) # don't show any stats
from math import sqrt
def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./VBF_sync_input.root',help="File to be analyzed.")
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-y","--year",default=2016,type=int,help="Year for data.")
    parser.add_argument("-l","--LTcut",default=0.,type=float,help="H_LTcut")
    parser.add_argument("-s","--sign",default='OS',help="Opposite or same sign (OS or SS).")
    parser.add_argument("--MConly",action='store_true',help="MC only") 
    parser.add_argument("--looseCuts",action='store_true',help="Loose cuts")
    parser.add_argument("--unBlind",action='store_true',help="Unblind signal region for OS")
    
    return parser.parse_args()

class dupeDetector() :
    
    def __init__(self):
        self.nCalls = 0 
        self.runEventList = []

    def checkEvent(self,entry) :
        self.nCalls += 1 
        runEvent = "{0:d}:{1:d}".format(entry.run,entry.evt)
        if runEvent in self.runEventList :
            #print("Event in list: runEventList={0:s}".format(str(self.runEventList)))
            return True
        else :
            self.runEventList.append(runEvent)
            #print("New event: runEventList={0:s}".format(str(self.runEventList)))
            return False

    def printSummary(self) :
        print("Duplicate Event Summary: Calls={0:d} Unique Events={1:d}".format(self.nCalls,len(self.runEventList)))
        return


def OverFlow(htest) :

    nb = htest.GetNbinsX()

    lastbincont = htest.GetBinContent(nb)
    overbincont = htest.GetBinContent(nb+1)
    lastbinerror = htest.GetBinError(nb)
    overbinerror = htest.GetBinError(nb+1)

    htest.SetBinContent(nb, 0)
    htest.SetBinContent(nb, lastbincont+overbincont)
    htest.SetBinContent(nb+1, 0.)
    htest.SetBinError(nb, sqrt(lastbinerror*lastbinerror + overbinerror*overbinerror))
    htest.SetBinError(nb+1, 0.)



    #return htest


def getFakeWeights(f1,f2) :
    w1 = f1/(1.-f1)
    w2 = f2/(1.-f2)
    w0 = w1*w2
    return w1, w2, w0

def trigweight(e,cat) :
    trigw = 1.
    '''
    if cat == 'eeet' or cat == 'mmmt' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC == 0. : trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T1_MC) ))

	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. : trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ))

	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ))

    if cat == 'eemt' or cat == 'mmet' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC == 0. : trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC != 0. : trigw = float(   (e.trig_Lp_Data/e.trig_Lp_MC) * (e.trig_Lp_Data/e.trig_Lp_MC)   )
	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. : trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC != 0. : trigw = float(   (e.trig_Lm_Data/e.trig_Lm_MC) * (e.trig_Lm_Data/e.trig_Lm_MC)   )
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ) )
	    if trig_T1_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) )  * float(e.trig_T1_Data/e.trig_T1_MC) )

    if cat == 'eeem' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0. : trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0. : trigw = float(e.trig_Lp_Data/e.trig_Lp_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T1_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T1_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))

	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0. : trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0. : trigw = float(e.trig_Lm_Data/e.trig_Lm_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))

	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0. : trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ))
	    if trig_T1_MC == 0. and trig_T2_MC != 0. : trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))
	    if trig_T1_MC != 0. and trig_T2_MC == 0. : trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ) 
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))

    if cat == 'mmem' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lp_Data/e.trig_Lp_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T2_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T2_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))

	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lm_Data/e.trig_Lm_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))

	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC == 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))
	    if trig_T1_MC == 0. and trig_T2_MC != 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ) 
	    if trig_T1_MC != 0. and trig_T2_MC != 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))
    '''
    return trigw



args = getArgs()
era=str(args.year)

groups = ['Signal','Reducible','Rare','ZZ','data']
lumi = 1000.
tauID_w = 1.

weights= {''}
weights_muTotauFR={''}
weights_elTotauFR={''}


if era == '2016' : 
    weights = {'lumi':35.92, 'tauID_w' :0.87, 'tauES_DM0' : -0.6, 'tauES_DM1' : -0.5,'tauES_DM10' : 0.0, 'mutauES_DM0' : -0.2, 'mutauES_DM1' : 1.5, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 9.5}
    weights_muTotauFR = {'lmuFR_lt0p4' : 1.22, 'lmuFR_0p4to0p8' : 1.12, 'lmuFR_0p8to1p2' : 1.26, 'lmuFR_1p2to1p7' : 1.22, 'lmuFR_1p7to2p3' : 2.39 , 'tmuFR_lt0p4' : 1.47, 'tmuFR_0p4to0p8' : 1.55, 'tmuFR_0p8to1p2' : 1.33, 'tmuFR_1p2to1p7' : 1.72, 'tmuFR_1p7to2p3' : 2.50 }
    weights_elTotauFR = {'lelFR_lt1p46' : 1.21, 'lelFR_gt1p559' : 1.38, 'telFR_lt1p46' : 1.40, 'telFR_gt1p559' : 1.90}



if era == '2017' : 
    weights = {'lumi':41.53, 'tauID_w' :0.89, 'tauES_DM0' : 0.7, 'tauES_DM1' : -0.2,'tauES_DM10' : 0.1, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.3, 'eltauES_DM1' : 3.6}
    weights_muTotauFR = { 'lmuFR_lt0p4' : 1.06, 'lmuFR_0p4to0p8' : 1.02, 'lmuFR_0p8to1p2' : 1.10, 'lmuFR_1p2to1p7' : 1.03, 'lmuFR_1p7to2p3' : 1.94 , 'tmuFR_lt0p4' : 1.17, 'tmuFR_0p4to0p8' : 1.29, 'tmuFR_0p8to1p2' : 1.14, 'tmuFR_1p2to1p7' : 0.94, 'tmuFR_1p7to2p3' : 1.61}
    weights_elTotauFR = {'lelFR_lt1p46' : 1.09, 'lelFR_gt1p559' : 1.19, 'telFR_lt1p46' : 1.80, 'telFR_gt1p559' : 1.53}

if era == '2018' : 
    weights = {'lumi':59.74, 'tauID_w' :0.90, 'tauES_DM0' : -1.3, 'tauES_DM1' : -0.5,'tauES_DM10' : -1.2, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 0.0}
    weights_muTotauFR = { 'lmuFR_lt0p4' : 1., 'lmuFR_0p4to0p8' : 1., 'lmuFR_0p8to1p2' : 1., 'lmuFR_1p2to1p7' : 1., 'lmuFR_1p7to2p3' : 1. , 'tmuFR_lt0p4' : 1., 'tmuFR_0p4to0p8' : 1., 'tmuFR_0p8to1p2' : 1., 'tmuFR_1p2to1p7' : 1., 'tmuFR_1p7to2p3' : 1.}
    weights_elTotauFR = {'lelFR_lt1p46' : 1., 'lelFR_gt1p559' : 1., 'telFR_lt1p46' : 1., 'telFR_gt1p559' : 1.}


'''
if era == '2016' : 
    lumi *= 35.92
    tauID_w = 0.87

if era == '2017' : 
    lumi *= 41.53
    tauID_w = 0.89

if era == '2018' : 
    lumi *= 59.74
    tauID_w = 0.90
'''


#cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem', 9:'et', 10:'mt', 11:'tt' }
groups = ['Signal','Reducible','Rare','ZZ','data']
tightCuts = not args.looseCuts 
dataDriven = not args.MConly

# use this utility class to screen out duplicate events
DD = {}
for cat in cats.values() :
    DD[cat] = dupeDetector()

# dictionary where the group is the key
hMC = {}


# dictionary where the nickName is the key
nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}

for group in groups :
    nickNames[group] = []

#       0                 1       2        3        4        5            6
# GluGluHToTauTau       Signal  48.58   9259000 198813970.4             /GluGluHToTauTau_...

# make a first pass to get the weights
#for line in open('./MC/MCsamples_small_'+era+'.csv','r').readlines() :
for line in open('./MC/MCplots_'+era+'.csv','r').readlines() :
    vals = line.split(',')
    nickName = vals[0]
    group = vals[1]
    nickNames[group].append(nickName)
    xsec[nickName] = float(vals[2])
    totalWeight[nickName] = float(vals[4])
    sampleWeight[nickName]= lumi*xsec[nickName]/totalWeight[nickName]
    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

# Stitch the DYJets and WJets samples

for i in range(1,5) :
    nn = 'DY{0:d}JetsToLL'.format(i)
    if 'DYJetsToLL' in totalWeight : sampleWeight[nn] = lumi/(totalWeight['DYJetsToLL']/xsec['DYJetsToLL'] + totalWeight[nn]/xsec[nn])

for i in range(1,4) :
    nn = 'W{0:d}JetsToLNu'.format(i)
    if 'WJetsToLNu' in totalWeight : sampleWeight[nn] = lumi/(totalWeight['WJetsToLNu']/xsec['WJetsToLNu'] + totalWeight[nn]/xsec[nn])

# now add the data
#for eras in ['2017B','2017C','2017D','2017E','2017F'] :
for eras in ['2016'] :
    #for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
    #for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
    for dataset in ['SingleMuon'] :
        nickName = '{0:s}_Run{1:s}'.format(dataset,eras)
        totalWeight[nickName] = 1.
        sampleWeight[nickName] = 1.
        nickNames['data'].append(nickName)
#####################################3


print("tightCuts={0}".format(tightCuts))
if tightCuts :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}.root'.format(args.year,args.sign,int(args.LTcut))
    if args.MConly :
        print("args.MConly is TRUE")
        outFileName = outFileName.replace('.root','_MC.root') 
else :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_loose.root'.format(args.year,args.sign,int(args.LTcut))
    
print("Opening {0:s} as output.".format(outFileName))
fOut = TFile( outFileName, 'recreate' )

#fe, fm, ft_et, ft_mt, f1_tt, f2_tt   = 0.0456, 0.0935, 0.1391, 0.1284, 0.0715, 0.0609
# values with nbtag = 0 cut 
fe, fm, ft_et, ft_mt, f1_tt, f2_tt   = 0.0390, 0.0794, 0.1397, 0.1177, 0.0756, 0.0613
fW1, fW2, fW0 = {}, {}, {}
fW1['et'], fW2['et'], fW0['et'] = getFakeWeights(fe,ft_et)
fW1['mt'], fW2['mt'], fW0['mt'] = getFakeWeights(fm,ft_mt)
fW1['tt'], fW2['tt'], fW0['tt'] = getFakeWeights(f1_tt,f2_tt)
fW1['em'], fW2['em'], fW0['em'] = getFakeWeights(fe,fm)

global getsf,sf


plotSettings = { # [nBins,xMin,xMax,units]
        "pt_1":[100,0,500,"[Gev]","P_{T}(#tau_{1})"],
        "eta_1":[100,-4,4,"","#eta(l_{1})"],
        "phi_1":[100,-4,4,"","#phi(l_{1})"],
        "iso_1":[20,0,1,"","relIso(l_{1})"],
        "dz_1":[10,0,0.2,"[cm]","d_{z}(l_{1})"],
        "d0_1":[10,0,0.2,"[cm]","d_{xy}(l_{1})"],
        "q_1":[10,-5,5,"","charge(l_{1})"],

        "pt_2":[100,0,500,"[Gev]","P_{T}(l_{2})"],
        "eta_2":[100,-4,4,"","#eta(l_{2})"],
        "phi_2":[100,-4,4,"","#phi(l_{2})"],
        "iso_2":[20,0,1,"","relIso(l_{2})"],
        "dz_2":[10,0,0.2,"[cm]","d_{z}(l_{2})"],
        "d0_2":[10,0,0.2,"[cm]","d_{xy}(l_{2})"],
        "q_2":[10,-5,5,"","charge(l_{2})"],

        "njets":[10,-0.5,9.5,"","nJet"],
        #"Jet_pt":[100,0,500,"[GeV]","Jet P_{T}"], 
        #"Jet_eta":[64,-3.2,3.2,"","Jet #eta"],
        #"Jet_phi":[100,-4,4,"","Jet #phi"],
        #"Jet_ht":[100,0,800,"[GeV]","H_{T}"],

        "jpt_1":[100,0,500,"[GeV]","Jet^{1} P_{T}"], 
        "jeta_1":[64,-3.2,3.2,"","Jet^{1} #eta"],
        "jpt_2":[100,0,500,"[GeV]","Jet^{2} P_{T}"], 
        "jeta_2":[64,-3.2,3.2,"","Jet^{2} #eta"],

        "bpt_1":[100,0,500,"[GeV]","BJet^{1} P_{T}"], 
        "bpt_2":[100,0,500,"[GeV]","BJet^{2} P_{T}"], 

        "nbtag":[5,-0.5,4.5,"","nBTag"],
        #"nbtagLoose":[10,0,10,"","nBTag Loose"],
        #"nbtagTight":[5,0,5,"","nBTag Tight"],
        "beta_1":[64,-3.2,3.2,"","BJet^{1} #eta"],
        "beta_2":[64,-3.2,3.2,"","BJet^{2} #eta"],

        "met":[100,0,500,"[GeV]","#it{p}_{T}^{miss}"], 
        "met_phi":[100,-4,4,"","#it{p}_{T}^{miss} #phi"], 
        "puppi_phi":[100,-4,4,"","PUPPI#it{p}_{T}^{miss} #phi"], 
        "puppimet":[100,0,500,"[GeV]","#it{p}_{T}^{miss}"], 
        #"mt_tot":[100,0,1000,"[GeV]"], # sqrt(mt1^2 + mt2^2)
        #"mt_sum":[100,0,1000,"[GeV]"], # mt1 + mt2
        "ll_lmass":[100,0,500,"[GeV]","l^{+} mass"],
        "mll":[100,0,500,"[Gev]","m(l^{+}l^{-})"],
        "ll_pt_p":[100,0,500,"[GeV]","P_{T}l^{-}"],
        "ll_phi_p":[100,-4,4,"","#phi(l_^{-})"],
        "ll_eta_p":[100,-4,4,"","#eta(l_^{-})"],
        "ll_pt_m":[100,0,500,"[GeV]","P_{T}l^{-}"],
        "ll_phi_m":[100,-4,4,"","#phi(l_^{-})"],
        "ll_eta_m":[100,-4,4,"","#eta(l_^{-})"],

        "m_sv":[100,0,500,"[Gev]","m(#ttau#tau)"],
        "mt_sv":[100,0,500,"[Gev]","m_{T}(#tau#tau)"],
        "pt_tt":[100,0,500,"[GeV]","P_{T}(#tau#tau)"],
        "mt_tot":[100,0,500,"[GeV]","m_{T}tot(#tau#tau)"],



        }






canvasDict = {}
legendDict = {}
hBkgdStacksDict = {} # maps plotVar to the stack of background
for cat in cats.values()[0:8] :
    for plotVar in plotSettings: # add an entry to the plotVar:hist dictionary
        canvasDict.update({plotVar:TCanvas("c_"+plotVar+"_"+cat,"c_"+plotVar+"_"+cat,10,20,1000,700)})
        legendDict.update({plotVar:TLegend(.45,.75,.90,.90)})
        title = plotVar+" ("+cat+")"
        hBkgdStacksDict.update({plotVar:THStack(plotVar+"_bkgdStack", title)})
        title = "cutflow ("+cat+")"
        #hBkgdCutflowStack = THStack("cutflow_bkgdStack", title)

for group in groups :
    fOut.cd()
    hMC[group] = {}
    for cat in cats.values()[0:8] :
        hMC[group][cat] = {}
        for plotVar in plotSettings:
            hMC[group][cat][plotVar] = {}
            nBins = plotSettings[plotVar][0]
            xMin = plotSettings[plotVar][1]
            xMax = plotSettings[plotVar][2]
            units = plotSettings[plotVar][3]
            lTitle = plotSettings[plotVar][4]
            hName = 'h{0:s}_{1:s}_{2:s}'.format(group,cat,plotVar)
            
            binwidth = (xMax - xMin)/nBins
            hMC[group][cat][plotVar] = TH1D(hName,hName,nBins,xMin,xMax)
            hMC[group][cat][plotVar].SetDefaultSumw2()
            hMC[group][cat][plotVar].GetXaxis().SetTitle(lTitle)
            if 'GeV' in units : hMC[group][cat][plotVar].GetYaxis().SetTitle("Events / "+str(binwidth)+" {0:s}".format(units))
            if 'GeV' not in units : hMC[group][cat][plotVar].GetYaxis().SetTitle("Events / "+str(binwidth))

            #print '=======', nBins, xMin, xMax, hMC[group][cat][plotVar].GetName(), hMC[group][cat][plotVar].GetTitle()

    print("\nInstantiating TH1D {0:s}".format(hName))
    print("      Nickname                 Entries    Wt/Evt  Ngood   Tot Wt")
    for nickName in nickNames[group] :
        isData = False 
        inFileName = '../MC/condor/{0:s}_{1:s}/{0:s}_{1:s}.root'.format(nickName,era)
        if group == 'data' :
            isData = True
            inFileName = './data/{0:s}/{0:s}.root'.format(nickName)
        try :
            inFile = TFile.Open(inFileName)
            inFile.cd()
            inTree = inFile.Get("Events")
            nentries = inTree.GetEntries()
        except AttributeError :
            print("  Failure on file {0:s}".format(inFileName))
            exit()

        # resume here
        nEvents, trigw, totalWeight = 0, 1., 0.
        sWeight = sampleWeight[nickName]
        DYJets = (nickName == 'DYJetsToLL')
        WJets  = (nickName == 'WJetsToLNu')

        for i, e in enumerate(inTree) :
            hGroup = group
            #if e.nbtag > 0 : continue
            sw = sWeight
            if e.LHE_Njets > 0 :
                if DYJets : sw = sampleWeight['DY{0:d}JetsToLL'.format(e.LHE_Njets)]
                if WJets  : sw = sampleWeight['W{0:d}JetsToLNu'.format(e.LHE_Njets)] 

            weight = e.weight * sw

            ww = weight
            #s = sf.checkFile()

            cat = cats[e.cat]
            #apply tau-ID
            pfmet_tree = e.met
            puppimet_tree = e.puppimet
            '''
            if cat[2:] == 'et' or cat[2:]  == 'mt' or  cat[2:] == 'tt' :
            
                #tau energy scale
                if  cat[2:] == 'tt' and  e.gen_match_1 == 5 : 
                    weight *= weights['tauID_w'] # tauID SF
                    if e.decayMode_1 == 0 : e.pt_1 *= (1+ weights['tauES_DM0'])  #tau ES
                    if e.decayMode_1 == 1 : e.pt_1 *= (1+ weights['tauES_DM1'])  ##TODO CHANGE MASS of TAU TO PION
                    if e.decayMode_1 == 10 : e.pt_1 *= (1+ weights['tauES_DM10'])

                if e.gen_match_2 == 5 : 
                    weight *= weights['tauID_w'] # tauID SF

                    if e.decayMode_2 == 0 : e.pt_2 *= (1+ weights['tauES_DM0'])  #tau ES
                    if e.decayMode_2 == 1 : e.pt_2 *= (1+ weights['tauES_DM1'])  ##TODO CHANGE MASS of TAU TO PION
                    if e.decayMode_2 == 10 : e.pt_2 *= (1+ weights['tauES_DM10'])

                #now shift the met as well - the problem is that we don't propagate that to m_tt
                if e.gen_match_1 == 5 or e.gen_match_2 == 5 :
                    if e.decayMode_1 == 0 or e.decayMode_2 == 0 : 
                        pfmet_tree *= (1+ weights['tauES_DM0'])  #tau ES
                        puppimet_tree *= (1+ weights['tauES_DM0'])
                    if e.decayMode_1 == 1 or e.decayMode_2 == 1 : 
                        pfmet_tree *= (1+ weights['tauES_DM1'])  #tau ES
                        puppimet_tree *= (1+ weights['tauES_DM1'])
                    if e.decayMode_1 == 10 or e.decayMode_2 == 10 : 
                        pfmet_tree *= (1+ weights['tauES_DM10'])  #tau ES
                        puppimet_tree *= (1+ weights['tauES_DM10'])

                #mu->tau FR
                if e.gen_match_1 == 2 or e.gen_match_1 == 4  :
                    if cat[2:] == 'et' or cat[2:] == 'tt' :
                        if abs(e.eta_1) < 0.4 : weight *= weights_muTotauFR['lmuFR_lt0p4']
                        if abs(e.eta_1) > 0.4 and abs(e.eta_1 < 0.8) : weight *= weights_muTotauFR['lmuFR_0p4to0p8']
                        if abs(e.eta_1) > 0.8 and abs(e.eta_1 < 1.2) : weight *= weights_muTotauFR['lmuFR_0p8to1p2']
                        if abs(e.eta_1) > 1.2 and abs(e.eta_1 < 1.7) : weight *= weights_muTotauFR['lmuFR_1p2to1p7']
                        if abs(e.eta_1) > 1.7 and abs(e.eta_1 < 2.3) : weight *= weights_muTotauFR['lmuFR_1p7to2p3']
                    if cat[2:] == 'mt' :
                        if abs(e.eta_1) < 0.4 : weight *= weights_muTotauFR['tmuFR_lt0p4']
                        if abs(e.eta_1) > 0.4 and abs(e.eta_1 < 0.8) : weight *= weights_muTotauFR['tmuFR_0p4to0p8']
                        if abs(e.eta_1) > 0.8 and abs(e.eta_1 < 1.2) : weight *= weights_muTotauFR['tmuFR_0p8to1p2']
                        if abs(e.eta_1) > 1.2 and abs(e.eta_1 < 1.7) : weight *= weights_muTotauFR['tmuFR_1p2to1p7']
                        if abs(e.eta_1) > 1.7 and abs(e.eta_1 < 2.3) : weight *= weights_muTotauFR['tmuFR_1p7to2p3']
                #e->tau FR
                if e.gen_match_1 == 1 or e.gen_match_1 == 3  :
                    if cat[2:] == 'et' or cat[2:] == 'tt' :
                        if abs(e.eta_1) < 1.460 : weight *= weights_elTotauFR['lelFR_lt1p46']
                        if abs(e.eta_1) >= 1.559 : weight *= weights_elTotauFR['lelFR_gt1p559']
                    if cat[2:] == 'mt' :
                        if abs(e.eta_1) < 1.460 : weight *= weights_elTotauFR['telFR_lt1p46']
                        if abs(e.eta_1) >= 1.559 : weight *= weights_elTotauFR['telFR_gt1p559']


                if e.gen_match_2 == 2 or e.gen_match_2 == 4  :
                    if cat[2:] == 'et' or cat[2:] == 'tt' :
                        if abs(e.eta_2) < 0.4 : weight *= weights_muTotauFR['lmuFR_lt0p4']
                        if abs(e.eta_2) > 0.4 and abs(e.eta_2 < 0.8) : weight *= weights_muTotauFR['lmuFR_0p4to0p8']
                        if abs(e.eta_2) > 0.8 and abs(e.eta_2 < 1.2) : weight *= weights_muTotauFR['lmuFR_0p8to1p2']
                        if abs(e.eta_2) > 1.2 and abs(e.eta_2 < 1.7) : weight *= weights_muTotauFR['lmuFR_1p2to1p7']
                        if abs(e.eta_2) > 1.7 and abs(e.eta_2 < 2.3) : weight *= weights_muTotauFR['lmuFR_1p7to2p3']
                    if cat[2:] == 'mt' :
                        if abs(e.eta_2) < 0.4 : weight *= weights_muTotauFR['tmuFR_lt0p4']
                        if abs(e.eta_2) > 0.4 and abs(e.eta_2 < 0.8) : weight *= weights_muTotauFR['tmuFR_0p4to0p8']
                        if abs(e.eta_2) > 0.8 and abs(e.eta_2 < 1.2) : weight *= weights_muTotauFR['tmuFR_0p8to1p2']
                        if abs(e.eta_2) > 1.2 and abs(e.eta_2 < 1.7) : weight *= weights_muTotauFR['tmuFR_1p2to1p7']
                        if abs(e.eta_2) > 1.7 and abs(e.eta_2 < 2.3) : weight *= weights_muTotauFR['tmuFR_1p7to2p3']

                if e.gen_match_2 == 1 or e.gen_match_2 == 3  :
                    if cat[2:] == 'et' or cat[2:] == 'tt' :
                        if abs(e.eta_2) < 1.460 : weight *= weights_elTotauFR['lelFR_lt1p46']
                        if abs(e.eta_2) >= 1.559 : weight *= weights_elTotauFR['lelFR_gt1p559']
                    if cat[2:] == 'mt' :
                        if abs(e.eta_2) < 1.460 : weight *= weights_elTotauFR['telFR_lt1p46']
                        if abs(e.eta_2) >= 1.559 : weight *= weights_elTotauFR['telFR_gt1p559']
                        

                 #weights_muTotauFR = {'lmuFR_lt0p4' : 1.22, 'lmuFR_0p4to0p8' : 1.12, 'lmuFR_0p8to1p2' : 1.26, 'lmuFR_1p2to1p7' : 1.22, 'lmuFR_1p7to2p3' : 2.39 , 'tmuFR_lt0p4' : 1.47, 'tmuFR_0p4to0p8' : 1.55, 'tmuFR_0p8to1p2' : 1.33, 'tmuFR_1p2to1p7' : 1.72, 'tmuFR_1p7to2p3' : 2.50 }

                 #weights_elTotauFR = {'lelFR_lt1p46' : 1., 'lelFR_gt1p559' : 1., 'telFR_lt1p46' : 1., 'telFR_gt1p559' : 1.}
                '''    
            if tightCuts :
                if cat[2:] == 'et' : tight1 = e.iso_1 > 0.5 
                if cat[2:] == 'mt' : tight1 = e.iso_1 < 0.25 and e.iso_1_ID > 0.5
                if cat[2:] == 'tt' : tight1 = e.iso_1_ID > 15
                tight2 = e.iso_2_ID > 15
                if cat[2:] == 'em' :
                    tight1 = e.iso_1 > 0.5
                    tight2 = e.iso_2 < 0.25 and e.iso_2_ID > 0.5
                    
                if group == 'data' :
                    if dataDriven :
                        hGroup = 'Reducible'
                        if not tight1 and tight2 : ww = fW1[cat[2:]]
                        elif tight1 and not tight2 : ww = fW2[cat[2:]]
                        elif not (tight1 or tight2) : ww = -fW0[cat[2:]]
                        else :
                            ww = 1.
                            hGroup = 'data'
                    else :
                        hGroup = 'data'
                        #print("group = data  cat={0:s} tight1={1} tight2={2} ww={3:f}".format(cat,tight1,tight2,ww))
                        if not (tight1 and tight2) : continue 
                        
                else : 
                    if not (tight1 and tight2) : continue
                    #print("Good MC event: group={0:s} nickName={1:s} cat={2:s} gen_match_1={3:d} gen_match_2={4:d}".format(
                    #    group,nickName,cat,e.gen_match_1,e.gen_match_2))
                    if dataDriven :   # include only events with MC matching
                        if cat[2] == 'e' or cat[2] == 'm':
                            if not (e.gen_match_1 == 1 or e.gen_match_1 == 15) : continue
                        else :
                            if not e.gen_match_1 == 5 : continue
                        if cat[3] == 'e' or cat[3] == 'm' :
                            if not (e.gen_match_2 == 1 or e.gen_match_2 == 15) : continue
                        else : 
                            if not e.gen_match_2 == 5 : continue
                                        
                #elif group == 'Rare' or group == 'ZZ4L' or group == 'Signal' :
                #    if not (tight1 and tight2) : continue         
                                        
            if args.sign == 'SS':
                if e.q_1*e.q_2 < 0. : continue
            else :
                if e.q_1*e.q_2 > 0. : continue
                if hGroup == 'data' and not args.unBlind and e.m_sv > 80. and e.m_sv < 140. : continue                 
            H_LT = e.pt_1 + e.pt_2
            if H_LT < args.LTcut : continue
            if group == 'data' :
                if DD[cat].checkEvent(e) : continue 
            if cat == 'mmtt' :
                totalWeight += ww
                nEvents += 1


            trigw_ = 1.#trigweight(e,cat)

            #if e.is_trig == 1 :  
            if 1 == 1 : 
                for plotVar in plotSettings:
                    #print plotVar
                    val = getattr(e, plotVar, None)
		    if val is not None: 
                        hMC[hGroup][cat][plotVar].Fill(val,ww*trigw_)
                        #print hGroup, cat, plotVar, val
                        #if val < hGroup][cat][plotVar].GetNbinsX() * hGroup][cat][plotVar].GetBinWidth(1) : hMC[hGroup][cat][plotVar].Fill(val,ww*trigw_)
                        #else : hMC[hGroup][cat][plotVar].Fill(val,ww*trigw_)
                    



        print("{0:30s} {1:7d} {2:10.6f} {3:5d} {4:8.3f}".format(nickName,nentries,sampleWeight[nickName],nEvents,totalWeight))
        inFile.Close()
    fOut.cd()
    for cat in cats.values()[0:8] : 
        for plotVar in plotSettings:
            OverFlow(hMC[group][cat][plotVar])
            hMC[group][cat][plotVar].Write()

for cat in cats.values():
    print("Duplicate summar for {0:s}".format(cat))
    DD[cat].printSummary()
    


