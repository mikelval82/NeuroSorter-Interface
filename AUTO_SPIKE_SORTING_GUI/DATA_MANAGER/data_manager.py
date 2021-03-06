# -*- coding: utf-8 -*-
"""
@authors: %(Val-Calvo, Mikel and Alegre-Cortés, Javier)
@emails: %(mikel1982mail@gmail.com, jalegre@umh.es)
@institutions: %(Dpto. de Inteligencia Artificial, Universidad Nacional de Educación a Distancia (UNED), Postdoctoral Researcher Instituto de Neurociencias UMH-CSIC)
"""
#%%
from DATA_MANAGER.file_IO_01 import nev_manager 
from decorators.time_consuming import timeit 
from scipy.signal import savgol_filter
from scipy.signal import argrelextrema

import numpy as np

class data_manager(nev_manager):
    
    def __init__(self, spk, ae):
        nev_manager.__init__(self)
        self.spk = spk
        self.ae = ae
    
    #%% TAB 1 LOADING AND SELECTING DATA
    def initialize_spike_containers(self):
        self.current ={'channelID':None,'unitID':None,'plotted':[],'selected':[]}
        self.full_spike_dict = {'FileNames':[],'SamplingRate':[],'ExperimentID':[],'Active':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[],'Triggers':[],'Triggers_active':[]}
        
    def get_experiment_channels(self, experimentID):
        channels = []
        ch_activated = []
        for it,channel in enumerate(self.full_spike_dict['ChannelID']):
            if self.full_spike_dict['ExperimentID'][it] == experimentID and not channel in channels:
                channels.append(channel)
                ch_activated.append(self.full_spike_dict['Active'][it])
                
        return channels, ch_activated
    
    def get_experiment_triggers(self, experimentID):   
        return self.full_spike_dict['Triggers'][experimentID], self.full_spike_dict['Triggers_active'][experimentID]
    
    def set_channel_active(self, experimentID, channel, mode=True):
        for it,ch in enumerate(self.full_spike_dict['ChannelID']):
            if ch == channel and self.full_spike_dict['ExperimentID'][it] == experimentID:
                self.full_spike_dict['Active'][it] = mode   
        self.update_spike_dict('channels')
                
    def active_channels(self, experimentID, mode):
        for it,ch in enumerate(self.full_spike_dict['ChannelID']):
            if self.full_spike_dict['ExperimentID'][it] == experimentID:
                self.full_spike_dict['Active'][it] = mode
        self.update_spike_dict('channels')
                
    def set_trigger_active(self, experimentID, trigger_index, mode=True):
        self.full_spike_dict['Triggers_active'][experimentID][trigger_index] = mode
        self.update_spike_dict('triggers')
        
    def update_spike_dict(self, update):
        if update == 'triggers':
            self.spike_dict['Triggers_active'] = self.full_spike_dict['Triggers_active']
        elif update == 'channels':
            self.spike_dict = {'FileNames':[],'SamplingRate':[],'ExperimentID':[],'Active':[],'ChannelID':[],'UnitID':[],'OldID':[],'TimeStamps':[],'Waveforms':[],'Triggers':[],'Triggers_active':[]}
            self.spike_dict['FileNames'] = self.full_spike_dict['FileNames']
            self.spike_dict['SamplingRate'] = self.full_spike_dict['SamplingRate']
            self.spike_dict['Triggers'] = self.full_spike_dict['Triggers']
            self.spike_dict['Triggers_active'] = self.full_spike_dict['Triggers_active']
 
            for it,state in enumerate(self.full_spike_dict['Active']):
                if state:
                    self.spike_dict['ExperimentID'].append( self.full_spike_dict['ExperimentID'][it] )
                    self.spike_dict['Active'].append( self.full_spike_dict['Active'][it] )
                    self.spike_dict['ChannelID'].append( self.full_spike_dict['ChannelID'][it] )
                    self.spike_dict['UnitID'].append( self.full_spike_dict['UnitID'][it] )
                    self.spike_dict['OldID'].append( self.full_spike_dict['OldID'][it] )
                    self.spike_dict['TimeStamps'].append( self.full_spike_dict['TimeStamps'][it] )
                    self.spike_dict['Waveforms'].append( self.full_spike_dict['Waveforms'][it] )
        
    #%% TAB 2 CLEANING AND SORTING
    def show_channelID(self, channelID):
        channelID = int(channelID)
        self.current['channelID'] = channelID
        self.current['plotted'] = [idx for idx, channel in enumerate(self.spike_dict['ChannelID'])  if (channel == channelID and self.spike_dict['UnitID'][idx] != -1)]
        return self.current['plotted']
        
    def show_unitID(self, unitID):
        channelID = self.current['channelID']
        self.current['unitID'] = unitID
        if unitID == 'Noise':
            self.current['plotted'] = [idx for idx, channel in enumerate(self.spike_dict['ChannelID'])  if (channel == channelID and self.spike_dict['UnitID'][idx] == -1)]
        elif unitID == 'All':
            self.current['plotted'] = [idx for idx, channel in enumerate(self.spike_dict['ChannelID'])  if (channel == channelID and self.spike_dict['UnitID'][idx] != -1)]
        else:
            self.current['plotted'] = [idx for idx, channel in enumerate(self.spike_dict['ChannelID'])  if (channel == channelID and self.spike_dict['UnitID'][idx] == int(unitID))]
        return self.current['plotted']

    def selected_unit2ID(self, unit2ID):           
        if unit2ID != 'All':
            if unit2ID == 'Noise':
                unit2ID = -1
            else:
                unit2ID = int(unit2ID)
                
            self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
            
            for sel in self.current['selected']:
                if self.spike_dict['UnitID'][sel] != unit2ID:
                    self.spike_dict['OldID'][sel] = self.spike_dict['UnitID'][sel]
                    self.spike_dict['UnitID'][sel] = unit2ID
                    self.current['plotted'].remove(sel)
            self.current['selected'] = []

        return self.current['plotted']
        
    def undo(self): 
        index = [it for it,oldID in enumerate(self.spike_dict['OldID']) if oldID != None]
        for it in index:
            self.spike_dict['UnitID'][it] = self.spike_dict['OldID'][it]
            if it not in self.current['plotted'] and self.spike_dict['ChannelID'][it] == self.current['channelID']:
                self.current['plotted'].append(it)

        self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
        
        return self.current['plotted']
    
    def delete(self):
        self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
        
        for sel in self.current['selected']:
            self.spike_dict['OldID'][sel] = self.spike_dict['UnitID'][sel]
            self.spike_dict['UnitID'][sel] = -1
            self.current['plotted'].remove(sel)
            
        self.current['selected'] = []
        return self.current['plotted']

    @timeit
    def clean_by_amplitude_threshold(self, r_min, r_max, threshold):
        if self.current['unitID'] != 'Noise':     
            index = np.array([it for it, channel in enumerate(self.spike_dict['ChannelID']) if self.spike_dict['Active'][it] and self.spike_dict['UnitID'][it] != -1])
            # get the corresponding waveforms
            waveforms = np.array(self.spike_dict['Waveforms'])[index]
            
            #detect which units are in the accepted interval, or higher than the threshold
            sub_index = []
            for it,idx in enumerate(index):
            	wave = waveforms[it]
            	peak_min = wave[np.argmin(wave)]
            	if peak_min < r_min or peak_min > r_max or wave.max() > threshold:
            		sub_index.append(idx)
            sub_index = np.array( sub_index )
            
            # reset old unit for undo action
            self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
            for idx in sub_index:
                self.spike_dict['OldID'][idx] = self.spike_dict['UnitID'][idx]
                self.spike_dict['UnitID'][idx] = -1
                if idx in self.current['plotted']:
                    self.current['plotted'].remove(idx)
    
        return self.current['plotted']

     
    @timeit        
    def clean_by_cross_talk(self, window=10):
        # reset old unit for undo action
        self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
        for experimentID in np.unique(self.spike_dict['ExperimentID']):

            index = np.array([it for it, exp in enumerate(self.spike_dict['ExperimentID']) if exp == experimentID and self.spike_dict['UnitID'][it] != -1])
            # compute global average firing rate
            bin_ = int(self.spike_dict['SamplingRate'][experimentID]*window/1000)
            max_ = np.max(self.spike_dict['TimeStamps'])
            num_channels = len(np.unique(self.spike_dict['ChannelID']))
            temporal_pattern = np.zeros( (num_channels, int(max_/bin_)) )

            for it in index:
                stamp = self.spike_dict['TimeStamps'][it]
                x = np.where(np.unique(self.spike_dict['ChannelID']) == self.spike_dict['ChannelID'][it])[0][0]
                y = int(stamp/bin_)-1
                temporal_pattern[x, y] = 1
             
            global_FiringRate = np.mean(temporal_pattern, axis=0)
            # -------------- a threshold must be specified automatically ------
            # compute the amplitude envelope over the global firing rate
            intervalLength = 100 # Experiment with this number, it depends on your sample frequency and highest "whistle" frequency
            outputSignal = []
            for baseIndex in range (intervalLength, len (global_FiringRate)):
                maximum = 0
                for lookbackIndex in range (intervalLength):
                    maximum = max (global_FiringRate [baseIndex - lookbackIndex], maximum)
                outputSignal.append (maximum)

            if np.std(outputSignal) > .3:
                # compute the histogram of the enveloppe and set a threshold
                hist,range_ = np.histogram(outputSignal, bins=10)
                filtered = savgol_filter(hist, 7, 2)
                extrems =  argrelextrema(filtered, np.less)[0]
                detected_modes = [range_[it] for it in extrems]

                try:
                    threshold = detected_modes[0] # --------------> the desired threshold
                except:
                    threshold = .3
                # those units that correspond to bins of the global firing rate that are over the threshold are set as noisy
                for it in index:
                    stamp = self.spike_dict['TimeStamps'][it]
                    check = int(stamp/bin_)-1
                    if global_FiringRate[check] > threshold:
                        self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
                        self.spike_dict['UnitID'][it] = -1 
                        if it in self.current['plotted']:
                            self.current['plotted'].remove(it)
                        
                        
        return self.current['plotted']
    
    @timeit
    def clean(self, n_neighbors=15, min_dist=.1, metric='manhattan'):
        if self.current['unitID'] != 'Noise':
            # reset old unit for undo action
            self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
            channelID = int(self.current['channelID'])
                                
            if self.current['unitID'] != 'All':
                unitID = int(self.current['unitID'])
                index = np.array( [it for it, channel  in enumerate(self.spike_dict['ChannelID']) if channel == channelID and self.spike_dict['UnitID'][it] == unitID and self.spike_dict['UnitID'][it] != -1] )
            else:
                index = np.array( [it for it, channel  in enumerate(self.spike_dict['ChannelID']) if channel == channelID and self.spike_dict['UnitID'][it] != -1] )
            waveforms = np.array([self.spike_dict['Waveforms'][it] for it in index])
            scores = self.spk.run(waveforms, n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
            spike_index = index[scores==1]
            noise_index = index[scores==0]

            for it in spike_index:
                self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
            for it in noise_index:
                self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
                self.spike_dict['UnitID'][it] = -1  
                if it in self.current['plotted']:
                    self.current['plotted'].remove(it)
            
        return self.current['plotted']

    @timeit
    def clean_all(self, n_neighbors=15, min_dist=.1, metric='manhattan'):
        # reset old unit for undo action
        self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
        
        channels_active = []
        for it,channel in enumerate(self.spike_dict['ChannelID']):
            if self.spike_dict['Active'][it] and not channel in channels_active:
                channels_active.append(channel)

        for channelID in channels_active:
            index = np.array([it for it, channel in enumerate(self.spike_dict['ChannelID']) if channel == channelID and self.spike_dict['UnitID'][it] != -1])
            waveforms = np.array([self.spike_dict['Waveforms'][it] for it in index])
            
            scores = self.spk.run(waveforms, n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
            
            spike_index = index[scores==1]
            noise_index = index[scores==0]

            for it in spike_index:
                self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
            for it in noise_index:
                self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
                self.spike_dict['UnitID'][it] = -1  
                if it in self.current['plotted']:
                    self.current['plotted'].remove(it)
                
        return self.current['plotted']    

    
    @timeit
    def sort(self, n_neighbors=15, min_dist=.1, metric='manhattan'):
        if self.current['unitID'] != 'Noise' and self.current['unitID'] != 'All':
            channelID = int(self.current['channelID'])
            unitID = int(self.current['unitID'])
            index_channel = np.array( [it for it, channel  in enumerate(self.spike_dict['ChannelID']) if (channel == channelID and self.spike_dict['UnitID'][it] == unitID and self.spike_dict['UnitID'][it] != -1)] )
            # get the corresponding waveforms
            waveforms = np.array(self.spike_dict['Waveforms'])[index_channel]
            # compute clustering
            UnitIDs = self.ae.sort_spikes(waveforms, n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
            # reset old unit for undo action
            self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
            for index in index_channel:
                self.spike_dict['OldID'][index] = self.spike_dict['UnitID'][index]
            # select the maximun unitID value for the current plotted channel
            index_ch = np.array( [it for it, channel in enumerate(self.spike_dict['ChannelID']) if (channel == channelID and self.spike_dict['UnitID'][it] != -1)] )
            max_unitID = np.array(self.spike_dict['UnitID'])[index_ch].max()+1
            # set new unitIDs for the selected units in the selected channel
            for index,global_index in enumerate(index_channel):
                # first old ID is stored
                self.spike_dict['OldID'][global_index] = self.spike_dict['UnitID'][global_index]
                # second, the new ID is set
                self.spike_dict['UnitID'][global_index] = int(UnitIDs[index]) + max_unitID
            # now correct the unitIDs of all units in the channel, except Noise
            unitIDs_2correct = np.unique( np.asarray(self.spike_dict['UnitID'])[index_ch] )
            for index in index_ch:
                self.spike_dict['UnitID'][index] = list(unitIDs_2correct).index(self.spike_dict['UnitID'][index])+1
            # current unit set to all, current channel is mantained
            self.current['unitID'] = 'All'
            # plotted index is set to current channel
            self.current['plotted'] = list(index_ch)
            
        return self.current['plotted']
    
    @timeit
    def sort_all(self, n_neighbors=15, min_dist=.1, metric='manhattan'):
        # reset old unit for undo action
        self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
        
        channels_active = []
        for it,channel in enumerate(self.spike_dict['ChannelID']):
            if self.spike_dict['Active'][it] and not channel in channels_active:
                channels_active.append(channel)

        for channelID in channels_active:
            index = np.array([it for it, channel in enumerate(self.spike_dict['ChannelID']) if channel == channelID and self.spike_dict['UnitID'][it] != -1])
            waveforms = np.array([self.spike_dict['Waveforms'][it] for it in index])
            
            UnitIDs = self.ae.sort_spikes(waveforms, n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)

            for it, unit in enumerate(UnitIDs):
                self.spike_dict['OldID'][index[it]] = self.spike_dict['UnitID'][index[it]]
                self.spike_dict['UnitID'][index[it]] = unit
                
        self.current['unitID'] = 'All'
        return self.current['plotted']  
    
    @timeit
    def fully_automatic(self, window=10, r_min=-1000, r_max=1000, n_neighbors=15, min_dist=.1, metric='manhattan'):
        # reset old unit for undo action
        self.spike_dict['OldID'] = [None for _ in self.spike_dict['OldID']]
        ######### CROSS TALK ANALYSIS ############################################################
        for experimentID in np.unique(self.spike_dict['ExperimentID']):

            index = np.array([it for it, exp in enumerate(self.spike_dict['ExperimentID']) if exp == experimentID and self.spike_dict['UnitID'][it] != -1])
            # compute global average firing rate
            bin_ = int(self.spike_dict['SamplingRate'][experimentID]*window/1000)
            max_ = np.max(self.spike_dict['TimeStamps'])
            num_channels = len(np.unique(self.spike_dict['ChannelID']))
            temporal_pattern = np.zeros( (num_channels, int(max_/bin_)) )
            
            for it in index:
                stamp = self.spike_dict['TimeStamps'][it]
                temporal_pattern[self.spike_dict['ChannelID'][it]-1, int(stamp/bin_)-1] = 1
             
            global_FiringRate = np.mean(temporal_pattern, axis=0)
            # -------------- a threshold must be specified automatically ------
            # compute the amplitude envelope over the global firing rate
            intervalLength = 100 # Experiment with this number, it depends on your sample frequency and highest "whistle" frequency
            outputSignal = []
            for baseIndex in range (intervalLength, len (global_FiringRate)):
                maximum = 0
                for lookbackIndex in range (intervalLength):
                    maximum = max (global_FiringRate [baseIndex - lookbackIndex], maximum)
                outputSignal.append (maximum)

            if np.std(outputSignal) > .3:
                # compute the histogram of the enveloppe and set a threshold
                hist,range_ = np.histogram(outputSignal, bins=10)
                filtered = savgol_filter(hist, 7, 2)
                extrems =  argrelextrema(filtered, np.less)[0]
                detected_modes = [range_[it] for it in extrems]

                try:
                    threshold = detected_modes[0] # --------------> the desired threshold
                except:
                    threshold = .3
                # those units that correspond to bins of the global firing rate that are over the threshold are set as noisy
                for it in index:
                    stamp = self.spike_dict['TimeStamps'][it]
                    check = int(stamp/bin_)-1
                    if global_FiringRate[check] > threshold:
                        self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
                        self.spike_dict['UnitID'][it] = -1 
                        if it in self.current['plotted']:
                            self.current['plotted'].remove(it)
                        
        ######### AMPLITUDE THRESHOLD ANALYSIS ############################################################
        if self.current['unitID'] != 'Noise':     
            index = np.array( [it for it, channel in enumerate(self.spike_dict['ChannelID']) if self.spike_dict['UnitID'][it] != -1] )
            # get the corresponding waveforms
            waveforms = np.array(self.spike_dict['Waveforms'])[index]
            sub_index = np.array( [idx for it,idx in enumerate(index) if (waveforms[it].min() < r_min or waveforms[it].max() > r_max)] )
            # reset old unit for undo action
            for idx in sub_index:
                self.spike_dict['OldID'][idx] = self.spike_dict['UnitID'][idx]#CHECKEAR
                self.spike_dict['UnitID'][idx] = -1
                if idx in self.current['plotted']:
                    self.current['plotted'].remove(idx)
                    
        ######### CLEANER ANALYSIS ############################################################
        for channelID in np.unique(self.spike_dict['ChannelID']):
    
            index = np.array([it for it, channel in enumerate(self.spike_dict['ChannelID']) if channel == channelID and self.spike_dict['UnitID'][it] != -1])
            waveforms = np.array([self.spike_dict['Waveforms'][it] for it in index])
            
            scores = self.spk.run(waveforms, n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)
            
            spike_index = index[scores==1]
            noise_index = index[scores==0]

            for it in spike_index:
                self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
            for it in noise_index:
                self.spike_dict['OldID'][it] = self.spike_dict['UnitID'][it]
                self.spike_dict['UnitID'][it] = -1  
                if it in self.current['plotted']:
                    self.current['plotted'].remove(it)
                    
        ######### SORTING ANALYSIS ############################################################
        for channelID in np.unique(self.spike_dict['ChannelID']):
            
            index = np.array([it for it, channel in enumerate(self.spike_dict['ChannelID']) if channel == channelID and self.spike_dict['UnitID'][it] != -1])
            waveforms = np.array([self.spike_dict['Waveforms'][it] for it in index])
            
            UnitIDs = self.ae.sort_spikes(waveforms, n_neighbors=n_neighbors, min_dist=min_dist, metric=metric)

            for it, unit in enumerate(UnitIDs):
                self.spike_dict['OldID'][index[it]] = self.spike_dict['UnitID'][index[it]]
                self.spike_dict['UnitID'][index[it]] = unit
                
        self.current['unitID'] = 'All'
        return self.current['plotted']
        
    
    
    
    
    
        
