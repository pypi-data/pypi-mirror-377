from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
import pylab as m

class original:
    def __init__(self,filename):
        self.fname = filename


    def adcpasciireader(self):
        f_in = open(self.fname,'r')
        my_data = defaultdict(list)
        my_adcp_data = defaultdict(list)
        ensno = 1

        my_data['coma']=f_in.readline().rstrip()
        my_data['comb']=f_in.readline().rstrip()

        #The next line are general information for  Profile info table
        datal=f_in.readline().rstrip()
        #split the line with space and join them width ,
        dataf=','.join(datal.split())


        while True:
            #test si il y a encore des lignes
            test = f_in.readline()
            
            if test =='':
                break #Stop while when we get the EOF
            else:
                datal=test.rstrip()
                #For EnsembleInfo
                #The 6 lines correspond to data in EnsembleInfo table
                cpt=1
                dataf = datal.split()
                dataf = [float(x) for x in dataf]
                # dataf=','.join(datal.split())
                while cpt<5:
                    datal=f_in.readline().rstrip()
                    datal=datal.split()
                    for i in range(0,len(datal)):
                        if '-' in datal[i]:
                            dataltemp = datal[i].split('-')
                            datal[i] = -1*float(dataltemp[1])
                        else:
                            datal[i] = float(datal[i])
                            
                    datal = [float(x) for x in datal]
                    for i in range(0,len(datal)):
                        dataf.append(datal[i])
                    cpt=cpt+1
                #for last line need somme modifications
                datal=f_in.readline().rstrip()
                datat=datal.split()
                cpt = [1,2,3]
                for i in range(0, len(datat)):
                    if i not in cpt:
                        datat[i] = float(datat[i])
                    dataf.append(datat[i])
                #Save number of bins for ADCPData
                nbins=datat[0]
                #make the request

                my_data['Ensemblecode'].append(ensno)
                my_data['ETYear'].append(dataf[0])
                my_data['ETMonth'].append(dataf[1])
                my_data['ETDay'].append(dataf[2])
                my_data['ETHour'].append(dataf[3])
                my_data['ETMin'].append(dataf[4])
                my_data['ETSec'].append(dataf[5])
                my_data['ETHund'].append(dataf[6])
                my_data['ENum'].append(dataf[7])
                my_data['NES'].append(dataf[8])
                my_data['PITCH'].append(dataf[9])
                my_data['ROLL'].append(dataf[10])
                my_data['CORRHEAD'].append(dataf[11])
                my_data['ADCPTemp'].append(dataf[12])
                my_data['BTVelE'].append(dataf[13])
                my_data['BTVelN'].append(dataf[14])
                my_data['BTVelUp'].append(dataf[15])
                my_data['BTVelErr'].append(dataf[16])
                my_data['CBD'].append(dataf[17])
                my_data['GGAA'].append(dataf[18])
                my_data['GGAD'].append(dataf[19])
                my_data['GGAHDOP'].append(dataf[20])
                my_data['DB1'].append(dataf[21])
                my_data['DB2'].append(dataf[22])
                my_data['DB3'].append(dataf[23])
                my_data['DB4'].append(dataf[24])
                my_data['TED'].append(dataf[25])
                my_data['TET'].append(dataf[26])
                my_data['TDTN'].append(dataf[27])
                my_data['TDTE'].append(dataf[28])
                my_data['TDMG'].append(dataf[29])
                my_data['LAT'].append(dataf[30])
                my_data['lON'].append(dataf[31])
                my_data['NDInv'].append(dataf[32])
                my_data['NDfnvu'].append(dataf[33])
                my_data['NDfnvu2'].append(dataf[34])
                my_data['DVMP'].append(dataf[35])
                my_data['DVTP'].append(dataf[36])
                my_data['DVBP'].append(dataf[37])
                my_data['DVSSDE'].append(dataf[38])
                my_data['DVSD'].append(dataf[39])
                my_data['DVESDE'].append(dataf[40])
                my_data['DVED'].append(dataf[41])
                my_data['SDML'].append(dataf[42])
                my_data['SDBL'].append(dataf[43])
                my_data['NBINS'].append(dataf[44])
                my_data['MU'].append(dataf[45])
                my_data['VR'].append(dataf[46])
                my_data['IU'].append(dataf[47])
                my_data['ISF'].append(dataf[48])
                my_data['SAF'].append(dataf[49])

                ensno = ensno + 1


                #For ADCPData

                
                Ensemblecode = []
                DEPTH = []
                VM = []
                VD = []
                EVC = []
                NVC = []
                VVC = []
                ERRV = []
                BCKSB1 = []
                BCKSB2 = []
                BCKSB3 = []
                BCKSB4 = []
                PG = []
                Q = []
                cpt=1
                type(nbins)
                while cpt<int(nbins)+1:
                    datal=f_in.readline().rstrip()
                    dataf = datal.split()
                    dataf = [float(x) for x in dataf]

                    cpt=cpt+1
                    #make the request

                    Ensemblecode.append(ensno)
                    DEPTH.append(float(dataf[0]))
                    VM.append(dataf[1])
                    VD.append(dataf[2])
                    EVC.append(dataf[3])
                    NVC.append(dataf[4])
                    VVC.append(dataf[5])
                    ERRV.append(dataf[6])
                    BCKSB1.append(dataf[7])
                    BCKSB2.append(dataf[8])
                    BCKSB3.append(dataf[9])
                    BCKSB4.append(dataf[10])
                    PG.append(dataf[11])
                    Q.append(dataf[12])

                my_adcp_data['Ensemblecode'].append(Ensemblecode)
                my_adcp_data['DEPTH'].append(DEPTH)
                my_adcp_data['VM'].append(VM)
                my_adcp_data['VD'].append(VD)
                my_adcp_data['EVC'].append(EVC)
                my_adcp_data['NVC'].append(NVC)
                my_adcp_data['VVC'].append(VVC)
                my_adcp_data['ERRV'].append(ERRV)
                my_adcp_data['BCKSB1'].append(BCKSB1)
                my_adcp_data['BCKSB2'].append(BCKSB2)
                my_adcp_data['BCKSB3'].append(BCKSB3)
                my_adcp_data['BCKSB4'].append(BCKSB4)
                my_adcp_data['PG'].append(PG)
                my_adcp_data['Q'].append(Q)
        
        return my_data, my_adcp_data


    def originalProfile(self,width = 20, length = 4):
        x,y = self.adcpasciireader()
        vel = np.array(y['VM'])
        bt = np.array(x['DB1'])
        depth = np.array(y['DEPTH'])
        tdmg = np.array(x['TDMG'])
        vel = np.ma.masked_where(vel == -32768, vel)
        vel = vel.T

        plt.figure(figsize=(width, length))
        plt.plot(tdmg, -bt,'k-',lw=3)
        plt.pcolormesh(tdmg,-depth[0],vel*10**-2,vmin=np.amin(vel*10**-2),vmax=np.amax(vel*10**-2),cmap = 'hsv')        
        cbar=colorbar(orientation='vertical')
        cbar.set_label('Velocity $[ms^{-1}]$')
        plt.xlabel('Distance($m$)')
        plt.ylabel('Depth($m$)')
        plt.ylim(-max(bt) -1, -min(bt))
        plt.xlim(min(tdmg), max(tdmg))
        plt.title('River Thread')
        plt.fill_between(tdmg, -bt, min(-bt-2), color='grey', alpha=0.5)
        plt.show()

    def ExportPosition (self,name_out,format='txt',process='mean') :
		# """ Fonction pour exporter les positions GPS
		# [option]
		# format : 'txt' [default] exprot en format texte
 		# 		 'kml' export au format kml de google
		# """

		#recupération du minimum en coord pour chaques points fixes
        x,y = self.adcpasciireader()
        lat = np.array(x['LAT'])
        lon = np.array(x['lON'])
        datas_gps = np.vstack([lon,lat])
        
        if format == 'txt' :
			#Ecriture dans un fichier
            f_out = open(name_out,'w')
            f_out.write("Lat_decim|Lon_decim\n")
            for i in datas_gps.T :
                f_out.write("%f|%f\n"%(i[1],i[0]))
            f_out.close()
        
        if format == 'kml' :
			#GESTION DES ENTETES ET DES FOOTERS
            kmlHeader = ('<?xml version="1.0" encoding="UTF-8"?>\n'
			 '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n'
             '<Document>\n'
             '<name>'+str(self.fname)+'</name>\n'
             '<Style id="yellowLineGreenPoly">\n'
			'<LineStyle>\n'
			'<color>7f00ffff</color>\n'
			'<width>4</width>\n'
			'</LineStyle>\n'
			'<PolyStyle>\n'
			'<color>7f00ff00</color>\n'
			'</PolyStyle>\n'
			'</Style>\n'
             )
            
            kmlFooter = ('</Document>\n'
						'</kml>\n')

            lat = datas_gps[1]
            lon = datas_gps[0]
            name = m.r_[0:len(lon)]

            kml = ''
            kml += '<Placemark>\n'+'<name>'+str(self.fname)+'</name>\n'
            kml += '<styleUrl>#yellowLineGreenPoly</styleUrl>'
            kml += (
      			'<LineString>\n'
        		'<extrude>1</extrude>\n'
        		'<tessellate>1</tessellate>\n'
				'<coordinates>')
            for i in range(len(name)) :
				#tmp_lon = str(lon[i]).split('.')
				#tmp_lat = str(lat[i]).split('.')
                if (lon[i]!=-30000 and lat[i] != -30000) :
                    kml += (
					'%f,%f,1\n'
					) %(lon[i], lat[i])

            kml += ' </coordinates>\n</LineString>\n</Placemark>\n'
            kml_final = kmlHeader + kml + kmlFooter
            print(kml_final)
            open(name_out,'w').write(kml_final)