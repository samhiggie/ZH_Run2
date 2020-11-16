from ROOT import gSystem, gStyle, gROOT, kTRUE, gDirectory, gPad
from ROOT import TCanvas, TH1D, TH1F, THStack, TFile, TPad, TLegend, TLatex, TLine, TAttMarker, TMarker, TColor
from ROOT import kBlack, kBlue, kMagenta, kOrange, kAzure, kRed, kGreen
from math import sqrt
import os
import sys



gROOT.SetBatch(kTRUE) # prevent displaying canvases

plotSettings = { # [nBins,xMin,xMax,units]
        #"m_sv_new":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"Z_Pt":[10,0,200,"[Gev]","P_T(l_{1}l_{2})"],
        #"m_sv_new_FM":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"m_sv_new_FMext":[20,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"m_sv_new_FMjall":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"m_sv_new_FMjallv2":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "m_sv_new_FMjall":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "lep_FWDH_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_0_75_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_75_150_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_0J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_GE1J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_GT250_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
}


cutflows=['hCutFlowPerGroup', 'hCutFlowPerGroupFM']

cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}

inFileName=str(sys.argv[2])
outFileName=str(sys.argv[3])


print 'in', inFileName, 'out', outFileName

fIn = TFile( inFileName, 'read' )

fOut = TFile( outFileName, 'recreate' )

fIn.cd()
groups=['Signal']
groups = ['bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','fakes','f1', 'f2', 'Signal','Other','Top','DY','WZ','ZZ','data', 'Reducible']
groupss = ['Signal','Other','Top','DY','WZ','ZZ','data', 'Reducible']


groupss = ['Other','ZZ','data', 'Reducible', 'ggZH', 'ZH', 'WH', 'HWW', 'ggHWW']
groupss = ['Other','ZZ','data', 'Reducible', 'ggZH', 'ZH', 'HWW', 'ggHWW']
#groupss = ['ZZ']

groups=groupss
fgroups = ['fakes', 'f1', 'f2']

h={}
hFM={}
hFMjall={}
hFMjallv2={}
hcut={}
hcutFM={}
hsignal={}
#hCutFlowPerGroup_data_mmmt

htest={}
for group in groups : 
    for icat, cat in cats.items()[0:8] :
	hname = "hCutFlowPerGroup_"+group+"_"+cat
        hcut[icat-1] = fIn.Get(hname)
	hname = "hCutFlowPerGroupFM_"+group+"_"+cat
        hcutFM[icat-1] = fIn.Get(hname)
	#fOut.cd()
        #hcut[icat-1].Write()
        
    try : 
	hcut[0].Add(hcut[4])
        
	hcut[1].Add(hcut[5])
	hcut[2].Add(hcut[6])
	hcut[3].Add(hcut[7])
	hcutFM[0].Add(hcutFM[4])
	hcutFM[1].Add(hcutFM[5])
	hcutFM[2].Add(hcutFM[6])
	hcutFM[3].Add(hcutFM[7])
	
	hname="hCutFlowPerGroup_"+group+"_llet"
	hcut[0].SetName(hname)
	hname="hCutFlowPerGroup_"+group+"_llmt"
	hcut[1].SetName(hname)
	hname="hCutFlowPerGroup_"+group+"_lltt"
	hcut[2].SetName(hname)
	hname="hCutFlowPerGroup_"+group+"_llem"
	hcut[3].SetName(hname)

	hname="hCutFlowPerGroupFM_"+group+"_llet"
	hcutFM[0].SetName(hname)
	hname="hCutFlowPerGroupFM_"+group+"_llmt"
	hcutFM[1].SetName(hname)
	hname="hCutFlowPerGroupFM_"+group+"_lltt"
	hcutFM[2].SetName(hname)
	hname="hCutFlowPerGroupFM_"+group+"_llem"
	hcutFM[3].SetName(hname)

	for i in range(4) : 
	    fOut.cd()
	    hcut[i].Write()
	    hcutFM[i].Write()
	#fOut.Close()
    except AttributeError : 
        continue


    gg=group
    group='h'+group
    for plotVar in plotSettings :
        for icat, cat in cats.items()[0:8] :
            h[icat-1]={}
            hname=group+"_"+cat+"_"+plotVar
	    h[icat-1] = fIn.Get(hname)

            fOut.cd()
	    h[icat-1].Write()

        try : 

            
	    h[0].Add(h[4])
	    h[1].Add(h[5])
	    h[2].Add(h[6])
	    h[3].Add(h[7])

	    
	    hname=group+"_llet_"+plotVar
	    h[0].SetName(hname)

	    hname=group+"_llmt_"+plotVar
	    h[1].SetName(hname)

	    hname=group+"_lltt_"+plotVar
	    h[2].SetName(hname)

	    hname=group+"_llem_"+plotVar
	    h[3].SetName(hname)

            hsum={}
            hsum=h[0].Clone()
           
            
	    for i in range(1,4) : 
		hsum.Add(h[i])

            hsum.SetName(group+"_all_"+plotVar)

	    for i in range(0,4) : 
		#fOut.cd()
		h[i].Write()

            hsum.Write()

	    #fOut.Write()
        except AttributeError : 
            #print 'problem with', group, icat, cat, plotVar
            continue



