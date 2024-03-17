import pandas as pd
import numpy as np
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator
import openpyxl
from matplotlib.lines import Line2D
from openpyxl import Workbook

plt.rcParams['axes.unicode_minus'] = False
plt.rc('font', family= 'Malgun Gothic')

# Your code for reading the DataFrame and pivoting
df = pd.read_csv(r'C:\Users\user\Desktop\EMS\regression_results.csv', encoding='utf-8-sig')
df1 = df.pivot_table(index='Hour', columns='Season', values='회귀계수')
df1.to_csv(r'C:\Users\user\Desktop\EMS\MEF.csv', index=True, encoding='utf-8-sig')
df2 = df.pivot_table(index='Hour', columns='Season', values='R-squared')
df2.to_csv(r'C:\Users\user\Desktop\EMS\R-squared.csv', index=True, encoding='utf-8-sig')

# Reset the index
df1 = df1.reset_index()
# Reorder the columns as per your preference
df1 = df1[['Hour', '봄', '여름', '가을', '겨울']]

df2 = df2.reset_index()
# Reorder the columns as per your preference
df2 = df2[['Hour', '봄', '여름', '가을', '겨울']]
df3=pd.concat([df1,df2],axis=0)
df3.to_csv(r'C:\Users\user\Desktop\EMS\combine.csv', index=True, encoding='utf-8-sig')
df1 = df1.set_index('Hour')
plt.figure(figsize=(15,10))
# average_emission = 0.4747
# plt.axhline(y=average_emission, color='black', linestyle='--', linewidth=4, label='평균배출계수(송전단)')
plt.plot(df1['봄'], color='blue',linewidth=2, marker='o', markersize=10, label='봄')
plt.plot(df1['여름'], color='orange', linewidth=2, marker='$Z$', markersize=10, label='여름')
plt.plot(df1['가을'], color='green', linewidth=2, marker='x', markersize=10, label='가을')
plt.plot(df1['겨울'], color='red',  linewidth=2, marker='^', markersize=10, label='겨울')
# plt.plot(df1['봄'], color='#D3D3D3',linewidth=2, marker='o', markersize=10, label='봄')
# plt.plot(df1['여름'], color='orange', linewidth=2, marker='$Z$', markersize=10, label='여름')
# plt.plot(df1['가을'], color='#D3D3D3', linewidth=2, marker='x', markersize=10, label='가을')
# plt.plot(df1['겨울'], color='#D3D3D3',  linewidth=2, marker='^', markersize=10, label='겨울')
legend_handles = [
    Line2D([0], [0], color='blue',  linewidth=2, marker='o', markersize=10, label='봄'),
    Line2D([0], [0], color='orange',  linewidth=2, marker='$Z$', markersize=10, label='여름'),
    Line2D([0], [0], color='green',  linewidth=2, marker='x', markersize=10, label='가을'),
    Line2D([0], [0], color='red',  linewidth=2, marker='^', markersize=10, label='겨울'),
    # Line2D([0], [0], color='black', linestyle='--', linewidth=4, label='평균배출계수(송전단)')
]
# legend_handles = [
#     Line2D([0], [0], color='#D3D3D3',  linewidth=2, marker='o', markersize=10, label='봄'),
#     Line2D([0], [0], color='orange',  linewidth=2, marker='$Z$', markersize=10, label='여름'),
#     Line2D([0], [0], color='#D3D3D3',  linewidth=2, marker='x', markersize=10, label='가을'),
#     Line2D([0], [0], color='#D3D3D3',  linewidth=2, marker='^', markersize=10, label='겨울'),
#     # Line2D([0], [0], color='black', linestyle='--', linewidth=4, label='평균배출계수(송전단)')
# ]
plt.legend(handles=legend_handles, loc='upper center', fontsize=20, ncols=5)
plt.tick_params(axis='both', labelsize=20)
plt.xticks(range(len(df1['봄'].index)), df1['봄'].index)
plt.xlabel('Time(H)', fontsize=30, labelpad=20)
plt.ylabel('MEF(tCO$_2$/MWh)', fontsize=30, labelpad=20)
# plt.title('2021년도 계절 및 시간별 MEF',fontsize=25)
plt.grid(True)
plt.ylim([0.2, 1.00])

plt.tight_layout()
plt.savefig(r'C:\Users\user\Desktop\EMS\계절별 MEF 산정결과.tiff', format='tiff', dpi=300)

plt.show()
