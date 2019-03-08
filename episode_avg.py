# Purpose: Report episodic NA averages for PM2.5, NOx, VOC, NH3, and SO2
import numpy as np
import sys

# PARAMS:
# May have to manually set 'run_name' below if certain sector(s) weren't updated.
run_name = '2020_1aug2018'
emit_scenario = run_name
#

###########################################################
# File with grid cell -> nonattainment area mapping:
assig_file = '4kmDOM_CellsAssign_NonAttainment.txt'
days = [2010365]
jan_days = [2011001 + i for i in range(10)]
days += jan_days

# Which sectors to run reports on? Probably always do all of them =)
do_ar = True
do_nr = True
do_mb = True
do_pt = True

ar_rpts = []
nr_rpts = []
mb_rpts = []
pt_rpts = []
for day in days:
    ar_rpt = '../Reports/{1}/areat.hour_scc.{1}.{0}.rpt'.format(day, '2020_25jul2018')
    nr_rpt = '../Reports/{1}/nonroadt.hour_scc.{1}.{0}.rpt'.format(day, run_name)
    mb_rpt = '../Reports/{1}/mobilet.hour_scc.{1}.{0}.rpt'.format(day, run_name)
    pt_rpt = '../Reports/{1}/pointt.hour_scc.{1}.{0}.rpt'.format(day, run_name)
    ar_rpts.append(ar_rpt)
    nr_rpts.append(nr_rpt)
    mb_rpts.append(mb_rpt)
    pt_rpts.append(pt_rpt)
    
num_days = len(ar_rpts)   # number of days in episode (should be 12)

# Determine grid cell assignment
assigs = {}
with open(assig_file,'r') as fh:
    for line in fh:
        col,row,cd = line.split()
        k = (col, row)
        assigs[k] = cd.strip() # Remove NL

# Lookup tables for data_tabl -------------------
naa_index = {
    "1":0,  # Salt Lake
    "2":1,  # Provo
    "3":2   # Logan
    }

""" Pollutant indices don't change:
pm25 -> 0
nox -> 1
voc -> 2
nh3 -> 3
so2 -> 4
"""

src_index = {
    "area":0,
    "nonroad":1,
    "mobile":2,
    "point":3
    }

na_tabl = {
    0:'Salt Lake NA',
    1:'Provo NA',
    2:'Logan NA'
    }

# -------------------------------------------------
def prt_lines(sector_name,rpts):
    data_tabl = np.zeros(shape=(3,5))
    src = src_index[sector_name]
    src_title = '{0} Sources'.format(sector_name.capitalize())
    for rpt in rpts:
        print rpt
        with open(rpt,'r') as fh:
            for i, line in enumerate(fh):
                # Skip header lines:
                if i < 12:
                    continue

                parts = map(lambda s: s.strip(), line.split(';'))
                col, row = parts[1:3]
                cd = assigs[(col, row)]
                if cd == "0":   # Not in NAA region
                    continue
                else:
                    reg = naa_index[cd]

                # Works for area, nonroad, mobile, and point
                nox,voc,nh3,so2,pm10,pm25 = map(float, parts[4:10])
                data_tabl[reg,:] += [pm25,nox,voc,nh3,so2]

    # Average over number of days
    data_tabl /= num_days
    return (data_tabl,src_title)

# ------------------------------------------------------
ofh = open('epi_report_{0}.csv'.format(emit_scenario),'w')
ofh.write('Emissions [tons/day],Region,Sector,PM2_5,NOx,VOC,NH3,SO2\n')
for na_index in range(3):
    ar_tabl,ar_title = prt_lines('area',ar_rpts)
    mb_tabl,mb_title = prt_lines('mobile',mb_rpts)
    nr_tabl,nr_title = prt_lines('nonroad',nr_rpts)
    pt_tabl,pt_title = prt_lines('point',pt_rpts)
    region_total = ar_tabl[na_index,:] + mb_tabl[na_index,:] + nr_tabl[na_index,:] + pt_tabl[na_index,:]
    ar_vals = map(lambda v: '{0:.2f}'.format(v), ar_tabl[na_index,:])
    mb_vals = map(lambda v: '{0:.2f}'.format(v), mb_tabl[na_index,:])
    nr_vals = map(lambda v: '{0:.2f}'.format(v), nr_tabl[na_index,:])
    pt_vals = map(lambda v: '{0:.2f}'.format(v), pt_tabl[na_index,:])
    region_vals = map(lambda v: '{0:.2f}'.format(v), region_total)
    na_name = na_tabl[na_index]
    ay = [emit_scenario,na_name,'Area Sources'] + ar_vals
    my = [emit_scenario,na_name,'Mobile Sources'] + mb_vals
    ny = [emit_scenario,na_name,'NonRoad Sources'] + nr_vals
    py = [emit_scenario,na_name,'Point Sources'] + pt_vals
    ry = [emit_scenario,na_name,'Total'] + region_vals
    ofh.write(','.join(ay) + '\n')
    ofh.write(','.join(my) + '\n')
    ofh.write(','.join(ny) + '\n')
    ofh.write(','.join(py) + '\n')
    ofh.write(','.join(ry) + '\n')
       
ofh.close()

print 'Finished!'
