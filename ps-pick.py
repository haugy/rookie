#! /usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from obspy import read
from obspy.signal.trigger import ar_pick, recursive_sta_lta, trigger_onset
import csv
import gc

'''st = read('*.sac')
stn = st.select(component = 'N')[0]
ste = st.select(component = 'E')[0]
stz = st.select(component = 'Z')[0]

z = stz.data[0:ste.stats.npts]
x = stn.data[0:ste.stats.npts]
y = ste.data[0:ste.stats.npts]'''
class EQwave(object):
	def __init__(self, zwave, ewave, nwave, sampling_rate):
		self.zwave = zwave
		self.ewave = ewave
		self.nwave = nwave
		self.__sampling_rate = sampling_rate
	'''def bpfilter(self, freqmin = 1, freqmax = 20):
		self.zwave.filter("bandpass", freqmin, freqmax)
		self.ewave.filter("bandpass", freqmin, freqmax)
		self.nwave.filter("bandpass", freqmin, freqmax)'''
	def res_sta_lta(self,sta,lta):
		self.zwave = recursive_sta_lta(self.zwave, int(sta * sampling_rate), int(lta * sampling_rate))
		self.ewave = recursive_sta_lta(self.ewave, int(sta * sampling_rate), int(lta * sampling_rate))
		self.nwave = recursive_sta_lta(self.nwave, int(sta * sampling_rate), int(lta * sampling_rate))
		gc.collect()
	def tri_onset(self, cft, thr_on, thr_off):
		return trigger_onset(cft, thr_on, thr_off, 150, False)
	def cal_trtime(self, ztrtime, etrtime, ntrtime):
		self.trtime = []
		for x,y in ztrtime:
			self.trtime.append(x)
		for x,y in etrtime:
			self.trtime.append(x)
		for x,y in ntrtime:
			self.trtime.append(x)
		self.trtime.sort()
		print 'trlenth:',len(self.trtime)
		for ivalue in self.trtime:
			idx = self.trtime.index(ivalue) + 1
			if idx >= len(self.trtime):
				break
			if (self.trtime[idx] - ivalue) < 60:
				self.trtime[idx] = (self.trtime[idx] + ivalue)/2
				self.trtime.pop(idx - 1)
			else:
				continue
#		return self.trtime
	def ifpswave(self, thr_on):
		self.psresult = []
		for x in self.trtime:
			if((self.zwave[x] > thr_on)and((self.ewave[x] > thr_on)or(self.nwave[x] > thr_on))):
				self.psresult.append('s')
			else:
				self.psresult.append('p')
'''	def __del__(self):
		print 'del...'''
def wrfile(csvfile,station,ontime,pstype):
	rowvalue = [station, ontime, pstype]
	out = open(csvfile, 'a+')
	csv_writer = csv.writer(out)
	csv_writer.writerow(rowvalue)
if __name__ == '__main__':
	for days in xrange(213, 244):
		sacname = '*.2008%s*.BHZ' %days
		st = read(sacname)
#	st = read('*.BHZ', debug_headers=True)
		print len(st)
		for stz in st:
			t1time = stz.stats.starttime
			network = stz.stats.network
			station = stz.stats.station
			nzyear = stz.stats.sac.nzyear
			nzjday = stz.stats.sac.nzjday
			sampling_rate = stz.stats.sampling_rate
			filename = '%s.%s.%s%s*' %(network, station, nzyear, nzjday)
			tr = read(filename) 
			stn = tr.select(component = 'N')[0]
			ste = tr.select(component = 'E')[0]
			stz.filter('lowpass', freq = 0.05, corners = 2, zerophase = True)
			ste.filter('lowpass', freq = 0.05, corners = 2, zerophase = True)
			stn.filter('lowpass', freq = 0.05, corners = 2, zerophase = True)
			z = stz.data#[0:ste.stats.npts]
			n = stn.data#[0:ste.stats.npts]
			e = ste.data#[0:ste.stats.npts]
			print station
			wavedata = EQwave(z,e,n,sampling_rate)
			'''fmin = 1
			fmax = 20
			wavedata.bpfilter(fmin, fmax)'''
			sta = 20
			lta = 150
			wavedata.res_sta_lta(sta, lta)
			thr_on = 6
			thr_off = 0.7
			ztime = wavedata.tri_onset(wavedata.zwave, thr_on, thr_off)
			etime = wavedata.tri_onset(wavedata.ewave, thr_on, thr_off)
			ntime = wavedata.tri_onset(wavedata.nwave, thr_on, thr_off)
			wavedata.cal_trtime(ztime, etime, ntime)
			wavedata.ifpswave(thr_on)
			t1_unix=float(t1time.strftime("%s.%f"))
			print t1_unix
			for t1 in wavedata.trtime:
				t2 = t1//sampling_rate
				time_submission = float(datetime.fromtimestamp(t1_unix+ 8*3600+t1).strftime('%Y%m%d%H%M%S.%f'))
				pstype = wavedata.psresult[wavedata.trtime.index(t1)]
				csvname = 'eqai.csv'
				wrfile(csvname, station, time_submission, pstype)
			print 'FLAG'
			del wavedata
			gc.collect()
'''pwave = z - (x + y)*(0.5)
swave = (x + y)*(0.5)
t = np.arange(0,ste.stats.npts/ste.stats.sampling_rate,ste.stats.delta)
plt.subplot(211)
plt.plot(t[400000:600000], pwave[400000:600000], 'k')
plt.ylabel('p-wave')
plt.subplot(212)
plt.plot(t[400000:600000], swave[400000:600000], 'k')
plt.ylabel('s-wave')
plt.xlabel('Time [s]')
plt.suptitle(ste.stats.starttime)
plt.savefig('p-s-wave.png')'''

