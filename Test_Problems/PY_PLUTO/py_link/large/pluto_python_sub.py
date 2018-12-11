#!/usr/bin/env python

import subprocess
import glob
from astropy.io import ascii
from astropy.table import Table
from astropy import constants as c
from astropy import units as u
from scipy.integrate import quad

import pyPLUTO as pp
import numpy as np


def get_units(fname='definitions.h'):
	inp=open('definitions.h','ro')
	for line in inp.readlines():
		data=line.split()
		if len(data)>1:
			if data[1]=='UNIT_DENSITY':
				UNIT_DENSITY=float(data[2])
			elif data[1]=='UNIT_LENGTH':
				UNIT_LENGTH=float(data[2])
			elif data[1]=='UNIT_VELOCITY':
				UNIT_VELOCITY=float(data[2])
	inp.close()
	return(UNIT_DENSITY,UNIT_LENGTH,UNIT_VELOCITY)
	
	


def brem(freq,T_x=5.6e7,alpha=0.0):
	return freq**alpha*np.exp((-1.*c.h.cgs*freq/c.k_B.cgs/T_x).value)

def pluto_input_file(tlim,data):
	output=open('pluto.ini','w')
	output.write("[Grid]\n")
	output.write("\n")
	output.write("X1-grid 1 "+str(data["R_MIN"])+" "+str(data["N_R"])+" r "+str(data["R_MAX"])+" 1.02\n")
	output.write("X2-grid 1 "+str(data["T_MIN"])+" "+str(data["N_T"])+" r "+str(data["T_MAX"])+" 0.95\n")
	output.write("X3-grid 1    0.0    1      u    1.0\n")
	output.write("\n")
	output.write("[Chombo Refinement]\n")
	output.write("\n")
	output.write("Levels           4\n")
	output.write("Ref_ratio        2 2 2 2 2\n") 
	output.write("Regrid_interval  2 2 2 2 \n")
	output.write("Refine_thresh    0.3\n")
	output.write("Tag_buffer_size  3\n")
	output.write("Block_factor     8\n")
	output.write("Max_grid_size    64\n")
	output.write("Fill_ratio       0.75\n")
	output.write("\n")
	output.write("[Time]\n")
	output.write("\n")
	output.write("CFL              0.4\n")
	output.write("CFL_max_var      1.1\n")
	output.write("tstop            "+str(tlim)+"\n")
	output.write("first_dt         1e-4\n")
	output.write("\n")
	output.write("[Solver]\n")
	output.write("\n")
	output.write("Solver         tvdlf\n")
	output.write("\n")
	output.write("[Boundary]\n")
	output.write("\n")
	output.write("X1-beg        outflow\n")
	output.write("X1-end        outflow\n")
	output.write("X2-beg        axisymmetric\n")
	output.write("X2-end        reflective\n")
	output.write("X3-beg        outflow\n")
	output.write("X3-end        outflow\n")
	output.write("\n")
	output.write("[Static Grid Output]\n")
	output.write("\n")
	output.write("uservar    14    XI T comp_h comp_c line_c brem_c xray_h comp_h_pre comp_c_pre line_c_pre brem_c_pre xray_h_pre ne nh\n")
	output.write("dbl        1000000000000   -1   single_file\n")
	output.write("flt       -1.0  -1   single_file\n")
	output.write("vtk       -1.0  -1   single_file\n")
	output.write("dbl.h5    -1.0  -1\n")
	output.write("flt.h5    -1.0  -1\n")
	output.write("tab       -1.0  -1   \n")
	output.write("ppm       -1.0  -1   \n")
	output.write("png       -1.0  -1\n")
	output.write("log        1000\n")
	output.write("analysis  -1.0  -1\n")
	output.write("\n")
	output.write("[Chombo HDF5 output]\n")
	output.write("\n")
	output.write("Checkpoint_interval  -1.0  0\n")
	output.write("Plot_interval         1.0  0 \n")
	output.write("\n")
	output.write("[Parameters]\n")
	output.write("\n")
	output.write("RHO_0                       "+str(data["RHO_0"])+"\n")
	output.write("RHO_ALPHA                   "+str(data["RHO_ALPHA"])+"\n")
	output.write("R_0                         "+str(data["R_0"])+"\n")
	output.write("CENT_MASS                   "+str(data["CENT_MASS"])+"\n")
	output.write("DISK_MDOT                   "+str(data["DISK_MDOT"])+"\n")
	output.write("CISO                        1e10  \n")
	output.write("L_x                         "+str(data["L_x"])+"\n")
	output.write("T_x                         "+str(data["T_x"])+"\n")
	output.write("DISK_TRUNC_RAD              "+str(data["DISK_TRUNC_RAD"])+"\n")
	output.write("MU                          "+str(data["MU"])+"\n")
	output.close()
	return
	
	
	
def python_input_file(fname,data,cycles=2):
	output=open(fname+".pf",'w')
	output.write("System_type(0=star,1=binary,2=agn)                    2\n")
	output.write("Wind_type                 3\n")	
	output.write("Coord.system(0=spherical,1=cylindrical,2=spherical_polar,3=cyl_var)                    1\n")
	output.write("Wind.dim.in.x_or_r.direction                     30\n")
	output.write("Wind.dim.in.z_or_theta.direction                   30\n")
	output.write("Number.of.wind.components 1\n") 
	output.write("disk.type(0=no.disk,1=standard.flat.disk,2=vertically.extended.disk) 0\n") 
	output.write("Atomic_data                         data/standard80\n")
	output.write("write_atomicdata(0=no,1=yes)               0\n")        
	output.write("photons_per_cycle                            "+str(data["NPHOT"])+"\n")
	output.write("Ionization_cycles                                "+str(cycles)+"\n")
	output.write("spectrum_cycles                                   0\n")
	output.write("adjust_grid(0=no,1=yes)								0\n")
	output.write("Wind_ionization 9\n")
	output.write("Line_transfer 3\n")
	output.write("Thermal_balance_options(0=everything.on,1=no.adiabatic)                    1\n")
	output.write("Disk_radiation(y=1)                               0\n")
	output.write("Wind_radiation(y=1)                               1\n")
	output.write("QSO_BH_radiation                               1\n")
	output.write("Rad_type_for_disk(0=bb,1=models)_to_make_wind     0\n")
	output.write("Rad_type_for_agn(0=bb,1=models,3=power_law,4=cloudy_table)_to_make_wind)  5\n")
	output.write("mstar(msol)        "+str(data["CENT_MASS"]/c.M_sun.cgs.value)+"\n")
	output.write("rstar(cm)                                     7e+08\n")
	output.write("tstar                                         40000\n")
	output.write("lum_agn(ergs/s) "+str(data["L_2_10"])+"\n")
	output.write("agn_bremsstrahlung_temp(K) "+str(data["T_x"])+"\n")
	output.write("agn_bremsstrahlung_alpha "+str(data["BREM_ALPHA"])+"\n")
	output.write("geometry_for_pl_source 0\n")
	output.write("agn_power_law_index 							0.0\n")
	output.write("agn_power_law_cutoff (0)						0\n")
	output.write("Torus(0=no,1=yes)								0\n")
	output.write("disk.mdot(msol/yr)   "+str(data["DISK_MDOT"]/c.M_sun.cgs.value*60.*60.*24.*365.25)+"\n")
	output.write("Disk.illumination.treatment 0\n")
	output.write("Disk.temperature.profile(0=standard;1=readin)                    0\n")
	output.write("disk.radmax(cm)                             2.4e+10\n")
	output.write("wind.radmax(cm)                               1e+11\n")
	output.write("wind.t.init                                   40000\n")
	output.write("hydro_file "+fname+"\n")
	output.write("Hydro_thetamax(degrees)                        -1\n")
	output.write("filling_factor(1=smooth,<1=clumped)                    1\n")
	output.write("Rad_type_for_agn(3=power_law,4=cloudy_table)_in_final_spectrum 3\n")
	output.write("Rad_type_for_disk(0=bb,1=models,2=uniform)_in_final_spectrum                    0\n")
	output.write("spectrum_wavemin                               1450\n")
	output.write("spectrum_wavemax                               1650\n")
	output.write("no_observers                                      4\n")
	output.write("angle(0=pole)                                    10\n")
	output.write("angle(0=pole)                                    30\n")
	output.write("angle(0=pole)                                    60\n")
	output.write("angle(0=pole)                                    80\n")
	output.write("live.or.die(0).or.extract(anything_else)                    1\n")
	output.write("spec.type(flambda(1),fnu(2),basic(other)                    1\n")
	output.write("Use.standard.care.factors(1=yes)						1\n")
	output.write("reverb.type 0\n")
	output.write("Photon.sampling.approach           8\n")
	output.write("Num.of.frequency.bands(5) 10\n")
	output.write("Lowest_energy_to_be_considered(eV) 1.03333\n")
	output.write("Highest_energy_to_be_considered(eV) 50000 \n")
	output.write("Extra.diagnostics(0=no,1=yes)   1\n")
	output.write("keep_ioncycle_windsaves()   1\n")
	output.close()
	return
	
	
def pluto2py(ifile):

	D=pp.pload(ifile)

	# We need the definitions file - so we know the conversion factors.

	UNIT_DENSITY,UNIT_LENGTH,UNIT_VELOCITY=get_units('definitions.h')

	# Open an output file 

	fname="%08d"%ifile+".pluto"

	# Preamble

	out=open(fname,'w')
	out.write("# This is a file generated by hydro_to_python\n")
	out.write("# We can put any number of comments in behind # signs\n")
	out.write("# By default, the order of coordinates are \n")
	out.write("#				r, theta phi for spherical polars\n")
	out.write("# 		                x,y,z        for carteisan\n")
	out.write("#                         or w, z, phi    for cylindrical\n")


	titles=[]
	titles=titles+["ir","r_cent","r_edge"]
	titles=titles+["itheta","theta_cent","theta_edge"]
	titles=titles+["v_r","v_theta","v_phi","density","temperature"]

	r_edge=[]
	r_ratio=(D.x1[2]-D.x1[1])/(D.x1[1]-D.x1[0])
	dr=(D.x1[1]-D.x1[0])/(0.5*(1.0+r_ratio))
	r_edge.append(D.x1[0]-0.5*dr)
	for i in range(len(D.x1)-1):
		r_edge.append(r_edge[-1]+dr)
		dr=dr*r_ratio
	
	
	r_edge=np.array(r_edge)	

	theta_edge=[]
	theta_ratio=(D.x2[2]-D.x2[1])/(D.x2[1]-D.x2[0])
	dtheta=(D.x2[1]-D.x2[0])/(0.5*(1.0+theta_ratio))
	theta_min=D.x2[0]-0.5*dtheta
	if theta_min<0.0:
		theta_min=0.0
	theta_edge.append(theta_min)
	for i in range(len(D.x2)-1):
		theta_edge.append(theta_edge[-1]+dtheta)
		dtheta=dtheta*theta_ratio
	if (theta_edge[-1]+(D.x2[-1]-theta_edge[-1])*2.0)>(np.pi/2.0):
		D.x2[-1]=(theta_edge[-1]+(np.pi/2.0))/2.0

	theta_edge=np.array(theta_edge)	

	col0=np.array([])
	col1=np.array([])
	col2=np.array([])
	col3=np.array([])
	col4=np.array([])
	col5=np.array([])
	col6=np.array([])
	col7=np.array([])
	col8=np.array([])
	col9=np.array([])
	col10=np.array([])

	fmt='%013.6e'

	#This next line defines formats for the output variables. This is set in a dictionary
	fmts={	'ir':'%03i',	
		'r_cent':fmt,
		'r_edge':fmt,
		'itheta':'%i',	
		'theta_cent':fmt,
		'theta_edge':fmt,
		'v_r':fmt,
		'v_theta':fmt,
		'v_phi':fmt,
		'density':fmt,
		'temperature':fmt}

	for j in range(len(D.x2)):
		col0=np.append(col0,np.arange(len(D.x1)))
		col1=np.append(col1,D.x1*UNIT_LENGTH)
		col2=np.append(col2,r_edge*UNIT_LENGTH)
		col3=np.append(col3,np.ones(len(D.x1))*j)
		col4=np.append(col4,np.ones(len(D.x1))*D.x2[j])
		col5=np.append(col5,np.ones(len(D.x1))*theta_edge[j])
		col6=np.append(col6,np.transpose(D.vx1)[j]*UNIT_VELOCITY)
		col7=np.append(col7,np.transpose(D.vx2)[j]*UNIT_VELOCITY)
		col8=np.append(col8,np.transpose(D.vx3)[j]*UNIT_VELOCITY)
		col9=np.append(col9,np.transpose(D.rho)[j]*UNIT_DENSITY)
		col10=np.append(col10,np.transpose(D.T)[j])

	out_dat=Table([col0,col1,col2,col3,col4,col5,col6,col7,col8,col9,col10],names=titles)
	ascii.write(out_dat,out,formats=fmts)
	out.close()
	return


def pre_calc(ifile):
	max_change=0.9
	heatcool=ascii.read("py_heatcool.dat")
	D=pp.pload(ifile)

	# We need the definitions file - so we know the conversion factors.

	UNIT_DENSITY,UNIT_LENGTH,UNIT_VELOCITY=get_units('definitions.h')
	

	comp_h_pre=[]
	comp_c_pre=[]
	xray_h_pre=[]
	brem_c_pre=[]
	line_c_pre=[]

	odd=0.0

	for i in range(len(heatcool["rho"])):
		if (heatcool["rho"][i]/(D.rho[heatcool["i"][i]][heatcool["j"][i]]*UNIT_DENSITY))-1.>1e-6:
			odd=odd+1
		nenh=D.ne[heatcool["i"][i]][heatcool["j"][i]]*D.nh[heatcool["i"][i]][heatcool["j"][i]]
		test=(heatcool["heat_comp"][i]/(D.comp_h_pre[heatcool["i"][i]][heatcool["j"][i]]*D.comp_h[heatcool["i"][i]][heatcool["j"][i]]*nenh))
		if test<max_change*D.comp_h_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=max_change*D.comp_h_pre[heatcool["i"][i]][heatcool["j"][i]]
		elif test>(1./max_change)*D.comp_h_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=(1./max_change)*D.comp_h_pre[heatcool["i"][i]][heatcool["j"][i]]
		comp_h_pre.append(test)
			
		test=(heatcool["cool_comp"][i]/(D.comp_c_pre[heatcool["i"][i]][heatcool["j"][i]]*D.comp_c[heatcool["i"][i]][heatcool["j"][i]]*nenh))
		if test<max_change*D.comp_c_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=max_change*D.comp_c_pre[heatcool["i"][i]][heatcool["j"][i]]
		elif test>(1./max_change)*D.comp_c_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=(1./max_change)*D.comp_c_pre[heatcool["i"][i]][heatcool["j"][i]]
		comp_c_pre.append(test)	
	
		test=(heatcool["cool_lines"][i]/(D.line_c_pre[heatcool["i"][i]][heatcool["j"][i]]*D.line_c[heatcool["i"][i]][heatcool["j"][i]]*nenh))
		if test<max_change*D.line_c_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=max_change*D.line_c_pre[heatcool["i"][i]][heatcool["j"][i]]
		elif test>(1./max_change)*D.line_c_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=(1./max_change)*D.line_c_pre[heatcool["i"][i]][heatcool["j"][i]]
		line_c_pre.append(test)	
	
		test=(heatcool["cool_ff"][i]/(D.brem_c_pre[heatcool["i"][i]][heatcool["j"][i]]*D.brem_c[heatcool["i"][i]][heatcool["j"][i]]*nenh))
		if test<max_change*D.brem_c_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=max_change*D.brem_c_pre[heatcool["i"][i]][heatcool["j"][i]]
		elif test>(1./max_change)*D.brem_c_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=(1./max_change)*D.brem_c_pre[heatcool["i"][i]][heatcool["j"][i]]
		brem_c_pre.append(test)	
	
		test=(heatcool["heat_xray"][i]/(D.xray_h_pre[heatcool["i"][i]][heatcool["j"][i]]*D.xray_h[heatcool["i"][i]][heatcool["j"][i]]*nenh))
		if test<max_change*D.xray_h_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=max_change*D.xray_h_pre[heatcool["i"][i]][heatcool["j"][i]]
		elif test>(1./max_change)*D.xray_h_pre[heatcool["i"][i]][heatcool["j"][i]]:
			test=(1./max_change)*D.xray_h_pre[heatcool["i"][i]][heatcool["j"][i]]
		xray_h_pre.append(test)
	
	
	fmt='%013.6e'

	#This next line defines formats for the output variables. This is set in a dictionary
	fmts={	'ir':'%03i',
		'rcent':fmt,
		'itheta':'%03i',
		'thetacent':fmt,	
		'rho':fmt,
		'comp_h_pre':fmt,
		'comp_c_pre':fmt,
		'xray_h_pre':fmt,
		'line_c_pre':fmt,
		'brem_c_pre':fmt,
		}	

	titles=[]
	titles=titles+["ir","rcent","itheta","thetacent","rho"]
	titles=titles+["comp_h_pre","comp_c_pre","xray_h_pre","brem_c_pre","line_c_pre"]	
	
	col0=heatcool["i"]
	col1=heatcool["rcen"]
	col2=heatcool["j"]
	col3=heatcool["thetacen"]
	col4=heatcool["rho"]
	col5=comp_h_pre
	col6=comp_c_pre
	col7=xray_h_pre
	col8=brem_c_pre
	col9=line_c_pre

	out=open("prefactors.dat",'w')

	out_dat=Table([col0,col1,col2,col3,col4,col5,col6,col7,col8,col9],names=titles)
	ascii.write(out_dat,out,formats=fmts)
	return(odd)
		