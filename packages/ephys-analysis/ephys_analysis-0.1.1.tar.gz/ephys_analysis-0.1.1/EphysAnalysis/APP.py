def main():
    import os
    from datetime import datetime
    import tkinter as tk
    from tkinter import filedialog
    import numpy as np
    import pandas as pd
    import pyabf
    from EphysAnalysis.feature_extractor import SpikeFeatureExtractor, SpikeTrainFeatureExtractor
    import EphysAnalysis.subthresh_features as sbth
    import EphysAnalysis.qc_features as qc
    import EphysAnalysis.spike_train_features as stf
    from EphysAnalysis.event_signal import EventSignal
    
    
    
    root = tk.Tk()
    root.withdraw()
    
    selected_folder = filedialog.askdirectory()
    
    file_paths = []
    
    for root_dir, dirs, files in os.walk(selected_folder):
        for file in files:
            if file.lower().endswith('.abf'):
                file_paths.append(os.path.join(root_dir, file))
    
    num_files = len(file_paths)
    
    
    # filetypes = [('ABF Files', '*.abf')]
    # files = filedialog.askopenfilenames(filetypes=filetypes)
    
    
    out_csv = fr'{selected_folder}\result.csv'
    
    results = dict()
    
    cnt = 0
    
    for file in file_paths:
        cnt += 1
        result = dict()
        file_name = os.path.basename(file)
        print(f'{file_name}: {cnt} / {num_files}')
        f = pyabf.ABF(file)
    
        if f.sweepUnitsC in ['pA', 'nA', 'mA']:   # current clamp
                clamp_mode = 'C'
        else:   # voltage clamp
            clamp_mode = 'V'
        match f.sweepCount:
                case 1:
                    mode = 'gap_free'
                case _:
                    mode = 'episodes'
        if clamp_mode == 'C' and mode == 'gap_free':
            record_mode = 'PSP'
        elif clamp_mode == 'C' and mode == 'episodes':
            record_mode = 'spike'
        elif clamp_mode == 'V' and mode == 'episodes':
            record_mode = 'voltage'
        else:
            record_mode = 'PSC'
    
        if f.sweepCount > 3:   # multi-sweeps
            # folder = out_folder + '\\' + f.abfID
            # if not os.path.exists(folder):
            #     os.mkdir(folder)
            
            result['file'] = f.abfID
    
            f.setSweep(0)
            first_epoc = f.sweepEpochs
            f.setSweep(1)
            second_epoc = f.sweepEpochs
            dif = np.asarray(second_epoc.levels) - np.asarray(first_epoc.levels)
    
            step = dif != 0
            start = np.asarray(first_epoc.p1s)[step][0]
            end = np.asarray(first_epoc.p2s)[step][0]
            d_step = abs(dif[step][0]) 
    
            if record_mode == 'spike':   # current clamp
    
                sampling_rate = f.sampleRate
                temp_result_list = []
    
                rmp = []
                tau = []
                sag = []
    
                t_set = []
                i_set = []
                v_set = []
    
                try:
                    baseline_interval = min(start/(sampling_rate*2), 0.1)
                    sfe = SpikeFeatureExtractor(start=start/sampling_rate, end=end/sampling_rate, filter=2)
                    spte = SpikeTrainFeatureExtractor(start=start/sampling_rate, end=end/sampling_rate, baseline_interval=baseline_interval)
                except Exception as e:
                    pass
    
                for index in f.sweepList:
                    f.setSweep(index)
                    t = f.sweepX
                    v = f.sweepY
                    i = f.sweepC
                    
                    if f.sweepUnitsY == f.sweepUnitsC:
                        v = v/20
                    
                    current = np.median(i[start:end]) 
    
                    try:
    
                        rmp.append(np.median(v[np.where(i == 0)]))
                        if current < 0:
                            
                            tau.append(sbth.time_constant(t=t, v=v, i=i, start=start/sampling_rate, end=(end-2)/sampling_rate, baseline_interval=baseline_interval))
                            sag.append(sbth.sag(t=t, v=v, i=i, start=start/sampling_rate, end=end/sampling_rate, baseline_interval=baseline_interval))
                            t_set.append(t)
                            i_set.append(i)
                            v_set.append(v)
    
                        if current == 0:
                            t_set.append(t)
                            i_set.append(i)
                            v_set.append(v)
    
                        ft = sfe.process(t, v, i)
                        # ft.to_csv(f'{folder}/{index}.csv', index=False)
                        # sptft= spte.process(t=t, v=v, i=i, spikes_df=ft)
                        sptft= spte.process(t=t, v=v, i=i, spikes_df=ft, extra_features=['pause', 'burst'])
                        sptft['injected current (pA)'] = current
                        temp_result_list.append((ft, sptft))
                    except Exception as e:
                        pass
                try:
                    rin = sbth.input_resistance(t_set=t_set, i_set=i_set, v_set=v_set, start=start/sampling_rate, end=end/sampling_rate)
                    result['Rin (MOhms)'] = rin
                    result['RMP (mV)'] = np.nanmean(rmp)
                    result['Tau (ms)'] = np.nanmean(tau) * 1000
                    result['Sag ratio'] = np.nanmean(sag)
                    result['Cm (pF)'] = result['Tau (ms)'] / result['Rin (MOhms)'] * 1000
                except Exception as e:
                    pass
    
                for i_result in temp_result_list:
                    try:
                        if i_result[1]['avg_rate'] > 0:
                            ft0 = i_result[0]
                            spike_result_mean = ft0.mean(numeric_only=True)
                            spike_result_max = ft0.max(numeric_only=True)
                            spike_result_min = ft0.min(numeric_only=True)
                            result['Threshold (mV)'] = spike_result_min['threshold_v']
                            result['Peak (mV)'] = spike_result_max['peak_v']
                            # result['Trough (mV)'] = spike_result['slow_trough_v'] if spike_result['slow_trough_v'] else spike_result['fast_trough_v']
                            
                            result['Trough (mV)'] = spike_result_mean['trough_v']
                            result['Height (mV)'] = result['Peak (mV)'] - result['Trough (mV)']
                            # result['Fast Trough (mV)'] = spike_result['fast_trough_v']
                            # result['Slow Trough (mV)'] = spike_result['slow_trough_v']
                            result['FWHM (ms)'] = spike_result_mean['width'] * 1000
                            result['Upstroke/Downstroke'] = spike_result_mean['upstroke_downstroke_ratio']
                            result['AHP amplitude (mV)'] = result['Threshold (mV)'] - result['Trough (mV)']
    
                            if d_step <= 10:
                                result['Rheobase (pA)'] = spike_result_mean['threshold_i']
                            else:
                                result['Rheobase_estimated (pA)'] = spike_result_mean['threshold_i']
                            break
                    except Exception as e:
                        pass
                try:
                    result['Adaptation index'] = None
                    result['Delay'] = 'non-delay'
                    result['Pause'] = 'non-pause'
                    result['Burst'] = 'non-burst'
                    result['Silence'] = 'non-silence'
    
                    # with open(f'{folder}/result.txt', mode='w', encoding='utf-8') as result_txt_file:
                    #     for i_result in temp_result_list:
                    #         result_txt_file.write(str(i_result[1]))
                    #         result_txt_file.write('\n')
    
                    last_rate = 0
                    stim_current = []
                    rates = []
                    spike_numbers = []
    
                    for i_result in temp_result_list:
                        rate = i_result[1]['avg_rate']
                        current = i_result[1]['injected current (pA)']
                        stim_current.append(current)
                        rates.append(rate)
                        spike_numbers.append(i_result[1]['spike_number'])
                        result[f'Spike Frequency - {current} pA (Hz)'] = rate
    
                        if rate < last_rate:
                            break
                        if  result['Adaptation index'] is None and 'adapt' in i_result[1] and i_result[1]['adapt'] > 0:
                            result['Adaptation index'] = i_result[1]['adapt']
                        if 'latency' in i_result[1] and 'Delay Ratio' not in result:
                            result['Delay Ratio'] = i_result[1]['latency'] / i_result[1]['mean_isi']
                        if current <= result['Rheobase (pA)']:
                            continue
                        if result['Pause'] != 'Pause' and 'pause' in i_result[1] and i_result[1]['pause'][0] > 0:
                            result['Pause'] = 'Pause'
                            result['No. of Pause'] = i_result[1]['pause'][0]
                            result['Pause Fraction'] = i_result[1]['pause'][1]
                        if result['Burst'] != 'Burst' and 'burst' in i_result[1] and i_result[1]['burst'][1] > 0:
                            result['Burst'] = 'Burst'
                            result['Burst Index'] = i_result[1]['burst'][0]
                            result['No. of Burst'] = i_result[1]['burst'][1]
                        if result['Delay']!= 'Delay' and 'latency' in i_result[1] and result['Delay Ratio'] > 1:
                            result['Delay'] = 'Delay'
                            result['Delay Ratio'] = i_result[1]['latency'] / i_result[1]['mean_isi']
                        if result['Silence']!= 'Silence' and 'pfs' in i_result[1] and 'last_isi' in i_result[1] and i_result[1]['last_isi'] != np.nan and i_result[1]['pfs'] > i_result[1]['last_isi'] * 2:
                            result['Silence'] = 'Silence'
                except Exception as e:
                    pass
                    try:
                        last_rate = rate
                    except Exception as e:
                        pass
                
                ar_num_spikes = np.asarray(spike_numbers)
                if len(ar_num_spikes) > 0 and np.max(ar_num_spikes) == 1:
                    result['Single'] = 'Single'
                else:
                    result['Single'] = 'non-single'
                try:
                    result['FI Curve Slope'] = stf.fit_fi_slope(stim_amps=stim_current, avg_rates=rates)
                except Exception as e:
                    pass
    
            elif record_mode == 'voltage':
                # QC
                rin_v = []
                r_access = []
                time_constant = []
    
                ina = dict()
    
                try:
    
                    for index in f.sweepList:
                        f.setSweep(index)
                        v, t, i = f.sweepC[:start-1], f.sweepX[:start-1], f.sweepY[:start-1]
                        holding_current = np.median(i[np.where(v == f.sweepEpochs.levels[0])])
                        rin_v.append(qc.measure_input_resistance(v, i, t))
                        r_access.append(qc.measure_initial_access_resistance(v, i, t))
                        time_constant.append(qc.measure_time_constant(v, i, t))
                        v_step = np.median(f.sweepC[start:end])
                        i_peak = np.min(f.sweepY[start:end]) - holding_current
    
                        ina[f'Inward current peak - {v_step} mV (pA)'] = i_peak
                            
                    result['Rin_vclamp (MOhms)'] = np.nanmean(rin_v)
                    result['Access resistance (MOhms)'] = np.nanmean(r_access)
                    result['Tau_vclamp (ms)'] = np.nanmean(time_constant) * 1000
    
                    result.update(ina)
                except Exception as e:
                    pass
            
        elif record_mode == 'PSC':
            try:
                f.setSweep(0)
                data = f.sweepY
                es = EventSignal(data, threshold=6, rate=sampling_rate, positive=False)
                es.adjust_baseline()
                result['Mean Frequency (Hz)'] = es.frequency
                result['Mean Amplitude (pA)'] = np.nanmean(es.events[1])
                result['Max Amplitude (pA)'] = np.nanmax(es.events[1])
                result['Rise time 10 - 90 (msec)'] = np.nanmedian(es.rise1090) * 1000
                result['Decay time 10 - 90 (msec)'] = np.nanmedian(es.decay1090) * 1000
                result['Mean FWHM (msec)'] = np.nanmedian(es.fwhm) * 1000
            except Exception:
                continue
        elif record_mode == 'PSP':
            try:
                f.setSweep(0)
                v = f.sweepY
                i = f.sweepC
                
                if f.sweepUnitsY == f.sweepUnitsC:
                    v = v/20
                es = EventSignal(v, positive=True, threshold=2.58, rate=sampling_rate)
                amp = es.events[1]
                result['Mean Frequency (Hz)'] = es.frequency
                result['Mean Amplitude (pA)'] = np.nanmean(amp)
                result['Max Amplitude (pA)'] = np.nanmax(amp)
                result['Rise time 10 - 90 (msec)'] = np.nanmedian(es.rise1090) * 1000
                result['Decay time 10 - 90 (msec)'] = np.nanmedian(es.decay1090) * 1000
                result['Mean FWHM (msec)'] = np.nanmedian(es.fwhm) * 1000
        
                spikes = amp[amp>-20]
                result["Mean Frequency of sAPs (Hz)"] = len(spikes) / f.sweepX[-1]
                result["Mean Amplitude of sAPs (pA)"]  = np.nanmean(spikes)
            except Exception:
                pass
    
        if 'file' in result:
            results[result['file']] = result.copy()
            result.clear()
    
    pd.DataFrame(results).T.to_csv(out_csv)
    
    
    
                
                
                

if __name__ == "__main__":
    main()
