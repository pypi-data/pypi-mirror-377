import datetime
from src.pynusinov._nusinov_euv import Euvt2021
from src.pynusinov._nusinov_fuv import Fuvt2021
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import xarray as xr


# ssi = pd.read_csv('timed_see_ssi_l3.csv')
# res = ssi[ssi['wavelength'] == 5.5][['time', 'irradiance']].reset_index(drop=True)
# for i in range(6,105):
#     irr = ssi[ssi['wavelength'] == i+0.5]['irradiance'].reset_index(drop=True)
#     irr = irr.rename(f'{i + 0.5}irr')
#     res = pd.concat([res, irr], axis=1)
#
# lyman = pd.read_csv('composite_lyman_alpha.csv')
# lyman = lyman[(lyman['time'] >= '2002-02-09') & (lyman['time'] <= '2021-03-03')].reset_index(drop=True)
#
# res.insert(1,'lac',lyman['irradiance'])
# # res.to_csv('combined_data.csv', index=False)

# data = pd.read_csv('combined_data.csv')
# print(data)
# out = pd.DataFrame(data.iloc[:, 1:].apply(lambda x: x != -1.0).all(True))
# out.columns = ['yes']
# yes = data.iloc[out[out['yes'] == True].index]
# yes = yes.reset_index(drop=True)
# print(yes)
# # yes.to_csv('clear_combined_irradiance.csv', index=False)


#************************************** перевод irradiance в flux ***********************************************
# h = 6.62607015e-34
# c = 299792458
#
# data = pd.read_csv('clear_combined_irradiance.csv')
# print(data)
# for i in range(5, 105, 1):
#     data[f'{i}.5irr'] = data[f'{i}.5irr'].apply(lambda x: (x * (i+0.5)*1.e-9) / (h*c*1.e15))

#****************************************************************************************************************

# излучение в длинах волн уже в потоках
# data = pd.read_csv('fluxes.csv')
# res = data[['time', 'lac']]
#
# for i in range(5,105, 5):
#     summ = data[[f'{i}.5irr', f'{i+1}.5irr', f'{i+2}.5irr', f'{i+3}.5irr', f'{i+4}.5irr']].sum(axis=1)
#     summ.name = f'{i+2}.5irr'
#     res = pd.concat([res, summ], axis=1)
#
# l = 7.5
# i = 0
#
# h = 6.62607015e-34
# c = 299792458
# l_ly = 121.6e-9
# l_irr = l * 1.e-9
#
# irr = res[f'{l}irr']
# lac = res['lac'].apply(lambda x: (x * l_ly / (h*c*1.e15)))
#
# lac_min, lac_max = lac.min(), lac.max()
#
# euvt = Euvt2021()
# spectra = euvt.get_spectral_bands([lac_min, lac_max])['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15)
#
# b0, b1 = -0.00278, 0.00107
# spec1 = lac_min * (b0 + b1 * lac_min)
# spec2 = lac_max * (b0 + b1 * lac_max)
#
# full_spectra = euvt.get_spectral_bands(lac)['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15).reset_index(drop=True)
# df = pd.DataFrame({'irr': irr, 'euvt': full_spectra.iloc[i].reset_index(drop=True)})
# df['diff'] = df['irr'] - df['euvt']
# print(sum(abs(df['irr'] - df['euvt']) / df['irr']) / df.shape[0] * 100)
#
#
# plt.scatter(lac, irr, s=5)
# plt.plot([lac_min, lac_max], spectra.iloc[0], color='red')
# # plt.plot([lac_min, lac_max], [spec1, spec2], color='red')
# plt.show()

# *******************************************************************************************************************

# data = pd.read_csv('fluxes.csv')
# res = data[['time', 'lac']]
#
# for i in range(5,105, 5):
#     summ = data[[f'{i}.5irr', f'{i+1}.5irr', f'{i+2}.5irr', f'{i+3}.5irr', f'{i+4}.5irr']].sum(axis=1)
#     summ.name = f'{i+2}.5irr'
#     res = pd.concat([res, summ], axis=1)
#
# for i in range(20):
#
#     h = 6.62607015e-34
#     c = 299792458
#     l_ly = 121.6e-9
#
#     irr = res[f'{7.5 + i*5}irr']
#     lac = res['lac'].apply(lambda x: (x * l_ly / (h*c*1.e15)))
#
#     lac_min, lac_max = lac.min(), lac.max()
#
#     euvt = Euvt2021()
#     spectra = euvt.get_spectral_bands([lac_min, lac_max])['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15)
#
#     full_spectra = euvt.get_spectral_bands(lac)['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15).reset_index(drop=True)
#     df = pd.DataFrame({'irr': irr, 'euvt': full_spectra.iloc[i].reset_index(drop=True)})
#     df['diff'] = df['irr'] - df['euvt']
#     print(sum(abs(df['irr'] - df['euvt']) / df['irr']) / df.shape[0] * 100)
#
#     plt.scatter(lac, irr, s=5)
#     plt.plot([lac_min, lac_max], spectra.iloc[i], color='red')
#     plt.title(f'Модель Нусинова в диапазоне {5 + i*5}-{10 + i*5} нм', fontsize=14)
#     plt.xlabel('LaC, 10^15 фотонов * м^-2 с^-1', fontsize=14)
#     plt.ylabel('Поток радиоизлучения, 10^15 фотонов * м^-2 с^-1', fontsize=10)
#     plt.savefig(f'plot_{7.5 + i*5}_nm.png')
#     plt.close()

# ************************************** отдельные линии ************************************************************

# data = pd.read_csv('timed_see_lines.csv')
# lyman = pd.read_csv('composite_lyman_alpha.csv')
# lyman = lyman[(lyman['time'] <= '2021-03-03')].reset_index(drop=True)
# data.insert(1,'lac',lyman['irradiance'])
#
# out = pd.DataFrame(data.iloc[:, 1:].apply(lambda x: x != -1.0).all(True))
# out.columns = ['yes']
# yes = data.iloc[out[out['yes'] == True].index]
# yes = yes.reset_index(drop=True)
#
# h = 6.62607015e-34
# c = 299792458
# l_ly = 121.6e-9
#
# data = pd.read_csv('clear_lines.csv')
# # data = data[data['time'] <= '2017-12-31']
#
# wavenegths = [121.6e-9, 28.4e-9, 30.4e-9,36.8e-9,46.5e-9,55.4e-9,58.4e-9,61.0e-9,63.0e-9,70.4e-9,76.5e-9,77.0e-9,78.8e-9, 97.7e-9, 102.6e-9, 103.2e-9]
#
# for i in range(len(wavenegths)):
#     data.iloc[:, i+1] = data.iloc[:, i+1].apply(lambda x: (x * wavenegths[i]) / (h*c*1.e15))
#
# lac_min, lac_max = data['lac'].min(), data['lac'].max()
#
# euvt = Euvt2021()
# spectra = euvt.get_spectral_lines([lac_min, lac_max])['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15)
#
# for i in range(2):
#     full_spectra = euvt.get_spectral_lines(data['lac'])['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15).reset_index(drop=True)
#     df = pd.DataFrame({'irr': data.iloc[:, i+2], 'euvt': full_spectra.iloc[i+1].reset_index(drop=True)})
#     df['diff'] = df['irr'] - df['euvt']
#     print(sum(abs(df['irr'] - df['euvt']) / df['irr']) / df.shape[0] * 100)
#
#     plt.scatter(data['lac'], data.iloc[:, i+2], s=5)
#     plt.plot([lac_min, lac_max], spectra.iloc[i+1], color='red')
#     plt.title(f'Модель Нусинова в диапазоне {round(wavenegths[i+1] * 1.e9, 2)} нм', fontsize=14)
#     plt.xlabel('LaC, 10^15 фотонов * м^-2 с^-1', fontsize=14)
#     plt.ylabel('Поток радиоизлучения, 10^15 фотонов * м^-2 с^-1', fontsize=10)
#     plt.show()
    # plt.savefig(f'line_{round(wavenegths[i+1] * 1.e9, 1)}_nm.png')
    # plt.close()

# ************************************ сумма линии и интервала *******************************************************
# intervals = pd.read_csv('fluxes.csv')
# res = intervals[['time', 'lac']]
# for i in range(5,105, 5):
#     summ = intervals[[f'{i}.5irr', f'{i+1}.5irr', f'{i+2}.5irr', f'{i+3}.5irr', f'{i+4}.5irr']].sum(axis=1)
#     summ.name = f'{i+2}.5irr'
#     res = pd.concat([res, summ], axis=1)
#
# intervals = res
#
# lines = pd.read_csv('clear_lines.csv')
# lines = lines[lines['time'] <= '2021-01-14'].reset_index(drop=True)
#
# h = 6.62607015e-34
# c = 299792458
# wavenegths = [121.6e-9, 28.4e-9, 30.4e-9,36.8e-9,46.5e-9,55.4e-9,58.4e-9,61.0e-9,63.0e-9,70.4e-9,76.5e-9,77.0e-9,78.8e-9, 97.7e-9, 102.6e-9, 103.2e-9]
#
# for i in range(len(wavenegths)):
#     lines.iloc[:, i+1] = lines.iloc[:, i+1].apply(lambda x: (x * wavenegths[i]) / (h*c*1.e15))
#
# intervals['time'] = pd.to_datetime(intervals['time'])
# lines['time'] = pd.to_datetime(lines['time'])
# data = pd.merge(lines, intervals, on='time', how='inner')
# data = data.drop('lac_y', axis=1)
#
# euvt = Euvt2021()
# lac_min, lac_max = data['lac_x'].min(), data['lac_x'].max()
# spectra_bands = euvt.get_spectral_bands([lac_min, lac_max])['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15)
# spectra_lines = euvt.get_spectral_lines([lac_min, lac_max])['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15)
# data['27.5irr'] += data['284irr']
# data['32.5irr'] += data['304irr']
# data['37.5irr'] += data['368irr']
# data['47.5irr'] += data['465irr']
# data['57.5irr'] += data['554irr']
# data['57.5irr'] += data['584irr']
# data['62.5irr'] += data['610irr']
# data['62.5irr'] += data['630irr']
# data['72.5irr'] += data['704irr']
# data['77.5irr'] += data['765irr']
# data['77.5irr'] += data['770irr']
# data['77.5irr'] += data['788irr']
# data['97.5irr'] += data['977irr']
# data['102.5irr'] += data['1026irr']
# data['102.5irr'] += data['1032irr']
#
# spectra_bands.loc[27.5] += spectra_lines.loc[28.4]
# spectra_bands.loc[32.5] += spectra_lines.loc[30.4]
# spectra_bands.loc[37.5] += spectra_lines.loc[36.8]
# spectra_bands.loc[47.5] += spectra_lines.loc[46.5]
# spectra_bands.loc[57.5] += spectra_lines.loc[55.4]
# spectra_bands.loc[57.5] += spectra_lines.loc[58.4]
# spectra_bands.loc[62.5] += spectra_lines.loc[61.0]
# spectra_bands.loc[62.5] += spectra_lines.loc[63.0]
# spectra_bands.loc[72.5] += spectra_lines.loc[70.3]
# spectra_bands.loc[77.5] += spectra_lines.loc[76.5]
# spectra_bands.loc[77.5] += spectra_lines.loc[77.0]
# spectra_bands.loc[77.5] += spectra_lines.loc[78.9]
# spectra_bands.loc[97.5] += spectra_lines.loc[97.7]
# spectra_bands.loc[102.5] += spectra_lines.loc[102.6]
# spectra_bands.loc[102.5] += spectra_lines.loc[103.2]
#
# print(data)
#
# for i in range(16):
#     plt.scatter(data['lac_x'], data[f'{27.5 + 5*i}irr'], s=5)
#     plt.plot([lac_min, lac_max], spectra_bands.loc[27.5 + 5*i], color='red')
#     plt.title(f'Модель Нусинова в диапазоне {25 + 5*i}-{30 + i*5} нм', fontsize=14)
#     plt.xlabel('LaC, $10^{15}$ фотонов * м^-2 с^-1', fontsize=14)
#     plt.ylabel('Поток радиоизлучения, $10^{15}$ фотонов * м^-2 с^-1', fontsize=10)
#     # plt.savefig(f'sum_plot/sum_plot_{27.5 + 5*i}_nm.png')
#     plt.close()

# # ************************ построение всех линий на одном графике *************************************

# data = pd.read_csv('fluxes.csv')
# res = data[['time', 'lac']]
#
# for i in range(5,105, 5):
#     summ = data[[f'{i}.5irr', f'{i+1}.5irr', f'{i+2}.5irr', f'{i+3}.5irr', f'{i+4}.5irr']].sum(axis=1)
#     summ.name = f'{i+2}.5irr'
#     res = pd.concat([res, summ], axis=1)
#
# l = 7.5
# i = 0
#
# h = 6.62607015e-34
# c = 299792458
# l_ly = 121.6e-9
# l_irr = l * 1.e-9
#
# irr = res[f'{l}irr']
# lac = res['lac'].apply(lambda x: (x * l_ly / (h*c*1.e15)))
#
# lac_min, lac_max = lac.min(), lac.max()
#
# euvt = Euvt2021()
# spectra = euvt.get_spectral_bands([lac_min, lac_max])['euv_flux_spectra'].to_pandas().apply(lambda x: x / 1.e15)
#
# b0, b1 = -0.00278, 0.00107
# spec1 = lac_min * (b0 + b1 * lac_min)
# spec2 = lac_max * (b0 + b1 * lac_max)
#
#
# plt.scatter(lac, irr, s=5)
# plt.plot([lac_min, lac_max], spectra.iloc[0], color='red')
# # plt.plot([lac_min, lac_max], [spec1, spec2], color='red')
# plt.show()

# ************************** проверка рисунков 2 и 4 в работе Нусинова

# **************** рисунок 2
# h = 6.62607015e-34
# c = 3e8
# l_304 = 30.4e-9
# l_584 = 58.4e-9
# l_1026 = 102.6e-9
# l_1216 = 121.6e-9
#
# lines = pd.read_csv('timed_see_lines_l3 (1).csv')
# lines['304'] = lines['304'].apply(lambda x: (x * l_304 / (h*c)))
# lines['584'] = lines['584'].apply(lambda x: (x * l_584 / (h*c)))
# lines['1026'] = lines['1026'].apply(lambda x: (x * l_1026 / (h*c)))
# lines['1216'] = lines['1216'].apply(lambda x: (x * l_1216 / (h*c)) / 0.865)
#
# lines['r1'] = lines['304'] / lines['1216']
# lines['r2'] = lines['584'] / lines['1216']
# lines['r3'] = lines['1026'] / lines['1216']
#
#
# lac1, lac2 = 3.5e15, 6.0e15
#
# euvt = Euvt2021()
# spectra = euvt.get_spectral_lines([lac1 / 1e15, lac2 / 1e15])['euv_flux_spectra'].to_pandas()
# spectra.columns = ['lac1', 'lac2']
# lines_model = spectra.iloc[[2, 6, 14], :]
# lines_model['lac1'] = lines_model['lac1'] / lac1
# lines_model['lac2'] = lines_model['lac2'] / lac2
# print(lines_model)
#
# fig2 = pd.read_csv('fig2 dataset.csv')
# line584_x, line584_y = fig2.iloc[[0,1], 0] * 1e15, fig2.iloc[[0,1], 1]
# line304_x, line304_y = fig2.iloc[[2,3], 0] * 1e15, fig2.iloc[[2,3], 1]
# line1026_x, line1026_y = fig2.iloc[[4,5], 0] * 1e15, fig2.iloc[[4,5], 1]
#
#
# x = np.arange(lac1, lac2, 0.1e15)
#
# k1 = 599058976.0 / 4899387576553.0 / 1e15
# b1 = 2216694926673591 / 829988539741758300
# y1 = k1 * x + b1
#
# k2 = 24098070419 / 24431321084864 / 1e15
# b2 = 243580396542973 / 41388267807656970
# y2 = k2 * x + b2
#
# k3 = 14018090258 / 12128171478565 / 1e15
# b3 = 641080954095871 / 68486405548629710
# y3 = k3 * x + b3
#
# spectra1 = euvt.get_spectral_lines(x / 1e15)['euv_flux_spectra'].to_pandas().iloc[[2, 6, 14], :] / x
# print(spectra1)
# diff = abs(spectra1.iloc[0, :] - y1) / 1e9
# plt.plot(diff)
# plt.show()

# plt.xlim(lac1 - 0.1, lac2 + 0.1)
# plt.ylabel(r'$\mathrm{R}$', size=15)
# plt.xlabel(r'$\mathrm{N(L \alpha C), 10^{15}  m^{-2} s^{-1}}$', size=15)
# plt.plot([lac1, lac2], lines_model.iloc[0, :], linewidth=3, color='blue', label='30.4')
# plt.plot([lac1, lac2], lines_model.iloc[1, :], linewidth=3, color='blue', label='58.4')
# plt.plot([lac1, lac2], lines_model.iloc[2, :], linewidth=3, color='blue', label='102.6')
# plt.plot(line584_x, line584_y, linewidth=3, color='red', label='30.4')
# plt.plot(line304_x, line304_y, linewidth=3, color='red', label='58.4')
# plt.plot(line1026_x, line1026_y, linewidth=3, color='red', label='102.6')
#
# plt.plot(x, y1, color='black')
# plt.plot(x, y2, color='pink')
# plt.plot(x, y3, color='yellow')
#
# plt.scatter(lines['1216'], lines['r1'], s=3, color='purple', label='30.4')
# plt.scatter(lines['1216'], lines['r2'], s=3, color='green', label='58.4')
# plt.scatter(lines['1216'], lines['r3'], s=3, color='orange', label='102.6')
# plt.show()

# **************** рисунок 4

# data130 = pd.read_csv('sorce_ssi_l3.csv')
# data200 = pd.read_csv('sorce_ssi_l3 (1).csv')
# datalya = pd.read_csv('composite_lyman_alpha (1).csv')
# merged = pd.merge(data130, data200, on='time')
# merged = pd.merge(merged, datalya, on='time')
# merged.to_csv('fig4_lines_dataset.csv', index=False)
# print(merged)
# data = pd.read_csv('fig4_lines_dataset.csv')
# data = data.drop('wavelength_x', axis=1)
# data = data.drop('wavelength_y', axis=1)
# print(data)
# data.to_csv('fig4_lines_dataset.csv', index=False)

# ****************************

# h = 6.62607015e-34
# c = 3e8
# l_1216 = 121.6e-9
# l_130 = 130.0e-9
# l_200 = 200.0e-9
#
# data = pd.read_csv('fig4_lines_dataset.csv')
# cipher_data = pd.read_csv('fig4 dataset.csv')
#
# data['irr130'] = data['irr130'].apply(lambda x: (x * l_130 / (h*c)))
# data['irr200'] = data['irr200'].apply(lambda x: (x * l_200 / (h*c)))
# data['lya'] = data['lya'].apply(lambda x: (x * l_1216 / (h*c)))
#
#
# lac1, lac2 = 3.5e15, 6.0e15
# x = np.arange(lac1, lac2, 0.1e15)
#
# k1 = 285570890841.0 / 19046424090338.0
# b1 = 3741957686708733 / 88691823605159300
# y1 = k1 * x + b1
#
#
# k2 = 5545796737767 / 18845671267252
# b2 = 24947863847087660 / 3990726119121537
# y2 = k2 * x + b2
#
#
# k3 = 0.0471 / 1e15
# b3 = 0.013437 / 1e15
# y3 = k3 * x + b3
#
# fuvt = Fuvt2021()
# spectra = fuvt.get_spectral_bands([lac1 / 1e15, lac2 / 1e15])['fuv_flux_spectra'].to_pandas()
# spectra.columns = ['lac1', 'lac2']
# lines_model = spectra.iloc[[15, 85], :]
#
# fig, ax1 = plt.subplots()
#
# ax1.plot(x, y3, color='green')
#
# ax1.scatter(data['lya'], data['irr130'] * 1.01, s=3, color='black')
# ax1.plot([lac1, lac2], lines_model.iloc[0, :], color='b')
# ax1.plot(cipher_data.iloc[[0, 1], 0] * 1e15, cipher_data.iloc[[0, 1], 1] * 1e15, color='red')
#
# ax1.set_xlabel(r'$\mathrm{N_{L_{\alpha}}, 10^{15}  m^{-2} s^{-1}}$', size=15)
# ax1.set_ylabel(r'$\mathrm{N_{130}, 10^{15}  m^{-2} s^{-1}}$', size=15)
# ax1.set_xlim(3.5e15, 5.5e15)
# ax1.set_ylim(0.09e15, 0.13e15)
#
# ax2 = ax1.twinx()
#
# ax2.scatter(data['lya'], data['irr200']*0.99, s=3, color='black')
# ax2.plot([lac1, lac2], lines_model.iloc[1, :], color='b')
# ax2.plot(cipher_data.iloc[[2, 3], 0] * 1e15, cipher_data.iloc[[2, 3], 1] * 1e15, color='red')
#
# ax2.set_ylabel(r'$\mathrm{N_{200}, 10^{15}  m^{-2} s^{-1}}$', size=15)
# ax2.set_ylim(6e15, 8e15)
#
# plt.show()

# fuvt = pd.read_csv('fuvt_bands_coeffs.csv')
# data = fuvt[['lband','uband','center']]
# d = pd.read_csv('fuvt.csv')
# data = pd.concat([data,d], axis = 1)
# data['B0'] = data['B0'].apply(lambda x: float(x))
# data['B1'] = data['B1'].apply(lambda x: float(x))
# data.to_csv('new_fuvt_bands_coeffs.csv', index=False)
# plt.plot(abs(fuvt['B0'] - data['B0']))
# plt.show()
#
# plt.plot(abs(data1['B1'] - data2['B1']))
# plt.show()


x = xr.open_dataset('../src/pynusinov/_coeffs/fuvt_bands_coeffs.nc')
print(x.to_pandas())

