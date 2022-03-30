'''
Ovo bi trebalo plotat valni oblik i FFT sa CH1 samo

1)Prilikom prvog pokretanja instaliras visa library: Runas komandu "pip install -U pyvisa"
2)Poveze se siglent preko USB port-a sa PC-em
3)Otvori se EasyScopeX
4)Iz njega se prepise adresa iz "Scope explorrer taba" 
(za USBTMSC izgleda ovako nes: USB0::0xF4ED::0xEE3A::SDS1EDEQ5R0059::INSTR)
5)Probas jeli radi :-)
'''

import pyvisa as visa
import pylab as pl
import numpy as np

USBTMSC_address = "USB0::0xF4ED::0xEE3A::SDS1EDEQ5R0059::INSTR" #Tu se pastea ta adresa

def main():
    _rm = visa.ResourceManager()
    sds = _rm.open_resource(USBTMSC_address)
    sds.write("chdr off")
    vdiv = sds.query("c1:vdiv?")
    ofst = sds.query("c1:ofst?")
    tdiv = sds.query("tdiv?")
    sara = sds.query("sara?")
    sara_unit = {'G':1E9,'M':1E6,'k':1E3}
    for unit in sara_unit.keys():
        if sara.find(unit)!=-1:
            sara = sara.split(unit)
            sara = float(sara[0])*sara_unit[unit]
            break
    sara = float(sara)
    sds.timeout = 2000 #default value is 2000(2s)
    sds.chunk_size = 20*1024*1024 #default value is 20*1024(20k bytes)
    sds.write("c1:wf? dat2")
    recv = list(sds.read_raw())[15:]
    recv.pop()
    recv.pop()
    volt_value = []
    for data in recv:
        if data > 127:
            data = data - 255
        else:
            pass
        volt_value.append(data)
    time_value = []
    for idx in range(0,len(volt_value)):
        volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
        time_data = -(float(tdiv)*14/2)+idx*(1/sara)
        time_value.append(time_data)
        
    #plotanje
    pl.figure(figsize=(14,10))
    pl.plot(time_value,volt_value,markersize=2)
    pl.xlabel('Time [s]')
    pl.ylabel('Voltage [V]')
    pl.grid()
    pl.show()
    
    
    #DFT
    X = abs(np.fft.rfft(volt_value))
    
    pl.figure(figsize=(14,10))
    pl.xscale('log')
    pl.xlabel('Frequency [Hz]')
    pl.ylabel('|amplitude|')
    pl.grid()
    pl.plot(X)
    #pl.savefig('DFT.png')
  
if __name__=='__main__':
    main()
