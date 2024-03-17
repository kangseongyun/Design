import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm


plt.rcParams['axes.unicode_minus'] = False
plt.rc('font', family= 'Malgun Gothic')

def CO2_Detail(A):
    df = pd.read_csv(A, encoding='UTF-8-SIG', parse_dates=['거래일자'])
    df['거래시간'] = pd.to_timedelta(df['거래시간'].astype(int),unit='h')
    df['거래시점'] = df['거래일자']+df['거래시간']
    cols=['거래일자','거래시간']
    # df['거래시점']=df['거래시점'].dt.strftime('%m-%d-%H')
    a3=pd.DataFrame(df.drop(columns=cols))
    a4=a3.pivot_table(index='거래시점',columns='연료원',values='전력거래량(MWh)')
    cols = ['가스압', 'RPS']
    a4 = pd.DataFrame(a4.drop(columns=cols))
    a7= pd.DataFrame(a4)
    cols = ['유연탄', 'LNG', '무연탄', 'IGCC', '중유', '경유','부생가스','LPG','바이오매스','바이오중유','바이오가스','폐기물','매립가스','기타']
    q1= a7[cols]
    a7=q1.mul(3600) # 단위변환 MWh->MJ
    a7=a7/0.3962
    V1 = (10 ** 9)
    a7['경유'] = a7['경유']*74100/V1  # IPCC
    a7['중유'] = a7['중유']*77400 /V1  # IPCC
    a7['무연탄'] = a7['무연탄']*98300/V1  # IPCC
    a7['유연탄'] = a7['유연탄']*94600/V1  # IPCC
    a7['LNG'] = a7['LNG']*64200/V1  # IPCC
    a7['부생가스'] = a7['부생가스'] * 132700 / V1  # IPCC
    if 'LPG' in a7.columns:
        a7['LPG'] = a7['LPG']*63100/V1  # IPCC
    if '바이오매스' in a7.columns:
        a7['바이오매스'] = a7['바이오매스']*103860/V1
    if '바이오가스' in a7.columns:
        a7['바이오가스'] = a7['바이오가스']*54600/V1
    if '바이오중유' in a7.columns:
        a7['바이오중유'] = a7['바이오중유']*79600/V1
    if '폐기물' in a7.columns:
        a7['폐기물'] = a7['폐기물']*102667/V1
    if 'IGCC' in a7.columns:
        a7['IGCC'] = a7['IGCC'] * (54600+94600)*0.75/(2*V1)
    if '매립가스' in a7.columns:
        a7['매립가스'] = a7['매립가스'] * 54600 / V1
    if '기타' in a7.columns:
        a7['기타'] = a7['기타'] * 132700 / V1
    # tCO2_time = a7.sum(axis=1).to_frame(name='시간별 이산화탄소배출량') #### 시간별 이산화탄소배출량
    a8 = a4.sum(axis=1) #### 시간별 발전량 총합wl
    result=(a7.sum(axis=1)).div(a8,axis=0)
    return result, a7, q1, a4


file_name = '시간대별 전력거래량.csv'

a5, b5, c5, d5 = CO2_Detail(file_name)
diffe0 = d5.sum(axis=1).diff()
diffe0 = diffe0.iloc[1:]
# 이산화탄소 차이 합계
diffc0 = b5.sum(axis=1).diff()
print(diffc0)
diffc0 = diffc0.iloc[1:]

def Data(A):
    data = pd.DataFrame({'diffe0': diffe0, 'diffc0': diffc0})
    diffe3 = data[data.index.month == A]
    Time = pd.DataFrame(diffe3)
    return Time


def Combine(season):
    if season in '봄':
        A = 3
        B = 4
        C = 5
    if season in '여름':
        A = 6
        B = 7
        C = 8
    if season in '가을':
        A = 9
        B = 10
        C = 11
    if season in '겨울':
        A = 12
        B = 1
        C = 2
    Energy3 = Data(A)
    Energy4 = Data(B)
    Energy5 = Data(C)
    w1 = pd.concat([Energy3, Energy4, Energy5], axis=0)
    w1 = w1.reset_index()
    w1['거래시점'] = pd.to_datetime(w1['거래시점']).dt.strftime('%H')
    results = []
    for hour in w1['거래시점'].unique():
        data_hour = w1[w1['거래시점'] == hour]
        X = data_hour['diffe0']
        y = data_hour['diffc0']
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()

        results.append((hour, model.params['diffe0'], model.params['const'], model.rsquared))

        print(f"Hour: {hour}")
        print(model.summary())

    coefficients_data = pd.DataFrame(results, columns=['Hour', '회귀계수', 'const', 'R-squared'])
    coefficients_data['Season'] = season  # Add a 'Season' column

    return coefficients_data

# Perform regression analysis for different seasons
q1 = Combine('봄')
q2 = Combine('여름')
q3 = Combine('가을')
q4 = Combine('겨울')

# Concatenate the results for different seasons
result = pd.concat([q1, q2, q3, q4], axis=0)

# Save the results to a single CSV file
csv_filename = r'C:\Users\user\Desktop\EMS\regression_results.csv'
result.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print("Results saved to CSV file:", csv_filename)