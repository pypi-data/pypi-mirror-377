import pandas as pd
import matplotlib.pyplot as plt
import glob
import numpy as np
import astropy.coordinates as coord
from astropy.io import ascii
from astropy.coordinates import SkyCoord
from datetime import datetime
from astropy.table import Table
from astropy.time import Time
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.animation import FuncAnimation
import math
from matplotlib import gridspec
from numba import jit
from celluloid import Camera
import matplotlib.image as mpimg
from mpl_toolkits.basemap import Basemap
from datetime import datetime
import os
from astropy.modeling import models, fitting
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
import astropy.units as units
from astropy.coordinates import SkyCoord, AltAz, EarthLocation

class Telescope:
    def __init__(self,lat,lon,height="",elev_lim=15,name="",sefd=100,color=None):
        """
        Initialize Telescope

        Args:
            lat: Latitude in Degrees
            lon: Longitude in Degrees
            height: Height above sea-level in m
            elev_lim: Elevation limit (float) or 2d-list with azimuth, elevation in degrees
            name: Telescope name
            sefd: System Equivalent Flux Density in Jy
            color: Telescope color (for plots)
        """
        
        self.lat=lat
        self.lon=lon
        self.sefd=sefd

        if isinstance(elev_lim,(float,int)):
            #set constant elev lim
            azimuth=np.linspace(0,360,37)
            elevation=np.full(37,elev_lim)
            self.elev_lim=[azimuth,elevation]
        elif isinstance(elev_lim,list):
            try:
                if len(elev_lim[0])==len(elev_lim[1]):
                    mask = ~np.isnan(elev_lim[1])
                    direction = np.array(elev_lim[0])[mask]
                    lim = np.array(elev_lim[1])[mask]

                    self.elev_lim=[direction,lim]
                else:
                    raise Exception(f"Please use a valid elevation limit! {elev_lim}")
            except:
                raise Exception(f"Please use a valid elevation limit! {elev_lim}")
        else:
            raise Exception(f"Please use a valid elevation limit! {elev_lim}")

        self.name=name
        self.color=color
    
        #convert hourangle to degrees if needed
        if isinstance(lat,str):
            split=lat.split(":")
            self.lat=float(split[0])+float(split[1])/60+float(split[2])/3600
        if isinstance(lon,str):
            split=lon.split(":")
            self.lon=-(float(split[0])+float(split[1])/60+float(split[2])/3600)

        if height=="":
            try:
                self.height = get_elevation(self.lat,self.lon)
            except: 
                self.height = 0
                print(f"Height for telescope {name} could not be estimated automatically, will default to 0")
        elif isinstance(height,(float,int)):
            self.height=height
        else:
            raise Exception("Invalid value for height!")


    #for printing out telescope info
    def __str__(self):
        return f"Telescope {self.name} located at lat: {self.lat}; lon: {self.lon}, height: {self.height}"

    def get_elev_lim(self,azimuth):
        """
        Get elevation limit for given azimuth (in degrees).

        Args:
            azimuth (float): Azimuth angle in degrees

        Returns:
            elevation (float): Elevation limit in degrees for given azimuth angle
        """

        #wrap azimuth angle 
        azimuth = azimuth % 360
 
        return np.interp(azimuth,self.elev_lim[0],self.elev_lim[1])
    
    def get_xyz_coords(self):
        tel = EarthLocation.from_geodetic(lon=self.lon*units.deg, lat=self.lat*units.deg, height=self.height*units.m) 
        
        return tel.geocentric
        

def fitBeam(data):
    med = np.median(data) 

    fit_w = fitting.LevMarLSQFitter()

    y0, x0 = np.unravel_index(np.argmax(data), data.shape)
    sigma = np.std(data)
    amp = np.max(data)

    w = models.Gaussian2D(amp, x0, y0, sigma, sigma, 0.0)
    
    yi, xi = np.indices(data.shape)

    g = fit_w(w, xi, yi, data)
    return g

def simulateUV(telescopes,
               source,output_name="uvout.mp4", #output filepath for 
               make_movie=False, #decide whether to create movie
               n_iter=200, #number of iterations
               make_plot=False, #decide whether to plot source
               obsstart=0, #Observation start in hours of a day
               obsend=24,
              obsday="2023-03-21",
              plotUptime=False,
              colors=[],
              return_uptime=False,
              imgSize=512, #pixelsize of image
               wavelength=1, #highly experimental still! only experts should use it!
              plotLim=15000, #plotLim in kilometer
              do_world_map=False, #decide whether to show world map or not
              image_input=False, #input custom image              
              ):
    r_e=6731 #Earth Radius in Kilometers
    
    plotLim=plotLim/wavelength #max plot length of baselines

    #create real image 
    real_image=np.zeros((imgSize,imgSize))
    #point source in center
    real_image[math.floor(imgSize/2)][math.floor(imgSize/2)]=1
    #point source 2
    #real_image[math.floor(imgSize/2)+20][math.floor(imgSize/2)]=1
    #point source 3
    #real_image[math.floor(imgSize/2)][math.floor(imgSize/2)+20]=1



    #upload custom image
    def rgb2gray(rgb):
        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b #standard grayscale conversion
        return gray
    

    if image_input:
        img_import = mpimg.imread(image_input)
        real_image = rgb2gray(img_import)
    

    real_image_fft=np.fft.fftshift(np.fft.fft2(real_image))
    #plt.imshow(np.abs(real_image_fft))
    #plt.show()

    #convert hourangle to degrees if needed for sourcce
    ra=source[0]
    dec=source[1]
    if isinstance(ra,str):
        split=ra.split(":")
        source[0]=(float(split[0])/24+float(split[1])*1/24/60+float(split[2])*1/24/60/60)*360
    if isinstance(dec,str):
        sign=dec[0]
        split=dec[1:].split(":")
        source[1]=float(split[0])+float(split[1])/60+float(split[2])/60/60
        if sign=="-":
            source[1]=-source[1]
            
            
    #calculate number of baselines
    n_baselines=int(len(telescopes)*(len(telescopes)-1)/2)

    #calculate u-v transformation matrix from source coordinates
    H=source[0]/180*np.pi
    delta=source[1]/180*np.pi
    matrix=np.array([[np.sin(H),np.cos(H),0],
                     [-np.sin(delta)*np.cos(H),np.sin(delta)*np.sin(H),np.cos(delta)],
                    [np.cos(delta)*np.cos(H),-np.cos(delta)*np.sin(H),np.sin(delta)]])

    if len(colors)==0:
        colors=['#e6194b', '#3cb44b', '#ffe119', '#4363d8',
                '#f58231', '#911eb4', '#46f0f0', '#f032e6',
                '#bcf60c', '#fabebe', '#008080', '#e6beff',
                '#9a6324', '#fffac8', '#800000', '#aaffc3',
                '#808000', '#ffd8b1', '#000075', '#808080',
                '#000000']
    
    def get_color(index):
        return colors[index % len(colors)]

    #convert polar coordinates to cartesian
    @jit(nopython=True)
    def Pol2Cart(r,phi,delta):
        x = r * np.cos(delta/180*np.pi) * np.cos(phi/180*np.pi)
        y = - r * np.cos(delta/180*np.pi) * np.sin(phi/180*np.pi)
        z = r * np.sin(delta/180*np.pi)

        return np.array([x,y,z])

    @jit(nopython=True)
    def getUV(Tel1,Tel2,matrix):
        baseline=Tel2-Tel1

        return np.dot(matrix,baseline)


    source_vector=Pol2Cart(r_e,source[0],source[1])

    u_v_grid=np.zeros((imgSize,imgSize))
    pixelSize=plotLim*2/imgSize

    #create array to save uv_tracks for every baseline
    u_v_tracks=[[[],[]] for x in range(n_baselines)]

    def animate(i,u_v_tracks):

        print(str(i+1)+"/"+str(n_iter),end="\r")
        t=obsstart/24*360+(obsend-obsstart)/24*360/n_iter*i+(datetime.strptime(obsday,"%Y-%m-%d")-datetime.strptime("2023-09-22","%Y-%m-%d")).days/365.25*360
        #convert all telescope positions to cartesian coordinates
        tels=np.empty(shape=(len(telescopes), 3))
        tel_visible=np.empty(len(telescopes)) #array to store boolean information whether telescope can see the source or not
        for ind,telescope in enumerate(telescopes):
            new_lat=telescope.lon+t
            if new_lat>180:
                new_lat=new_lat-360

            if do_world_map:
                ax=plt.subplot(gs_world,projection="aitoff")
                plt.scatter(new_lat/180*np.pi,telescope.lat/180*np.pi,marker="*",s=400,c="r")

            tel=Pol2Cart(r_e,new_lat,telescope.lat)
            tels[ind]=tel

            #check if azimuth limit needs to be calculated
            if not len(np.unique(telescope.elev_lim[1]))==1:
                #determine azimuth of source at telescope location
                target = SkyCoord(ra=source[0]*units.deg, dec=source[1]*units.deg)
                # Observation time (UTC)
                obs_time = Time(f'{obsday} 00:00:00') + (obsstart/24+(obsend-obsstart)/24/n_iter*i) * units.day

                # Observer's location (example: Berlin)
                location = EarthLocation(lat=telescope.lat*units.deg, lon=telescope.lon*units.deg)

                # Convert to AltAz frame
                altaz_frame = AltAz(obstime=obs_time, location=location)
                source_altaz = target.transform_to(altaz_frame)

                # Get azimuth
                azimuth = float(source_altaz.az.degree)
                
                elev_lim=telescope.get_elev_lim(azimuth)

            else:
                elev_lim=telescope.elev_lim[1][0]

            #determine whether the source is visible to the telescope
            if np.dot(tel,source_vector)/r_e**2<np.cos((90-elev_lim)/180*np.pi):
                tel_visible[ind]=False
                uptime[ind].append(False)
            else:
                tel_visible[ind]=True
                uptime[ind].append(True)
                
                if plotUptime:
                    plt.scatter(t/360*24-(datetime.strptime(obsday,"%Y-%m-%d")-datetime.strptime("2023-09-22","%Y-%m-%d")).days/365.25*24,ind,c=get_color(ind))


        baseline_count=0
        for k in range(len(tels)):
            if k<len(tels)-1:
                for j in range(k+1,len(tels)):
                    if tel_visible[k] and tel_visible[j]:

                        #plot baseline in world map
                        if do_world_map:
                            ax=plt.subplot(gs_world)
                            plt.plot([(telescopes[k].lon+t)/180*np.pi,(telescopes[j].lon+t)/180*np.pi],
                                     [(telescopes[k].lat)/180*np.pi,(telescopes[j].lat)/180*np.pi],
                                     c=get_color(baseline_count))

                        #get new u_v data point
                        baseline_uv=getUV(tels[k],tels[j],matrix)
                        u=baseline_uv[0]/wavelength
                        v=baseline_uv[1]/wavelength

                        #append new u_v point to baseline u_v track
                        u_array=u_v_tracks[baseline_count][0].append(u)
                        v_array=u_v_tracks[baseline_count][1].append(v)

                        #change u_v_sampling grid
                        x_ind=math.floor((u+plotLim)/pixelSize)
                        y_ind=math.floor((v+plotLim)/pixelSize)

                        u_v_grid[y_ind][x_ind]=1

                        x_ind=math.floor((-u+plotLim)/pixelSize)
                        y_ind=math.floor((-v+plotLim)/pixelSize)

                        u_v_grid[y_ind][x_ind]=1

                    if make_plot or make_movie: 
                        #plot current status of uv_tracks
                        u_plot=u_v_tracks[baseline_count][0]
                        v_plot=u_v_tracks[baseline_count][1]
                        ax = plt.subplot(gs_uv)
                        plt.scatter(u_plot,v_plot,c=get_color(baseline_count),s=1)
                        plt.scatter(-np.array(u_plot),-np.array(v_plot),c=get_color(baseline_count),s=1)
                            
                    baseline_count+=1
        
        if make_plot or make_movie:                
            ax=plt.subplot(gs_image)
            u_v_grid_new=u_v_grid*real_image_fft
            new_dirty_image=np.abs(np.fft.ifft2(np.fft.fftshift(u_v_grid_new)))
            plt.imshow(new_dirty_image,cmap="inferno")
            model=fitBeam(new_dirty_image)
            e=Ellipse((model.x_mean.value,model.y_mean.value),width=model.x_stddev.value,height=model.y_stddev.value,angle=model.theta.value)
            ax.add_artist(e)
            e.set_facecolor("white")
            return u_v_tracks,new_dirty_image
        return u_v_tracks

    if do_world_map:
        fig = plt.figure(figsize=(24,8))
        gs=gridspec.GridSpec(1,3,height_ratios=[1])
        gs_world=gs[0]
        gs_uv=gs[1]
        gs_image=gs[2]
    elif make_plot or make_movie:
        fig = plt.figure(figsize=(16,8))
        gs=gridspec.GridSpec(1,2,height_ratios=[1])
        gs_uv=gs[0]
        gs_image=gs[1]
    
    if make_plot or make_movie:
        camera = Camera(fig)
        ax = plt.subplot(gs_uv)

        plt.xlabel("u [km]")
        plt.ylabel("v [km]")
        plt.ylim(-plotLim,plotLim)
        plt.xlim(-plotLim,plotLim)

    if do_world_map:
        ax=plt.subplot(gs_world,projection="aitoff")
        plt.grid(True)

    uptime=[[] for _ in range(len(telescopes))]
    for i in range(n_iter):
        if make_plot or make_movie:
            u_v_tracks,dirty_image=animate(i,u_v_tracks)
            camera.snap()
        else:
            u_v_tracks=animate(i,u_v_tracks)
        
    if plotUptime:
        plt.show()

    if make_movie:
        anim = camera.animate(blit=False)
        anim.save(output_name, writer='ffmpeg')
    
    if make_plot:
        plt.show()
        return u_v_tracks, dirty_image
    
    if return_uptime:
        return u_v_tracks, uptime
    else:
        return u_v_tracks

def plotUVdata(uv_coverage,highlight_baselines=[],baseline_colors=["black","tab:orange","tab:green"],baseline_width=[0.3,0.3,0.3],z_values=[0,0,0],wavelength=1):
    if len(baseline_colors)<=len(highlight_baselines):
        print("Please define more baseline_colors")
    if len(baseline_width)<=len(highlight_baselines):
        print("Please define more baseline_width")
    if len(z_values)<=len(highlight_baselines):
        print("Please define more z_values")
    else:
        for baseline_count in range(len(uv_coverage)):
            color=baseline_colors[0]
            size=baseline_width[0]
            z_value=z_values[0]
            for i,baselines in enumerate(highlight_baselines):
                if baseline_count in baselines:
                    color=baseline_colors[i+1]
                    size=baseline_width[i+1]
                    z_value=z_values[i+1]
            u_plot=uv_coverage[baseline_count][0]
            v_plot=uv_coverage[baseline_count][1] 
            if not wavelength==1:
                plt.scatter(-np.array(u_plot)/wavelength/1e9,np.array(v_plot)/wavelength/1e9,c=color,s=size,zorder=z_value)
                plt.scatter(np.array(u_plot)/wavelength/1e9,-np.array(v_plot)/wavelength/1e9,c=color,s=size,zorder=z_value)
                plt.xlabel("u [G$\lambda$]",fontsize=25,fontweight="bold")
                plt.ylabel("v [G$\lambda$]",fontsize=25,fontweight="bold")
            else:
                plt.scatter(-np.array(u_plot),np.array(v_plot),c=color,s=size,zorder=z_value)
                plt.scatter(np.array(u_plot),-np.array(v_plot),c=color,s=size,zorder=z_value)
                plt.xlabel("u [km]",fontsize=20,fontweight="bold")
                plt.ylabel("v [km]",fontsize=20,fontweight="bold")
            
            plt.xticks(fontsize=25)
            plt.yticks(fontsize=25)
            plt.axis("equal")


def plotMap(telescopes,llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution="l",projection="cyl"):
    
    m = Basemap(projection=projection,llcrnrlat=llcrnrlat,urcrnrlat=urcrnrlat,\
            llcrnrlon=llcrnrlon,urcrnrlon=urcrnrlon,resolution=resolution)
    m.etopo(scale=1, alpha=0.5)
    m.drawcountries()
    m.drawcoastlines()

    # Map (long, lat) to (x, y) for plotting
    for telescope in telescopes:
        x, y = m(telescope.lon,telescope.lat)
        plt.scatter(x, y, s=60,color="#DD0000",edgecolors="black",zorder=2000)
        
    return m

def getHighlightBaselines(telescopes,inds=[],names=[]):

    n_baselines=int(len(telescopes)*(len(telescopes)-1)/2)

    highlight_baselines=[]

    baseline_count=0
    for k in range(len(telescopes)):
        for j in range(k+1,len(telescopes)):
            if (j in inds) or (k in inds):
                highlight_baselines.append(baseline_count)
            if (telescopes[j].name in names) or (telescopes[k].name in names):
                highlight_baselines.append(baseline_count)
            baseline_count+=1

    return highlight_baselines


def SplitScans(array,source,obstart,obsend,scan_time,n_scans,n_iter=100,obsday="2023-09-20"): #obstart,obsend,scan_time in hours!

    duration=obsend-obstart

    starttimes=np.linspace(obstart,obsend-scan_time,n_scans)

    uv_coverages=[]
    for ind,starttime in enumerate(starttimes):
        uv_coverage=simulateUV(array,source,n_iter=n_iter,obsstart=starttime,obsend=starttime+scan_time,obsday=obsday)
        uv_coverages.append(uv_coverage)
    return uv_coverages


### LIST OF TELESCOPES

def combine_telescopes(tel_arrays):
    final_array=tel_arrays[0].copy()
    for i in range(1,len(tel_arrays)):
        tel_array=tel_arrays[i]
        for tel in tel_array:
            final_array.append(tel)
    return final_array


def getArray(name):


    telescopes=[[50.1905748,11.789879],[49.783333,9.933333],[48.137154,11.576124]]

    if name=="VLBA":
        vlba=[Telescope(42.93362, -71.98681,name="HN"),
            Telescope(41.77165, -91.574133,name="NL"),
            Telescope(30.635214, -103.944826,name="FD"),
            Telescope(35.775289, -106.245599,name="LA"),
            Telescope(34.30107, -108.11912,name="PT"),
            Telescope(31.956253, -111.612361,name="KP"),
            Telescope(37.23176, -118.27714,name="OV"),
            Telescope(48.13117, -119.68325,name="BR"),
            Telescope(19.80159, -155.45581,name="MK"),
            Telescope(17.75652, -64.58376,name="SC")]
        return vlba


    eht_noalma_apex=[[32.701547,-109.891269],[37.066162,-3.392918],[19.822485,-155.476718],
          [18.985439,-97.314765],[19.8237546,-155.477420],[-89.99,-63.453056],[76.531203,-68.703161],[44.63389,5.90792],[31.9533,-111.615]]

    if name=="eht" or name=="EHT":
        eht_full=[
            Telescope(32.701547,-109.891269,name="Arizona"),#Arizona
            Telescope(-23.005893,-67.759155,name="APEX"),#APEX
            Telescope(37.066162,-3.392918,name="PV"),#Pico Veleta
            Telescope(19.822485,-155.476718,name="JCMT"),#JCMT
            Telescope(18.985439,-97.314765,name="LMT"),#LMT
            Telescope(19.8237546,-155.477420,name="SMA"),#SMA
            Telescope(-23.024135,-67.754230,name="ALMA"),#ALMA
            Telescope(-89.99,-63.453056,name="SPT"),#South Pole
            Telescope(76.531203,-68.703161,name="GLT"),#GLT
            Telescope(44.63389,5.90792,name="NOEMA"),#NOEMA
            Telescope(31.9533,-111.615,name="KP"),#Kitt Peak
            Telescope(37.233410,-118.28344,name="OVRO"),#OVRO
            Telescope(37.565237,126.941015,name="KTY"),#KVN Yonsei
            Telescope(37.543703,128.442235,name="KTP")#KVN Pyeongchang
            ]
        return eht_full

    if name=="ngVLA_LBA": #configuration from Walker ngVLA memo 128
        ngVLA_LBA=[Telescope("48:07:53","119:41:03",elev_lim=12,name="VLBA_BR"),
                Telescope("38:25:46","079:50:51",elev_lim=12,name="GBT_VLBA"),
                Telescope("19:38:10","155:28:45",elev_lim=12,name="VLBA_MK"),
                Telescope("42:56:01","071:59:13",elev_lim=12,name="VLBA_HN"),
                Telescope("44:05:10","107:06:54",elev_lim=12,name="WYOMING"),
                Telescope("26:28:10","081:26:43",elev_lim=12,name="FLORIDA"),
                Telescope("22:07:18","159:39:55",elev_lim=12,name="KOKEE"),
                Telescope("41:46:17","091:34:29",elev_lim=12,name="VLBA_NL"),
                Telescope("37:13:54","118:16:38",elev_lim=12,name="VLBA_OV"),
                Telescope("18:20:40","066:44:48",elev_lim=12,name="AREC_NEW"),
                Telescope("34:48:53","100:46:16",elev_lim=12,name="T19"),
                Telescope("30:39:53","101:47:51",elev_lim=12,name="T29"),
                Telescope("28:16:16","104:28:43",elev_lim=12,name="T39"),
                Telescope("27:26:13","108:08:31",elev_lim=12,name="T49"),
                Telescope("29:29:35","112:00:47",elev_lim=12,name="T59"),
                Telescope("33:22:35","106:07:29",elev_lim=12,name="T15"),
                Telescope("32:45:38","108:23:06",elev_lim=12,name="T35"),
                Telescope("34:04:59","109:26:12",elev_lim=12,name="T55"),
                Telescope("33:53:16","107:20:52",elev_lim=12,name="T11"),
                Telescope("35:46:30","106:14:44",elev_lim=12,name="VLBA_LA"),
                Telescope("34:05:24","107:38:20",elev_lim=12,name="COR058")]

        return ngVLA_LBA

    if name=="onsala" or name=="ON" or name=="ONSALA":
        return [Telescope(57.395974, 11.925778,name="ONSALA",elev_lim=7)]

    if name=="hungary" or name=="Hungary" or name=="HUNGARY":
        return [Telescope("47:54:30.0","-19:32:00.0",elev_lim=7,name="HUNGARY")] 

    if name=="yebes" or name=="YS" or name=="YEBES":
        return [Telescope(40.524370, -3.088596,name="YEBES",elev_lim=7)]
 
    #alternative Leverage
    if name=="leverage" or name=="LEVERAGE":
        LEVERAGE=[
                 Telescope(50.523800, 6.884231,elev_lim=12,name="Effelsberg"),#Effelsberg
                 Telescope(51.799973,10.613845,elev_lim=12,name="Harz"),#Brocken(Harz)
                 Telescope(51.178172, 14.948797,elev_lim=12,name="DZA"), #DZA
                 Telescope(51.1781, 14.948797,elev_lim=12,name="DZA2"), #DZA2 for zero spacing
                 Telescope(47.416702,10.979587,elev_lim=12,name="WMT")#Zugspitze
               ]

        return LEVERAGE


    if name=="EVN" or name=="evn":
        evn=[Telescope(50.524778, 6.883972,name="EF"),
                Telescope(-25.89037, 27.68558,name="HH"),
                Telescope(57.553493, 21.854916,name="IR"),
                Telescope(44.5208, 11.6469,name="MC"),
                Telescope(36.87605, 14.989031,name="NT"),
                Telescope(57.393056, 11.917778,name="ON"),
                Telescope(31.0921, 121.1365,name="Tm65"),
                Telescope(43.47, 87.18,name="UR"),
                Telescope(40.525208, -3.088725,name="YS"),
                Telescope(25.03, 102.78,name="KM"),
                Telescope(53.095453,18.563980,name="TR"),
                Telescope(52.914781,6.602881,name="WB")
                ]
        return evn

    if name=="MeerKAT" or name=="MEERKAT" or name=="meerkat":

        meerkat=[]

        file = open("meercat_coordinates.txt")
        for line in file:
            linepart=line.split()
            meerkat.append(Telescope(float(linepart[2]),float(linepart[1]),name=linepart[0],elev_lim=15))
        
        return meerkat


    if name=="SKA":
        ska_mid=[]
        file = open("ska_mid_coordinates.txt")
        for line in file:
            linepart=line.split()
            ska_mid.append(Telescope(float(linepart[2]),float(linepart[1]),name=linepart[0],elev_lim=15))
    
        return ska_mid

    if name=="SKA_cut" or name=="ska_mid_cut":

        #reduced version of ska for computability
        ska_mid_cut=[]
        file = open("ska_mid_coordinates_cut.txt")
        for line in file:
            linepart=line.split()
            ska_mid_cut.append(Telescope(float(linepart[2]),float(linepart[1]),name=linepart[0],elev_lim=15))
        
        ska_mid_cut[0].name="SKA"

        return ska_mid_cut

    if name=="LBA" or name=="lba":
        lba=[Telescope(-30.31,149.57,name="AT"),
             Telescope(-31.30,149.07,name="MP"),
             Telescope(-33.00,148.26,name="PA"),
             Telescope(-42.80,147.44,name="HO"),
             Telescope(-31.87,133.81,name="CD"),
             Telescope(-25.89,27.67,name="HH"),
             Telescope(-14.38,132.15,name="KE"),
             Telescope(-29.05,115.35,name="YG"),
             Telescope(-36.43,174.66,name="WA")]
        return lba

    if name=="GMVA" or name=="gmva":
    
        gmva3mm=[Telescope(41.77165, -91.574133,name="NL"),
                Telescope(30.635214, -103.944826,name="FD"),
                Telescope(35.775289, -106.24559,name="LA"),
                Telescope(34.30107, -108.11912,name="PT"),
                Telescope(31.956253, -111.612361,name="KP"),
                Telescope(37.23176, -118.27714,name="OV"),
                Telescope(48.13117, -119.68325,name="BR"),
                Telescope(19.80159, -155.45581,name="MK"),
                Telescope(50.525, 6.883333,name="EF"),
                Telescope(57.395974, 11.925778,name="ON"),
                Telescope(60.218699, 24.393835,name="MH"),
                Telescope(40.524370, -3.088596,name="YB"),
                Telescope(37.066084,3.392601,name="PV"),
                Telescope(44.633723,5.906684,name="NOEMA"),
                Telescope(76.540357,-68.836813,name="GLT")]
        
        return gmva3mm

    if name=="KVN" or name=="kvn":
        kvn=[Telescope(37.564765, 126.940457,name="KTY"), #Yonsei KY
        Telescope(35.545553, 129.249959,name="KTU"), #Ulsan KU
        Telescope(33.288925, 126.459546,name="KTT"),#Tamna KT
        Telescope(37.543703,128.442235,name="KTP") #Pyeongchang 
        ]
        return kvn

    gmva_alma=combine_telescopes([getArray("gmva"),[[-23.025172, -67.756752]]])

    gmva_alma_atca=combine_telescopes([getArray("gmva"),[[-23.025172, -67.756752],[-30.314097, 149.564473],
                    [-31.2677, 149.1]]])


    if name=="africa_vlbi" or name=="ska_vlbi" or name=="SKA_VLBI":
        africa_vlbi=combine_telescopes([getArray("ska_mid_cut"),[Telescope(-25.89017,27.68332,name="Hart"), #Hart
                                                    Telescope(-23.272226, 16.500667,name="HESS"), #HESS
                                                    Telescope(-22.594071,27.121829,name="Palapye")#, #Palapye Botswana
                                                    ]])  #[5.750350,-0.305276] #Ghana Kutunse Station
    
        return africa_vlbi


    if name=="africa_vlbi_ska_core":
        africa_vlbi_ska_core=[Telescope(21.449412, -30.71329,name="AA*"),Telescope(-25.89017,27.68332,name="HH"), #Hart
                                Telescope(-23.272226, 16.500667,name="HESS"), #HESS
                                Telescope(-22.594071,27.121829,name="Palapye"), #Palapye Botswana
                                Telescope(5.750350,-0.305276,name="Ghana")] #Ghana Kutunse Station
        return africa_vlbi_ska_core


    if name=="VERA" or name=="vera":
        vera=[Telescope(24.411650,124.171010),#Ishigaki-Jima
            Telescope(31.748042,130.439820),#Iriki
            Telescope(27.091850,142.216614),#Ogasawara
            Telescope(39.133520,141.132593),#Mizusawa
            ]
        return vera

    
    if name=="TANAMI" or name=="tanami":
        tanami=[Telescope(-30.31,149.57,name="AT"),
                Telescope(-31.30,149.07,name="MP"),
                Telescope(-33.00,148.26,name="PA"),
                Telescope(-42.80,147.44,name="HO"),
                Telescope(-31.87,133.81,name="CD"),
                Telescope(-25.89,27.67,name="HH"),
                Telescope(-14.38,132.15,name="KE"),
                Telescope(-29.05,115.35,name="YG"),
                Telescope(-36.43,174.66,name="WA")]

        return tanami

    if name in ["EMERLIN","eMERLIN","emerlin","merlin","MERLIN"]:
        emerlin=[Telescope("52:10:00","-00:02:15",name="Cambridge"),
                Telescope("53:09:22","02:32:07",name="Darnhall"),
                Telescope("52:06:01","02:08:39",name="Defford"),
                Telescope("52:47:24","02:59:49",name="Knockin"),
                Telescope("53:14:10","02:18:26",name="Jodrell Bank"),
                Telescope("53:17:18","02:26:44",name="Pickmere")]
        return emerlin

def plotGlobe(arrays,colors="",edgecolors="",lat_0=0,lon_0=0,size=100):
    
    if colors=="":
        colors=["black" for i in range(len(arrays))]
    if edgecolors=="":
        edgecolors=["white" for i in range(len(arrays))]

    #convert hourangle to degrees if need
    plt.figure(figsize=(8, 8))
    m = Basemap(projection='ortho', resolution=None, lat_0=lat_0, lon_0=lon_0)
    lats = m.drawparallels(np.linspace(-90, 90, 13))
    lons = m.drawmeridians(np.linspace(-180, 180, 13))
    m.etopo(scale=0.5, alpha=0.5)
    
    for ind,array in enumerate(arrays):
        for i in range(len(array)):
            #plot black
            telescope=array[i]
            x, y = m(telescope.lon,telescope.lat)
            plt.scatter(x, y,s=size,color=colors[ind],edgecolors=edgecolors[ind])
    

    plt.tight_layout()
    plt.savefig("worldmap.png",dpi=300)
    plt.savefig("worldmap.pdf")
    plt.show()


import requests

def get_elevation(lat,lon):
    url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["elevation"][0]
    else:
        raise Exception(f"API request failed with status {response.status_code}")

def main():
    print("Running vlbisim")

if __name__ == "__main__":
    main()
