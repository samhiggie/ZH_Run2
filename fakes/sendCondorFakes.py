import os
import os.path
import sys
import fileinput
import subprocess

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default='ZH',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-f","--inFileName",default='file.csv',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-e","--extraTag",default='pow_noL',type=str,help="pow_noL or pow_wL")
    parser.add_argument("-o","--overideSyst",default='',type=str,help="overide sys")
    return parser.parse_args()


args = getArgs()
era = str(args.year)
sel = str(args.selection)
tag= str(args.extraTag)

eospath='/eos/uscms/store/user/alkaloge/{0:s}/nAODv7/'.format(sel)



command = "mkdir -p /eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/{0:s}/data_{0:s}".format(era)
os.system(command)

scaleSyst = ["Central"]

scale = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']


for i, sys in enumerate(scale) :
    scaleSyst.append(sys+'Up')
    scaleSyst.append(sys+'Down')

jes=['jesAbsolute', 'jesAbsolute_{0:s}'.format(str(era)), 'jesBBEC1', 'jesBBEC1_{0:s}'.format(str(era)), 'jesEC2', 'jesEC2_{0:s}'.format(str(era)), 'jesFlavorQCD', 'jesHF', 'jesHF_{0:s}'.format(str(era)), 'jesRelativeBal', 'jesRelativeSample_{0:s}'.format(str(era)), 'jesHEMIssue', 'jesTotal', 'jer']

jesSyst=[]
for i, sys in enumerate(jes) :
    jesSyst.append(sys+'Up')
    jesSyst.append(sys+'Down')

otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40', 'scale_met_unclustered'] 
OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')

sysall = scaleSyst + jesSyst + OtherSyst

#sysall = ["Central"]

if str(args.overideSyst) != '' : sysall=[args.overideSyst]

for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    ds = vals[0]
    nickName=vals[1]
    if 'Run' in ds or 'data' in ds : sysall = ["Central"]
    if '#' in ds : continue



    for ic, sys in enumerate(sysall) :

        filejdl = 'condor_{0:s}_{1:s}_Fakes_{3:s}_sys{4:s}.jdl'.format(ds,era,sel,tag, sys)
        filesh = 'condor_{0:s}_{1:s}_Fakes_{3:s}_sys{4:s}.sh'.format(ds,era,sel,tag, sys)

	cf =os.path.isfile('/eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/{2:s}/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)) #ZHToTauTau_2016_sysscale_t_3prong1pizeroUp.root
	cff =os.path.isfile('/eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/{2:s}/NormZZ/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)) #ZHToTauTau_2016_sysscale_t_3prong1pizeroUp.root

	cfs = os.path.isfile("./Jobs/{0:s}.submitted".format(filejdl))

        if cf or cff : 
	    print 'looks like you have it this in eos', ds, era, sel, tag, sys , '/eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/{2:s}/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)
            continue
        if not cf and not cff and cfs : 
            print 'maybe this is running {0:s}? '.format(filejdl)
            continue
        if not cf and not cff and not cfs:

	    command = "cp Templates/template.sh {0:s}".format(filesh)
	    os.system(command)
	    command = "cp Templates/template.jdl {0:s}".format(filejdl)
	    os.system(command)
	    
	   
	    subprocess.call(["sed -i  's/SYSTEMATICHERE/{1:s}/g' {0:s}".format(filesh,sys)], shell=True)
	    subprocess.call(["sed -i  's/SYSTEMATICHERE/{1:s}/g' {0:s}".format(filejdl,sys)], shell=True)

	    subprocess.call(["sed -i  's/FILEIN/{1:s}/g' {0:s}".format(filesh,ds)], shell=True)
	    subprocess.call(["sed -i  's/FILEIN/{1:s}/g' {0:s}".format(filejdl,ds)], shell=True)

	    subprocess.call(["sed -i  's/YEAR/{1:s}/g' {0:s}".format(filesh,era)], shell=True)
	    subprocess.call(["sed -i  's/YEAR/{1:s}/g' {0:s}".format(filejdl,era)], shell=True)

	    subprocess.call(["sed -i  's/CHANNEL/Fakes/g' {0:s}".format(filesh,sel)], shell=True)
	    subprocess.call(["sed -i  's/CHANNEL/Fakes/g' {0:s}".format(filejdl,sel)], shell=True)

	    subprocess.call(["sed -i  's/NICKNAME/{1:s}/g' {0:s}".format(filesh,nickName)], shell=True)
	    subprocess.call(["sed -i  's/NICKNAME/{1:s}/g' {0:s}".format(filejdl,nickName)], shell=True)


	    subprocess.call(["sed -i  's/TAG/{1:s}/g' {0:s}".format(filesh,tag)], shell=True)
	    subprocess.call(["sed -i  's/TAG/{1:s}/g' {0:s}".format(filejdl,tag)], shell=True)

	    #outLines = []
	    #outLines.append("{0:s}\n".format(ds)
	    #ttW_2016_Fakes_pow_noL.txt
	    ftxt=ds+'_'+era+'.txt'

	    open(ftxt,'w').writelines(line)


	    command = "chmod 777 {0:s}".format(filejdl)
	    os.system(command)
	    command = "chmod 777 {0:s}".format(filesh)
	    os.system(command)


	    command = "mv  {0:s} Jobs/.".format(ftxt)
	    os.system(command)
	    command = "mv  {0:s} Jobs/.".format(filejdl)
	    os.system(command)
	    command = "mv  {0:s} Jobs/.".format(filesh)
	    os.system(command)

	    fileout='{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)

	    #/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/2016/

	    print 'this is missing..... eos', ds, era, sel, tag, sys
	    command = "cd Jobs;condor_submit {0:s} ;cd ..".format(filejdl)
	    os.system(command)
	    com="touch ./Jobs/{0:}.submitted".format(filejdl)
	    os.system(com)
	    print command
		

