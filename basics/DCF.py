
import numpy as np
import pandas as pd
import plotly.express as px
import scipy.optimize as optimize
import yfinance as yf
import sys
import pandas as pd
import time

print('')
print('Following program is non-case sensitive, inputs can be typed in lower cases and upper cases.')

print('')

stock = input('Ticker for Stock for DCF: ')
stock = stock.upper()
print(stock)
print('------------------------------------------------------------------------------------------------------------------')
index = '^' + input('Benchmark index for the ticker: ')
index = index.upper()
print(index)
print('Estimated Duration: 50 Seconds')
print('------------------------------------------------------------------------------------------------------------------')
simulations = int(input('Number of simulations you want to perform: '))
print('Number of simulations =', simulations )
projected_years = 6

forecasting_years = [2022,2023,2024,2025,2026,2027]
known_years = np.asarray(['2018','2019','2020','2021'], dtype='float64')

growth_rate = float(input('Growth rate of the country where the stock is listed(%): '))/100
tax_rate = float((input('Corporate Tax Rate in the Country where stock is listed(%): ')))
risk_free = float(input('Risk Free Rate in the Country where stock is listed(%): '))

def correlation(x, y):
    
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    p = x - mean_x
    q = y - mean_y

    return np.sum(p*q)/np.sqrt(np.sum(p**2)*np.sum(q**2))

## CashFlow Table

info = yf.Ticker(stock).info
balance_sheet = yf.Ticker((stock)).balancesheet
financials = yf.Ticker(stock).financials
cash_flow = yf.Ticker(stock).cashflow

total_revenue = financials.loc['Total Revenue']
gross_profit = financials.loc['Gross Profit']
research_dev = financials.loc['Research And Development'].fillna(0)
selling_g_a = financials.loc['Selling General And Administration']
ebit = financials.loc['EBIT']
dep_amor = cash_flow.loc['Depreciation And Amortization']
tax_rate = 0.25
operating_taxes = np.array(ebit) * tax_rate
cash = balance_sheet.loc['Cash And Cash Equivalents']
capex = cash_flow.loc['Capital Expenditure']
current_assets = balance_sheet.loc['Current Assets']
current_liab = balance_sheet.loc['Current Liabilities']
non_cash_working = current_assets - cash - current_liab
nopat = ebit - operating_taxes
change_in_nwc = -1*non_cash_working.shift(-1) + non_cash_working

df_1 =  pd.DataFrame({
    'Revenue': total_revenue,
    'COGS': total_revenue - gross_profit,
    'Gross Profit': gross_profit,
    'Research and Dev': research_dev,
    'SGA': selling_g_a,
    'Total Operating Expense': research_dev + selling_g_a,
    'EBITDA': ebit + dep_amor,
    'Depreciation': dep_amor,
    'EBIT': ebit,
    'Operating Taxes': operating_taxes,
    'NOPAT': nopat,
    'Cash': cash,
    'CapEx': capex,
    'Current Assets': current_assets,
    'Current Liabilities': current_liab,
    'Non-Cash Working Capital': non_cash_working,
    'Change in NWC': change_in_nwc,
    'Unlevered Free CashFlows': nopat + dep_amor + capex - change_in_nwc
})

cash_flow_table = np.transpose(df_1.iloc[::-1]) 
print('')
print(cash_flow_table)
print('')
print('------------------------------------------------------------------------------------------------------------------')

## WACC Calculation

def linalgforcashflow(known_years, variable):
        
    r = -correlation(known_years, variable)
    sx = np.std(known_years)
    sy = np.std(variable)
    b = r*sy/sx
    
    return b

slope_cashflow = linalgforcashflow(known_years, nopat + dep_amor + capex - change_in_nwc)

cash_flows = np.array(cash_flow_table.loc['Unlevered Free CashFlows'])

for i in range(1, len(cash_flows)):
    if cash_flows[i] < 0:
        print("Cashflow of", i, "Year is Negative")
    else:
        print("Cashflow of", i, "Year is Positive")

if slope_cashflow>0:
    print('Analysing by Linear Regression, Historic Cashflow is POSITIVE')

if slope_cashflow < 0:
    print('Analysing by Linear Regression, Historic Cashflow Trend is NEGATIVE')
    
print('Do you want to Continue?')
print('Type Yes')
print('Else type No')

choice_1 = input('Do you want to continue?: ')
choice_1 = choice_1.upper()

if choice_1 == 'NO':
    print('DCF ABORTED')

else:    

    equity = balance_sheet.loc['Stockholders Equity'].iloc[0]
    debt = info['totalDebt']
    interest_expense = (financials.loc['Interest Expense'].iloc[0])

    if interest_expense is None:
        interest_expense = 0    

    cost_of_debt = -interest_expense/debt
    print('')
   
    realised_rax_rate = tax_rate/100
    dde = debt/(debt + equity)
    after_tax_cod = cost_of_debt*(1-realised_rax_rate)
    
    print('')
    realised_risk_free = risk_free/100

    combined = [stock] + [index]
    df_specialised = yf.download(combined, period = '10y', interval = '1d')['Close']
    df_combined = yf.download(combined, period = '10y', interval = '1d')['Close'].pct_change().dropna()
    
    def Historic(stock_pct):
        return np.prod(1+stock_pct, axis = 0)**(1/10) - 1

    index_return = Historic(df_combined).iloc[1]
    stock_return = Historic(df_combined).iloc[0]

    market_premium = index_return - realised_risk_free

    covariance = df_combined.cov()
    betas = covariance.loc[index]/df_combined[index].var()

    beta_stock = betas.iloc[0]
    ede = equity/(equity + debt)
    cost_of_equity = realised_risk_free + beta_stock*(market_premium)

    wacc = cost_of_equity*ede + after_tax_cod*(dde)

    wacc_table = np.transpose(pd.DataFrame({
        
        'Equity': equity,
        'Debt': debt,
        'Interest Expense': interest_expense,
        'Cost of Debt': cost_of_debt,
        'Tax Rate (%)': tax_rate,
        'D/D+E': dde,
        'After Tax cost of Debt': after_tax_cod,
        'Risk Free Rate': risk_free,
        'Expected Index': index_return,
        'Market Premium': market_premium,
        'Beta': beta_stock,
        'E/D+E': ede,
        'Cost of Equity': cost_of_equity,
        'WACC': wacc

    }, index = ['WACC Calculation']))

    print('If you want to see WACC Calculation Table, type yes, else type no')
    print('If you want do not want to see any calculation table from now on, type X')

    yn = input('Your Preference is: ')
    yn = yn.lower()

    if yn == 'yes':
        print(wacc_table)
    if yn == 'no':
        print('')    
    if yn == 'x':
        print('')   

    print('WACC (%) =', np.round(wacc*100,2), '%')
    print('Beta of Stock:', np.round(beta_stock,2))

    ## Defining a function for Pearsons correlation coefficent 

    def correlation(x, y):
        
        mean_x = np.mean(x)
        mean_y = np.mean(y)
        p = x - mean_x
        q = y - mean_y

        return np.sum(p*q)/np.sqrt(np.sum(p**2)*np.sum(q**2))

    ## defining a function for Linear Regression Algorithm

    def linalg(known_years, variable, forecasting_years):
        
        r = -correlation(known_years, variable)
        sx = np.std(known_years)
        sy = np.std(variable)
        x_mean = np.mean(known_years)
        y_mean = np.mean(variable)

        b = r*sy/sx
        a = y_mean - b*x_mean

        forecasted_values = []
        for years in forecasting_years:
            forecasted_values.append(a + b*years)
        
        return forecasted_values

    corerlation_coeff = correlation(ebit, total_revenue)

    ## Giving Choices

    forecasting_choices = ['Monte Carlo', 'Holt-Winters Forecasting', 'Linear Forecasting Model']

    print('We will now be Forecasting CashFlow Components, Below are the instructions:')
    print('If you type A, then the forecasting of cashflow components will be done through Monte Carlo simulations with Custom modification.')
    print('If you type C, then forecasting will be done through Linear regression.')

    print('')
    print('Forecasting CashFlow Component #1: Net Operating Profit After Taxes (NOPAT)')
    choicece = input('Your Choice for Forecasting NOPAT is: ')

    if choicece == 'A' or 'a':
        choicece = 0  
    elif choicece == 'B' or 'b':
        choicece = 1
    elif choicece == 'C' or 'c':
        choicece = 2 
            
    choice = forecasting_choices[choicece]

## Forecasting NOPAT with Monte Carlo with all 3 methods


ebit_pct_revenue = ebit/total_revenue[::-1]
ebit_pct_revnue_mean = ebit_pct_revenue.mean()

revenue_growth_pct = cash_flow_table.loc['Revenue']/cash_flow_table.loc['Revenue'].shift(1) - 1 
revenue_growth_mean = revenue_growth_pct.mean()

if choice == 'Monte Carlo':

    print('Forecasting CashFlow Component #1: Net Operating Profit After Taxes (NOPAT)')

    print('Average Revenue Growth (%) =', np.round(revenue_growth_pct.mean()*100), '%')
    
    print('Projected Years =', projected_years)

    

    print('Do you want to input the lower bounds and upper bounds OR go with basic theory of Monte Carlo Simulations?, you can change your choices in the next projections as well.')
    print('if Custom modification, Type CUSTOM')
    print('If you want to go with basic theory, Type BASIC')

    query_1 = input('Your Choice for Monte Carlo is: ')
    query_1 = query_1.upper()

    if query_1 == 'CUSTOM':

        shg = float(input('Higher Bound for Revenue Growth in (%): '))
        selected_parameter_higher_bound = shg/100
        print('upper bound for revenue:',selected_parameter_higher_bound*100,'%')
        lhg = float(input('Lower Bound for Revenue Growth in (%): '))
        selected_parameter_lower_bound = lhg/100
        print('lower bound for revenue:', selected_parameter_lower_bound*100, '%')
        

        random_revenue_growthpct = []
        for i in range(simulations):
            random_revnue_X = []
            for i in range(projected_years):
                random_revenue = np.random.randint(selected_parameter_lower_bound*1000000,
                                                    selected_parameter_higher_bound*1000000)/1000000
                random_revnue_X.append(random_revenue)
            random_revenue_growthpct.append(random_revnue_X)

        table_for_random_rev_rate = pd.concat([pd.DataFrame([random_revenue_growthpct[i]]) 
                                                    for i in range(len(random_revenue_growthpct))],
                                                    ignore_index=True)

        first_rev_projection = total_revenue[0]*(1+table_for_random_rev_rate[0])   
        second_rev_projection = first_rev_projection*(1+table_for_random_rev_rate[1])
        third_rev_projection = second_rev_projection*(1+table_for_random_rev_rate[2])
        fourth_rev_projection = third_rev_projection*(1+table_for_random_rev_rate[3])
        fifth_rev_projection = fourth_rev_projection*(1+table_for_random_rev_rate[4])
        sixth_rev_projection = fifth_rev_projection*(1+table_for_random_rev_rate[5])

        projected_rev = pd.DataFrame({
            
            'First Year Projection': first_rev_projection,
            'Second Year Projection': second_rev_projection,
            'Third Year Projection': third_rev_projection,
            'Fourth Year Projection': fourth_rev_projection,
            'Fifth Year Projection': fifth_rev_projection,
            'Sixth Year Projection': sixth_rev_projection
        })    

        print('Co-Relation Coefficeint between Revenue and EBIT =',np.round(corerlation_coeff*100,2), '%')

        if corerlation_coeff > 0.70:
            
            print('As Corelation Coefficient is greater than 70%, Running for normal projections')

            projected_ebit = projected_rev*ebit_pct_revnue_mean
            operating_tax = projected_ebit*realised_rax_rate
            NOPAT = projected_ebit - operating_tax

            print('')
            print('Forecasting for NOPAT taking as ' + '%' + ' of Revenue through Monte Carlo Simulations')
            print('')
            
            if yn == 'x':
                print('')
            
            else:
                
                ss= input('Do you want to see NOPAT Monte Carlo Calculation, type yes or no: ')
                ss = ss.lower()
                        
                if ss == 'yes':
                    print(NOPAT)
                elif ss == 'no':
                    print('')
                
        else:
            print('As Revenue and EBIT are not Co-Related Strongly, forecasting cashfllow components with linear regression') 

            lin_revenue_forc = linalg(known_years, total_revenue, forecasting_years)
            lin_projected_ebit = np.array(lin_revenue_forc)*ebit_pct_revnue_mean
            lin_operating_tax = lin_projected_ebit*realised_rax_rate

            NOPAT = lin_projected_ebit - lin_operating_tax

            print(NOPAT)

    elif query_1 == 'BASIC':

        print('What assumption do you want to make?')
        print('1) Best Case Scenario (type BEST)')
        print('2) Normal Case Scenario (type NORMAL)')
        print('3) Worst Case Scenario (type WORST)')
        
        query_basic = input('Your assumtion: ')
        query_basic = query_basic.upper()

        if query_basic == 'BEST':

            lower_bound_rev = abs(revenue_growth_mean)/3.14
            higher_bound_rev = 1.614*abs(revenue_growth_mean) 

        elif query_basic == 'NORMAL':

            lower_bound_rev = 0
            higher_bound_rev = abs(revenue_growth_mean)

        elif query_basic == 'WORST':

            lower_bound_rev = -2*abs(revenue_growth_mean)
            higher_bound_rev = abs(revenue_growth_mean)/2  


        selected_parameter_higher_bound = higher_bound_rev
        print('upper bound for revenue:',np.round(selected_parameter_higher_bound*100,2),'%')
        
        selected_parameter_lower_bound = lower_bound_rev
        print('lower bound for revenue:', np.round(selected_parameter_lower_bound*100,2), '%')

        rev_choice = input('Above are Assumptions taken for projection, if you want to continue, type YES, if you want to change the assumptions, type CHANGE: ')
        rev_choice = rev_choice.upper()

        if rev_choice == 'CHANGE':

            shg = float(input('Higher Bound for Revenue Growth in (%): '))
            selected_parameter_higher_bound = shg/100
            print('upper bound for revenue:',selected_parameter_higher_bound*100,'%')
            lhg = float(input('Lower Bound for Revenue Growth in (%): '))
            selected_parameter_lower_bound = lhg/100
            print('lower bound for revenue:', selected_parameter_lower_bound*100, '%')

            random_revenue_growthpct = []
            for i in range(simulations):
                random_revnue_X = []
                for i in range(projected_years):
                    random_revenue = np.random.randint(selected_parameter_lower_bound*1000000,
                                                        selected_parameter_higher_bound*1000000)/1000000
                    random_revnue_X.append(random_revenue)
                random_revenue_growthpct.append(random_revnue_X)

            table_for_random_rev_rate = pd.concat([pd.DataFrame([random_revenue_growthpct[i]]) 
                                                        for i in range(len(random_revenue_growthpct))],
                                                        ignore_index=True)

            first_rev_projection = total_revenue[0]*(1+table_for_random_rev_rate[0])   
            second_rev_projection = first_rev_projection*(1+table_for_random_rev_rate[1])
            third_rev_projection = second_rev_projection*(1+table_for_random_rev_rate[2])
            fourth_rev_projection = third_rev_projection*(1+table_for_random_rev_rate[3])
            fifth_rev_projection = fourth_rev_projection*(1+table_for_random_rev_rate[4])
            sixth_rev_projection = fifth_rev_projection*(1+table_for_random_rev_rate[5])

            projected_rev = pd.DataFrame({
                
                'First Year Projection': first_rev_projection,
                'Second Year Projection': second_rev_projection,
                'Third Year Projection': third_rev_projection,
                'Fourth Year Projection': fourth_rev_projection,
                'Fifth Year Projection': fifth_rev_projection,
                'Sixth Year Projection': sixth_rev_projection
            })    

            print('Co-Relation Coefficeint between Revenue and EBIT =',np.round(corerlation_coeff*100,2), '%')

            if corerlation_coeff > 0.70:
                
                print('As Corelation Coefficient is greater than 70%, Running for normal projections')

                projected_ebit = projected_rev*ebit_pct_revnue_mean
                operating_tax = projected_ebit*realised_rax_rate
                NOPAT = projected_ebit - operating_tax

                print('')
                print('Forecasting for NOPAT taking as ' + '%' + ' of Revenue through Monte Carlo Simulations')
                print('')
                
                if yn == 'x':
                    print('')
                
                else:
                    
                    ss= input('Do you want to see NOPAT Monte Carlo Calculation, type yes or no: ')
                    ss = ss.lower()
                            
                    if ss == 'yes':
                        print(NOPAT)
                    elif ss == 'no':
                        print('')

        else:

            random_revenue_growthpct = []
            for i in range(simulations):
                random_revnue_X = []
                for i in range(projected_years):
                    random_revenue = np.random.randint(selected_parameter_lower_bound*1000000,
                                                        selected_parameter_higher_bound*1000000)/1000000
                    random_revnue_X.append(random_revenue)
                random_revenue_growthpct.append(random_revnue_X)

            table_for_random_rev_rate = pd.concat([pd.DataFrame([random_revenue_growthpct[i]]) 
                                                        for i in range(len(random_revenue_growthpct))],
                                                        ignore_index=True)

            first_rev_projection = np.array(total_revenue)[0]*(1+table_for_random_rev_rate[0])   
            second_rev_projection = first_rev_projection*(1+table_for_random_rev_rate[1])
            third_rev_projection = second_rev_projection*(1+table_for_random_rev_rate[2])
            fourth_rev_projection = third_rev_projection*(1+table_for_random_rev_rate[3])
            fifth_rev_projection = fourth_rev_projection*(1+table_for_random_rev_rate[4])
            sixth_rev_projection = fifth_rev_projection*(1+table_for_random_rev_rate[5])

            projected_rev = pd.DataFrame({
                
                'First Year Projection': first_rev_projection,
                'Second Year Projection': second_rev_projection,
                'Third Year Projection': third_rev_projection,
                'Fourth Year Projection': fourth_rev_projection,
                'Fifth Year Projection': fifth_rev_projection,
                'Sixth Year Projection': sixth_rev_projection
            })    

            print('Co-Relation Coefficeint between Revenue and EBIT =',np.round(corerlation_coeff*100,2), '%')

            if corerlation_coeff > 0.70:
                
                print('As Corelation Coefficient is greater than 70%, Running for normal projections')

                projected_ebit = projected_rev*ebit_pct_revnue_mean
                operating_tax = projected_ebit*realised_rax_rate
                NOPAT = projected_ebit - operating_tax

                print('')
                print('Forecasting for NOPAT taking as ' + '%' + ' of Revenue through Monte Carlo Simulations')
                print('')
                
                if yn == 'x':
                    print('')
                
                else:
                    
                    ss= input('Do you want to see NOPAT Monte Carlo Calculation, type yes or no: ')
                    ss = ss.lower()
                            
                    if ss == 'yes':
                        print(NOPAT)
                    elif ss == 'no':
                        print('')
                
            else:
                
                print('As Revenue and EBIT are not Co-Related Strongly, forecasting cashfllow components with linear regression') 

                lin_revenue_forc = linalg(known_years, total_revenue, forecasting_years)
                lin_projected_ebit = np.array(lin_revenue_forc)*ebit_pct_revnue_mean
                lin_operating_tax = lin_projected_ebit*realised_rax_rate

                NOPAT = lin_projected_ebit - lin_operating_tax

                print(NOPAT)


elif choice == 'Linear Forecasting Model':
    
    print('Forecasting NOPAT with Linear Regression Forecasting Model')

    lin_revenue_forc = linalg(known_years, total_revenue, forecasting_years)
    lin_projected_ebit = np.array(lin_revenue_forc)*ebit_pct_revnue_mean
    lin_operating_tax = lin_projected_ebit*realised_rax_rate

    NOPAT = lin_projected_ebit - lin_operating_tax

    print(NOPAT)


## Depreciation and Amortisation

print('We will now  bw forecasting other cashflow components, if you want all your assumptions to be same as before, type SAME, else type DIFF.')

chooice_dep_11 = input('SAME or DIFF?: ')
chooice_dep_11 = chooice_dep_11.upper()

dep_amor_growth_mean = (cash_flow_table.loc['Depreciation']/cash_flow_table.loc['Depreciation'].shift(1) - 1).mean() 

if chooice_dep_11 == 'DIFF':

    print('We will now be forecasting cashflow component #2, Depreciation and Amortisation.')
    print('If you type A, then the foecasting of cashflow components will be done through Monte Carlo simulations with Custom modification.')
    print('If you type C, then forecasting will be done through Linear regression.')

    choice_dep = input('Your choice to forecast Depreciation and Amortisation is: ')
    choice_dep = choice_dep.upper()

    if choice_dep == 'A':
        
        print('Average Depreciation Growth =', np.round((dep_amor_growth_mean)*100,2), '%')
        dep_simulations = simulations
        print('Simulations =', simulations)
        print('Projected Years =', projected_years)

        print('Do you want to input the lower bounds and upper bounds OR go with basic theory of Monte Carlo Simulations?, you can change your choices in the next projections as well.')
        print('if Custom modification, Type CUSTOM')
        print('If you want to go with basic theory, Type BASIC')

        query_2 = input('Your Choice for Monte Carlo is: ')
        query_2 = query_2.upper()

        if query_2 == 'CUSTOM':

            print('For this section you can refer average growth rate printed above.')
            
            shg = float(input('Higher Bound for Depreciation Growth in (%): '))
            selected_parameter_higher_bound = shg/100
            print('upper bound for Depreciation Growth:',selected_parameter_higher_bound*100,'%')
            lhg = float(input('Lower Bound for Depreciation Growth in (%): '))
            selected_parameter_lower_bound = lhg/100
            print('lower bound for Depreciation Growth:', selected_parameter_lower_bound*100, '%')

            random_dep_growthpct = []
            
            for i in range(simulations):
                random_dep_X = []
                
                for i in range(projected_years):
                    random_dep = np.random.randint(selected_parameter_lower_bound*1000000,
                                                        selected_parameter_higher_bound*1000000)/1000000
                    random_dep_X.append(random_dep)
                random_dep_growthpct.append(random_dep_X)

            table_for_dep_rev_rate = pd.concat([pd.DataFrame([random_dep_growthpct[i]]) 
                                                        for i in range(len(random_dep_growthpct))],
                                                        ignore_index=True)


            first_dep_projection = dep_amor[0]*(1+table_for_dep_rev_rate[0])   
            second_dep_projection = first_dep_projection*(1+table_for_dep_rev_rate[1])
            third_dep_projection = second_dep_projection*(1+table_for_dep_rev_rate[2])
            fourth_dep_projection = third_dep_projection*(1+table_for_dep_rev_rate[3])
            fifth_dep_projection = fourth_dep_projection*(1+table_for_dep_rev_rate[4])
            sixth_dep_projection = fifth_dep_projection*(1+table_for_dep_rev_rate[5])

            projected_dep = pd.DataFrame({
                
                'First Year Projection': first_dep_projection,
                'Second Year Projection': second_dep_projection,
                'Third Year Projection': third_dep_projection,
                'Fourth Year Projection': fourth_dep_projection,
                'Fifth Year Projection': fifth_dep_projection,
                'Sixth Year Projection': sixth_dep_projection
            
            })               

            if yn == 'x':
                print('') 
            
            else:
                
                dep_yes = input('Do you want to see Depreciation Monte Carlo Table?, type YES, else NO:')   
                dep_yes = dep_yes.upper()

                if dep_yes == 'YES':
                
                    print('Depreciation Monte Carlo Simulations')
                    print(projected_dep)
        
        if query_2 == 'BASIC':

            print('What assumption do you want to make?')
            print('1) Best Case Scenario (type BEST)')
            print('2) Normal Case Scenario (type NORMAL)')
            print('3) Worst Case Scenario (type WORST)')
            
            query_basic_dep = input('Your assumtion: ')
            query_basic_dep = query_basic_dep.upper()

            
            if query_basic_dep == 'BEST':

                lower_bound_dep = abs(dep_amor_growth_mean)/np.pi
                higher_bound_dep = np.pi*(abs(dep_amor_growth_mean))

            elif query_basic_dep == 'NORMAL':

                lower_bound_dep = 0
                higher_bound_dep = abs(dep_amor_growth_mean)

            elif query_basic_dep == 'WORST':

                lower_bound_dep = -2*abs(dep_amor_growth_mean)
                higher_bound_dep = abs(dep_amor_growth_mean)/2  

            else:
                print('Write the correct spelling.')    


            selected_parameter_higher_bound = higher_bound_dep
            print('upper bound for Depreciation:',np.round(selected_parameter_higher_bound*100,2),'%')
        
            selected_parameter_lower_bound = lower_bound_dep
            print('lower bound for Depreciation:', np.round(selected_parameter_lower_bound*100,2), '%')

            choicechoice_dep = input('Above are assumptions taken for projecting Depreciation, if you want to change the assumptions, type CHANGE, else type YES.')
            choicechoice_dep = choicechoice_dep.upper()

            if choicechoice_dep == 'CHANGE':

                shg = float(input('Higher Bound for Depreciation Growth in (%): '))
                selected_parameter_higher_bound = shg/100
                print('upper bound for Depreciation Growth:',selected_parameter_higher_bound*100,'%')
                lhg = float(input('Lower Bound for Depreciation Growth in (%): '))
                selected_parameter_lower_bound = lhg/100
                print('lower bound for Depreciation Growth:', selected_parameter_lower_bound*100, '%')

                random_dep_growthpct = []
                
                for i in range(simulations):
                    random_dep_X = []
                    
                    for i in range(projected_years):
                        random_dep = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_dep_X.append(random_dep)
                    random_dep_growthpct.append(random_dep_X)

                table_for_dep_rev_rate = pd.concat([pd.DataFrame([random_dep_growthpct[i]]) 
                                                            for i in range(len(random_dep_growthpct))],
                                                            ignore_index=True)


                first_dep_projection = dep_amor[0]*(1+table_for_dep_rev_rate[0])   
                second_dep_projection = first_dep_projection*(1+table_for_dep_rev_rate[1])
                third_dep_projection = second_dep_projection*(1+table_for_dep_rev_rate[2])
                fourth_dep_projection = third_dep_projection*(1+table_for_dep_rev_rate[3])
                fifth_dep_projection = fourth_dep_projection*(1+table_for_dep_rev_rate[4])
                sixth_dep_projection = fifth_dep_projection*(1+table_for_dep_rev_rate[5])

                projected_dep = pd.DataFrame({
                    
                    'First Year Projection': first_dep_projection,
                    'Second Year Projection': second_dep_projection,
                    'Third Year Projection': third_dep_projection,
                    'Fourth Year Projection': fourth_dep_projection,
                    'Fifth Year Projection': fifth_dep_projection,
                    'Sixth Year Projection': sixth_dep_projection})

            else:

                random_dep_growthpct = []
                
                for i in range(simulations):
                    random_dep_X = []
                    
                    for i in range(projected_years):
                        random_dep = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_dep_X.append(random_dep)
                    random_dep_growthpct.append(random_dep_X)

                table_for_dep_rev_rate = pd.concat([pd.DataFrame([random_dep_growthpct[i]]) 
                                                            for i in range(len(random_dep_growthpct))],
                                                            ignore_index=True)


                first_dep_projection = dep_amor[0]*(1+table_for_dep_rev_rate[0])   
                second_dep_projection = first_dep_projection*(1+table_for_dep_rev_rate[1])
                third_dep_projection = second_dep_projection*(1+table_for_dep_rev_rate[2])
                fourth_dep_projection = third_dep_projection*(1+table_for_dep_rev_rate[3])
                fifth_dep_projection = fourth_dep_projection*(1+table_for_dep_rev_rate[4])
                sixth_dep_projection = fifth_dep_projection*(1+table_for_dep_rev_rate[5])

                projected_dep = pd.DataFrame({
                    
                    'First Year Projection': first_dep_projection,
                    'Second Year Projection': second_dep_projection,
                    'Third Year Projection': third_dep_projection,
                    'Fourth Year Projection': fourth_dep_projection,
                    'Fifth Year Projection': fifth_dep_projection,
                    'Sixth Year Projection': sixth_dep_projection

                })

                if yn == 'x':
                    print('') 
                
                else:
                    
                    dep_yes = input('Do you want to see Depreciation Monte Carlo Table?, type YES, else NO:')   
                    dep_yes = dep_yes.upper()

                    if dep_yes == 'YES':
                    
                        print('Depreciation Monte Carlo Simulations')
                        print(projected_dep)    
                
                
                if yn == 'x':
                    print('') 
                
                else:
                    
                    dep_yes = input('Do you want to see Depreciation Monte Carlo Table?, type YES, else NO:')   
                    dep_yes = dep_yes.upper()

                    if dep_yes == 'YES':
                    
                        print('Depreciation Monte Carlo Simulations')
                        print(projected_dep)


    if choice_dep == 'C':

        projected_dep = linalg(known_years, dep_amor, forecasting_years)   

        print('Depreciation Forecasted by Linear Regression:') 
        print(projected_dep)   

elif chooice_dep_11 == 'SAME': 

    print('Continuing with', choice, 'method')
    
    if choice == 'Monte Carlo':

        print('Average Depreciation Growth =', np.round((dep_amor_growth_mean)*100,2), '%')
        dep_simulations = simulations
        print('Simulations =', simulations)
        print('Projected Years =', projected_years)

        if query_1 == 'CUSTOM':

            print('For this section you can refer average growth rate printed above.')
            
            shg = float(input('Higher Bound for Depreciation Growth in (%): '))
            selected_parameter_higher_bound = shg/100
            print('upper bound for Depreciation Growth:',selected_parameter_higher_bound*100,'%')
            lhg = float(input('Lower Bound for Depreciation Growth in (%): '))
            selected_parameter_lower_bound = lhg/100
            print('lower bound for Depreciation Growth:', selected_parameter_lower_bound*100, '%')

            random_dep_growthpct = []
            
            for i in range(simulations):
                random_dep_X = []
                
                for i in range(projected_years):
                    random_dep = np.random.randint(selected_parameter_lower_bound*1000000,
                                                        selected_parameter_higher_bound*1000000)/1000000
                    random_dep_X.append(random_dep)
                random_dep_growthpct.append(random_dep_X)

            table_for_dep_rev_rate = pd.concat([pd.DataFrame([random_dep_growthpct[i]]) 
                                                        for i in range(len(random_dep_growthpct))],
                                                        ignore_index=True)


            first_dep_projection = dep_amor[0]*(1+table_for_dep_rev_rate[0])   
            second_dep_projection = first_dep_projection*(1+table_for_dep_rev_rate[1])
            third_dep_projection = second_dep_projection*(1+table_for_dep_rev_rate[2])
            fourth_dep_projection = third_dep_projection*(1+table_for_dep_rev_rate[3])
            fifth_dep_projection = fourth_dep_projection*(1+table_for_dep_rev_rate[4])
            sixth_dep_projection = fifth_dep_projection*(1+table_for_dep_rev_rate[5])

            projected_dep = pd.DataFrame({
                
                'First Year Projection': first_dep_projection,
                'Second Year Projection': second_dep_projection,
                'Third Year Projection': third_dep_projection,
                'Fourth Year Projection': fourth_dep_projection,
                'Fifth Year Projection': fifth_dep_projection,
                'Sixth Year Projection': sixth_dep_projection
            
            })               

            if yn == 'x':
                print('') 
            
            else:
                
                dep_yes = input('Do you want to see Depreciation Monte Carlo Table?, type YES, else NO:')   
                dep_yes = dep_yes.upper()

                if dep_yes == 'YES':
                
                    print('Depreciation Monte Carlo Simulations')
                    print(projected_dep)
        
        if query_1 == 'BASIC':

            
            print('Taking Monte Carlo Assumption as', query_basic)
            
            if query_basic == 'BEST':

                lower_bound_dep = abs(dep_amor_growth_mean)/np.pi
                higher_bound_dep = np.pi*(abs(dep_amor_growth_mean))

            elif query_basic == 'NORMAL':

                lower_bound_dep = 0
                higher_bound_dep = abs(dep_amor_growth_mean)

            elif query_basic == 'WORST':

                lower_bound_dep = -2*abs(dep_amor_growth_mean)
                higher_bound_dep = abs(dep_amor_growth_mean)/2  

            else:
                print('Write the correct spelling.')    


            selected_parameter_higher_bound = higher_bound_dep
            print('upper bound for Depreciation:',np.round(selected_parameter_higher_bound*100,2),'%')
        
            selected_parameter_lower_bound = lower_bound_dep
            print('lower bound for Depreciation:', np.round(selected_parameter_lower_bound*100,2), '%')

            choicechoice_dep = input('Above are assumptions taken for projecting Depreciation, if you want to change the assumptions, type CHANGE, else type YES.')
            choicechoice_dep = choicechoice_dep.upper()

            if choicechoice_dep == 'CHANGE':

                shg = float(input('Higher Bound for Depreciation Growth in (%): '))
                selected_parameter_higher_bound = shg/100
                print('upper bound for Depreciation Growth:',selected_parameter_higher_bound*100,'%')
                lhg = float(input('Lower Bound for Depreciation Growth in (%): '))
                selected_parameter_lower_bound = lhg/100
                print('lower bound for Depreciation Growth:', selected_parameter_lower_bound*100, '%')

                random_dep_growthpct = []
                
                for i in range(simulations):
                    random_dep_X = []
                    
                    for i in range(projected_years):
                        random_dep = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_dep_X.append(random_dep)
                    random_dep_growthpct.append(random_dep_X)

                table_for_dep_rev_rate = pd.concat([pd.DataFrame([random_dep_growthpct[i]]) 
                                                            for i in range(len(random_dep_growthpct))],
                                                            ignore_index=True)


                first_dep_projection = dep_amor[0]*(1+table_for_dep_rev_rate[0])   
                second_dep_projection = first_dep_projection*(1+table_for_dep_rev_rate[1])
                third_dep_projection = second_dep_projection*(1+table_for_dep_rev_rate[2])
                fourth_dep_projection = third_dep_projection*(1+table_for_dep_rev_rate[3])
                fifth_dep_projection = fourth_dep_projection*(1+table_for_dep_rev_rate[4])
                sixth_dep_projection = fifth_dep_projection*(1+table_for_dep_rev_rate[5])

                projected_dep = pd.DataFrame({
                    
                    'First Year Projection': first_dep_projection,
                    'Second Year Projection': second_dep_projection,
                    'Third Year Projection': third_dep_projection,
                    'Fourth Year Projection': fourth_dep_projection,
                    'Fifth Year Projection': fifth_dep_projection,
                    'Sixth Year Projection': sixth_dep_projection})

            else:

                random_dep_growthpct = []
                
                for i in range(simulations):
                    random_dep_X = []
                    
                    for i in range(projected_years):
                        random_dep = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_dep_X.append(random_dep)
                    random_dep_growthpct.append(random_dep_X)

                table_for_dep_rev_rate = pd.concat([pd.DataFrame([random_dep_growthpct[i]]) 
                                                            for i in range(len(random_dep_growthpct))],
                                                            ignore_index=True)


                first_dep_projection = np.array(dep_amor)[0]*(1+table_for_dep_rev_rate[0])   
                second_dep_projection = first_dep_projection*(1+table_for_dep_rev_rate[1])
                third_dep_projection = second_dep_projection*(1+table_for_dep_rev_rate[2])
                fourth_dep_projection = third_dep_projection*(1+table_for_dep_rev_rate[3])
                fifth_dep_projection = fourth_dep_projection*(1+table_for_dep_rev_rate[4])
                sixth_dep_projection = fifth_dep_projection*(1+table_for_dep_rev_rate[5])

                projected_dep = pd.DataFrame({
                    
                    'First Year Projection': first_dep_projection,
                    'Second Year Projection': second_dep_projection,
                    'Third Year Projection': third_dep_projection,
                    'Fourth Year Projection': fourth_dep_projection,
                    'Fifth Year Projection': fifth_dep_projection,
                    'Sixth Year Projection': sixth_dep_projection

                })

                if yn == 'x':
                    print('') 
                
                else:
                    
                    dep_yes = input('Do you want to see Depreciation Monte Carlo Table?, type YES, else NO:')   
                    dep_yes = dep_yes.upper()

                    if dep_yes == 'YES':
                    
                        print('Depreciation Monte Carlo Simulations')
                        print(projected_dep)    
                
                
                if yn == 'x':
                    print('') 
                
                else:
                    
                    dep_yes = input('Do you want to see Depreciation Monte Carlo Table?, type YES, else NO:')   
                    dep_yes = dep_yes.upper()

                    if dep_yes == 'YES':
                    
                        print('Depreciation Monte Carlo Simulations')
                        print(projected_dep)

    
    elif choice == 'Linear Forecasting Model':

        projected_dep = linalg(known_years, dep_amor, forecasting_years)
        
        choice_dep = 'C'

        print('Depreciation Forecasted by Linear Regression:') 
        print(projected_dep)


## Projecting CapEx

print('We will now  bw forecasting Capex, if you want all your assumptions to be same as before, refer below.')  
print('Note that if you select SAMEDEP, the assumptions will be taken from Depreciation Forecast, if you want the assumptions to be same as Revenue projection, type SAMEREV.')

chooice_capex_11 = input('What Say?: ')
chooice_capex_11 = chooice_capex_11.upper()

capex_growth_mean = (cash_flow_table.loc['CapEx']/cash_flow_table.loc['CapEx'].shift(1) -1).mean()


if chooice_capex_11 == 'DIFF':

    print('We will now be forecasting cashflow component #3, Capex.')
    print('If you type A, then the forecasting of cashflow components will be done through Monte Carlo simulations with Custom modification.')
    print('If you type C, then forecasting will be done through Linear regression.')

    capex_growth_mean = (cash_flow_table.loc['CapEx']/cash_flow_table.loc['CapEx'].shift(1) -1).mean()

    choice_capex = input('Your choice to forecast CapEx and Amortisation is: ')
    choice_capex = choice_capex.upper()

    if choice_capex == 'A':

        print('Average Capex Growth =', np.round((capex_growth_mean)*100,2), '%')
        capex_simulations = simulations
        print('Simulations =', simulations)
        print('Projected Years =', projected_years)

        print('Do you want to input the lower bounds and upper bounds OR go with basic theory of Monte Carlo Simulations?, you can change your choices in the next projections as well.')
        print('if Custom modification, Type CUSTOM')
        print('If you want to go with basic theory, Type BASIC')

        query_3 = input('Your Choice for Monte Carlo is: ')
        query_3 = query_3.upper()

        if query_3 == 'CUSTOM':

            print('For this section you can refer average growth rate printed above.')
            
            shg = float(input('Higher Bound for Capex Growth in (%): '))
            selected_parameter_higher_bound = shg/100
            print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
            lhg = float(input('Lower Bound for Capex Growth in (%): '))
            selected_parameter_lower_bound = lhg/100
            print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

            random_capex_growthpct = []
            
            for i in range(simulations):
                random_capex_X = []
                
                for i in range(projected_years):
                    random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                        selected_parameter_higher_bound*1000000)/1000000
                    random_capex_X.append(random_capex)
                random_capex_growthpct.append(random_capex_X)

            table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                        for i in range(len(random_capex_growthpct))],
                                                        ignore_index=True)

            first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
            second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
            third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
            fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
            fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
            sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

            projected_capex = pd.DataFrame({
                
                'First Year Projection': first_capex_projection,
                'Second Year Projection': second_capex_projection,
                'Third Year Projection': third_capex_projection,
                'Fourth Year Projection': fourth_capex_projection,
                'Fifth Year Projection': fifth_capex_projection,
                'Sixth Year Projection': sixth_capex_projection
            
            })     

            if yn == 'x':
                print('') 
            
            else:
                
                capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                capex_yes = capex_yes.upper()

                if capex_yes == 'YES':
                
                    print('CapEx Monte Carlo Simulations')
                    print(projected_capex)

        if query_3 == 'BASIC':

            print('What assumption do you want to make?')
            print('1) Best Case Scenario (type BEST)')
            print('2) Normal Case Scenario (type NORMAL)')
            print('3) Worst Case Scenario (type WORST)')
            
            query_basic_capex = input('Your assumtion: ')
            query_basic_capex = query_basic_capex.upper()

            
            if query_basic_capex == 'BEST':

                lower_bound_capex = abs(capex_growth_mean)/3.14
                higher_bound_capex = (np.pi)*abs(capex_growth_mean) 

            elif query_basic_capex == 'NORMAL':

                lower_bound_capex = 0
                higher_bound_capex = abs(capex_growth_mean)

            elif query_basic_capex == 'WORST':

                lower_bound_capex = -2*abs(capex_growth_mean)
                higher_bound_capex = abs(capex_growth_mean)/2  

            else:
                print('Write the correct spelling, village person.')    


            selected_parameter_higher_bound = higher_bound_capex
            print('upper bound for CapEx:',np.round(selected_parameter_higher_bound*100,2),'%')
        
            selected_parameter_lower_bound = lower_bound_capex
            print('lower bound for CapEx:', np.round(selected_parameter_lower_bound*100,2), '%')

            choicehoice_capexpex = input('Above are assumptions for projecting CapEx, if you want to change the the assumptions, type CHANGE, else type YES: ')
            choicehoice_capexpex = choicehoice_capexpex.upper()

            if choicehoice_capexpex == 'CHANGE':

                shg = float(input('Higher Bound for Capex Growth in (%): '))
                selected_parameter_higher_bound = shg/100
                print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
                lhg = float(input('Lower Bound for Capex Growth in (%): '))
                selected_parameter_lower_bound = lhg/100
                print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

                random_capex_growthpct = []
                
                for i in range(simulations):
                    random_capex_X = []
                    
                    for i in range(projected_years):
                        random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_capex_X.append(random_capex)
                    random_capex_growthpct.append(random_capex_X)

                table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                            for i in range(len(random_capex_growthpct))],
                                                            ignore_index=True)


                first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                projected_capex = pd.DataFrame({
                    
                    'First Year Projection': first_capex_projection,
                    'Second Year Projection': second_capex_projection,
                    'Third Year Projection': third_capex_projection,
                    'Fourth Year Projection': fourth_capex_projection,
                    'Fifth Year Projection': fifth_capex_projection,
                    'Sixth Year Projection': sixth_capex_projection

                })

                if yn == 'x':
                    print('') 
                
                else:
                    
                    capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                    capex_yes = capex_yes.upper()

                    if capex_yes == 'YES':
                    
                        print('CapEx Monte Carlo Simulations')
                        print(projected_capex)

            else:

                random_capex_growthpct = []
                
                for i in range(simulations):
                    random_capex_X = []
                    
                    for i in range(projected_years):
                        random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_capex_X.append(random_capex)
                    random_capex_growthpct.append(random_capex_X)

                table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                            for i in range(len(random_capex_growthpct))],
                                                            ignore_index=True)


                first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                projected_capex = pd.DataFrame({
                    
                    'First Year Projection': first_capex_projection,
                    'Second Year Projection': second_capex_projection,
                    'Third Year Projection': third_capex_projection,
                    'Fourth Year Projection': fourth_capex_projection,
                    'Fifth Year Projection': fifth_capex_projection,
                    'Sixth Year Projection': sixth_capex_projection

                })

                if yn == 'x':
                    print('') 
                
                else:
                    
                    capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                    capex_yes = capex_yes.upper()

                    if capex_yes == 'YES':
                    
                        print('CapEx Monte Carlo Simulations')
                        print(projected_capex)


    if choice_capex == 'C': 
        
        projected_capex = linalg(known_years, capex, forecasting_years)   

        print('CapEx Forecasted by Linear Regression:') 
        print(projected_capex)


elif chooice_capex_11 == 'SAMEDEP':

    if chooice_dep_11 == 'SAME':

        if choice == 'Monte Carlo':

        
            print('We will now be forecasting cashflow component #3, Capex.')
            print('Continuing with', choice, 'method')

            print('Average Capex Growth =', np.round((capex_growth_mean)*100,2), '%')
            capex_simulations = simulations
            print('Simulations =', simulations)
            print('Projected Years =', projected_years)

            if query_1 == 'CUSTOM':

                print('For this section you can refer average growth rate printed above.')
                
                shg = float(input('Higher Bound for Capex Growth in (%): '))
                selected_parameter_higher_bound = shg/100
                print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
                lhg = float(input('Lower Bound for Capex Growth in (%): '))
                selected_parameter_lower_bound = lhg/100
                print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

                random_capex_growthpct = []
                
                for i in range(simulations):
                    random_capex_X = []
                    
                    for i in range(projected_years):
                        random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_capex_X.append(random_capex)
                    random_capex_growthpct.append(random_capex_X)

                table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                            for i in range(len(random_capex_growthpct))],
                                                            ignore_index=True)

                first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                projected_capex = pd.DataFrame({
                    
                    'First Year Projection': first_capex_projection,
                    'Second Year Projection': second_capex_projection,
                    'Third Year Projection': third_capex_projection,
                    'Fourth Year Projection': fourth_capex_projection,
                    'Fifth Year Projection': fifth_capex_projection,
                    'Sixth Year Projection': sixth_capex_projection
                
                })     

                if yn == 'x':
                    print('') 
                
                else:
                    
                    capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                    capex_yes = capex_yes.upper()

                    if capex_yes == 'YES':
                    
                        print('CapEx Monte Carlo Simulations')
                        print(projected_capex)

            if query_1 == 'BASIC':
                
                print('Going with Monte Carlo', query_basic, 'assumption.')
                
                if query_basic == 'BEST':

                    lower_bound_capex = abs(capex_growth_mean)/3.14
                    higher_bound_capex = (np.pi)*abs(capex_growth_mean) 

                elif query_basic == 'NORMAL':

                    lower_bound_capex = 0
                    higher_bound_capex = abs(capex_growth_mean)

                elif query_basic == 'WORST':

                    lower_bound_capex = -2*abs(capex_growth_mean)
                    higher_bound_capex = abs(capex_growth_mean)/2  

                else:
                    print('Write the correct spelling, village person.')    


                selected_parameter_higher_bound = higher_bound_capex
                print('upper bound for CapEx:',np.round(selected_parameter_higher_bound*100,2),'%')
            
                selected_parameter_lower_bound = lower_bound_capex
                print('lower bound for CapEx:', np.round(selected_parameter_lower_bound*100,2), '%')

                choicehoice_capexpex = input('Above are assumptions for projecting CapEx, if you want to change the the assumptions, type CHANGE, else type YES: ')
                choicehoice_capexpex = choicehoice_capexpex.upper()

                if choicehoice_capexpex == 'CHANGE':

                    shg = float(input('Higher Bound for Capex Growth in (%): '))
                    selected_parameter_higher_bound = shg/100
                    print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
                    lhg = float(input('Lower Bound for Capex Growth in (%): '))
                    selected_parameter_lower_bound = lhg/100
                    print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

                    random_capex_growthpct = []
                    
                    for i in range(simulations):
                        random_capex_X = []
                        
                        for i in range(projected_years):
                            random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                                selected_parameter_higher_bound*1000000)/1000000
                            random_capex_X.append(random_capex)
                        random_capex_growthpct.append(random_capex_X)

                    table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                                for i in range(len(random_capex_growthpct))],
                                                                ignore_index=True)


                    first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                    second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                    third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                    fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                    fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                    sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                    projected_capex = pd.DataFrame({
                        
                        'First Year Projection': first_capex_projection,
                        'Second Year Projection': second_capex_projection,
                        'Third Year Projection': third_capex_projection,
                        'Fourth Year Projection': fourth_capex_projection,
                        'Fifth Year Projection': fifth_capex_projection,
                        'Sixth Year Projection': sixth_capex_projection

                    })

                    if yn == 'x':
                        print('') 
                    
                    else:
                        
                        capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                        capex_yes = capex_yes.upper()

                        if capex_yes == 'YES':
                        
                            print('CapEx Monte Carlo Simulations')
                            print(projected_capex)

                else:

                    random_capex_growthpct = []
                    
                    for i in range(simulations):
                        random_capex_X = []
                        
                        for i in range(projected_years):
                            random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                                selected_parameter_higher_bound*1000000)/1000000
                            random_capex_X.append(random_capex)
                        random_capex_growthpct.append(random_capex_X)

                    table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                                for i in range(len(random_capex_growthpct))],
                                                                ignore_index=True)


                    first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                    second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                    third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                    fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                    fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                    sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                    projected_capex = pd.DataFrame({
                        
                        'First Year Projection': first_capex_projection,
                        'Second Year Projection': second_capex_projection,
                        'Third Year Projection': third_capex_projection,
                        'Fourth Year Projection': fourth_capex_projection,
                        'Fifth Year Projection': fifth_capex_projection,
                        'Sixth Year Projection': sixth_capex_projection

                    })

                    if yn == 'x':
                        print('') 
                    
                    else:
                        
                        capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                        capex_yes = capex_yes.upper()

                        if capex_yes == 'YES':
                        
                            print('CapEx Monte Carlo Simulations')
                            print(projected_capex)

        elif choice == 'Linear Forecasting Model':

            projected_capex = linalg(known_years, capex, forecasting_years)   
            choice_capex = 'C'

            print('CapEx Forecasted by Linear Regression:') 
            print(projected_capex)

            
    else:

        print('We will now be forecasting cashflow component #3, Capex.')
        print('Continuing with', choice_dep, 'method')

        print('Average Capex Growth =', np.round((capex_growth_mean)*100,2), '%')
        capex_simulations = simulations
        print('Simulations =', simulations)
        print('Projected Years =', projected_years)

        if query_2 == 'CUSTOM':

            print('For this section you can refer average growth rate printed above.')
            
            shg = float(input('Higher Bound for Capex Growth in (%): '))
            selected_parameter_higher_bound = shg/100
            print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
            lhg = float(input('Lower Bound for Capex Growth in (%): '))
            selected_parameter_lower_bound = lhg/100
            print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

            random_capex_growthpct = []
            
            for i in range(simulations):
                random_capex_X = []
                
                for i in range(projected_years):
                    random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                        selected_parameter_higher_bound*1000000)/1000000
                    random_capex_X.append(random_capex)
                random_capex_growthpct.append(random_capex_X)

            table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                        for i in range(len(random_capex_growthpct))],
                                                        ignore_index=True)

            first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
            second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
            third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
            fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
            fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
            sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

            projected_capex = pd.DataFrame({
                
                'First Year Projection': first_capex_projection,
                'Second Year Projection': second_capex_projection,
                'Third Year Projection': third_capex_projection,
                'Fourth Year Projection': fourth_capex_projection,
                'Fifth Year Projection': fifth_capex_projection,
                'Sixth Year Projection': sixth_capex_projection
            
            })     

            if yn == 'x':
                print('') 
            
            else:
                
                capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                capex_yes = capex_yes.upper()

                if capex_yes == 'YES':
                
                    print('CapEx Monte Carlo Simulations')
                    print(projected_capex)

        if query_2 == 'BASIC':
            
            print('Going with Monte Carlo', query_basic_dep, 'assumption.')
            
            if query_basic_dep == 'BEST':

                lower_bound_capex = abs(capex_growth_mean)/3.14
                higher_bound_capex = (np.pi)*abs(capex_growth_mean) 

            elif query_basic_dep == 'NORMAL':

                lower_bound_capex = 0
                higher_bound_capex = abs(capex_growth_mean)

            elif query_basic_dep == 'WORST':

                lower_bound_capex = -2*abs(capex_growth_mean)
                higher_bound_capex = abs(capex_growth_mean)/2  

            else:
                print('Write the correct spelling, village person.')    


            selected_parameter_higher_bound = higher_bound_capex
            print('upper bound for CapEx:',np.round(selected_parameter_higher_bound*100,2),'%')
        
            selected_parameter_lower_bound = lower_bound_capex
            print('lower bound for CapEx:', np.round(selected_parameter_lower_bound*100,2), '%')

            choicehoice_capexpex = input('Above are assumptions for projecting CapEx, if you want to change the the assumptions, type CHANGE, else type YES: ')
            choicehoice_capexpex = choicehoice_capexpex.upper()

            if choicehoice_capexpex == 'CHANGE':

                shg = float(input('Higher Bound for Capex Growth in (%): '))
                selected_parameter_higher_bound = shg/100
                print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
                lhg = float(input('Lower Bound for Capex Growth in (%): '))
                selected_parameter_lower_bound = lhg/100
                print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

                random_capex_growthpct = []
                
                for i in range(simulations):
                    random_capex_X = []
                    
                    for i in range(projected_years):
                        random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_capex_X.append(random_capex)
                    random_capex_growthpct.append(random_capex_X)

                table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                            for i in range(len(random_capex_growthpct))],
                                                            ignore_index=True)


                first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                projected_capex = pd.DataFrame({
                    
                    'First Year Projection': first_capex_projection,
                    'Second Year Projection': second_capex_projection,
                    'Third Year Projection': third_capex_projection,
                    'Fourth Year Projection': fourth_capex_projection,
                    'Fifth Year Projection': fifth_capex_projection,
                    'Sixth Year Projection': sixth_capex_projection

                })

                if yn == 'x':
                    print('') 
                
                else:
                    
                    capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                    capex_yes = capex_yes.upper()

                    if capex_yes == 'YES':
                    
                        print('CapEx Monte Carlo Simulations')
                        print(projected_capex)

            else:

                random_capex_growthpct = []
                
                for i in range(simulations):
                    random_capex_X = []
                    
                    for i in range(projected_years):
                        random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_capex_X.append(random_capex)
                    random_capex_growthpct.append(random_capex_X)

                table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                            for i in range(len(random_capex_growthpct))],
                                                            ignore_index=True)


                first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                projected_capex = pd.DataFrame({
                    
                    'First Year Projection': first_capex_projection,
                    'Second Year Projection': second_capex_projection,
                    'Third Year Projection': third_capex_projection,
                    'Fourth Year Projection': fourth_capex_projection,
                    'Fifth Year Projection': fifth_capex_projection,
                    'Sixth Year Projection': sixth_capex_projection

                })

                if yn == 'x':
                    print('') 
                
                else:
                    
                    capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                    capex_yes = capex_yes.upper()

                    if capex_yes == 'YES':
                    
                        print('CapEx Monte Carlo Simulations')
                        print(projected_capex)


elif chooice_capex_11 == 'SAMEREV':

    if choice == 'Monte Carlo':

        
            print('We will now be forecasting cashflow component #3, Capex.')
            print('Continuing with', choice, 'method')

            print('Average Capex Growth =', np.round((capex_growth_mean)*100,2), '%')
            capex_simulations = simulations
            print('Simulations =', simulations)
            print('Projected Years =', projected_years)

            if query_1 == 'CUSTOM':

                print('For this section you can refer average growth rate printed above.')
                
                shg = float(input('Higher Bound for Capex Growth in (%): '))
                selected_parameter_higher_bound = shg/100
                print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
                lhg = float(input('Lower Bound for Capex Growth in (%): '))
                selected_parameter_lower_bound = lhg/100
                print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

                random_capex_growthpct = []
                
                for i in range(simulations):
                    random_capex_X = []
                    
                    for i in range(projected_years):
                        random_capex = np.random.randint(selected_parameter_lower_bound*1000000,

                                                            selected_parameter_higher_bound*1000000)/1000000
                        random_capex_X.append(random_capex)
                    random_capex_growthpct.append(random_capex_X)

                table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                            for i in range(len(random_capex_growthpct))],
                                                            ignore_index=True)

                first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                projected_capex = pd.DataFrame({
                    
                    'First Year Projection': first_capex_projection,
                    'Second Year Projection': second_capex_projection,
                    'Third Year Projection': third_capex_projection,
                    'Fourth Year Projection': fourth_capex_projection,
                    'Fifth Year Projection': fifth_capex_projection,
                    'Sixth Year Projection': sixth_capex_projection
                
                })     

                if yn == 'x':
                    print('') 
                
                else:
                    
                    capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                    capex_yes = capex_yes.upper()

                    if capex_yes == 'YES':
                    
                        print('CapEx Monte Carlo Simulations')
                        print(projected_capex)

            if query_1 == 'BASIC':
                
                print('Going with Monte Carlo', query_basic, 'assumption.')
                
                if query_basic == 'BEST':

                    lower_bound_capex = abs(capex_growth_mean)/3.14
                    higher_bound_capex = (np.pi)*abs(capex_growth_mean) 

                elif query_basic == 'NORMAL':

                    lower_bound_capex = 0
                    higher_bound_capex = abs(capex_growth_mean)

                elif query_basic == 'WORST':

                    lower_bound_capex = -2*abs(capex_growth_mean)
                    higher_bound_capex = abs(capex_growth_mean)/2  

                else:
                    print('Write the correct spelling, village person.')    


                selected_parameter_higher_bound = higher_bound_capex
                print('upper bound for CapEx:',np.round(selected_parameter_higher_bound*100,2),'%')
            
                selected_parameter_lower_bound = lower_bound_capex
                print('lower bound for CapEx:', np.round(selected_parameter_lower_bound*100,2), '%')

                choicehoice_capexpex = input('Above are assumptions for projecting CapEx, if you want to change the the assumptions, type CHANGE, else type YES: ')
                choicehoice_capexpex = choicehoice_capexpex.upper()

                if choicehoice_capexpex == 'CHANGE':

                    shg = float(input('Higher Bound for Capex Growth in (%): '))
                    selected_parameter_higher_bound = shg/100
                    print('upper bound for Capex Growth:',selected_parameter_higher_bound*100,'%')
                    lhg = float(input('Lower Bound for Capex Growth in (%): '))
                    selected_parameter_lower_bound = lhg/100
                    print('lower bound for Capex Growth:', selected_parameter_lower_bound*100, '%')

                    random_capex_growthpct = []
                    
                    for i in range(simulations):
                        random_capex_X = []
                        
                        for i in range(projected_years):
                            random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                                selected_parameter_higher_bound*1000000)/1000000
                            random_capex_X.append(random_capex)
                        random_capex_growthpct.append(random_capex_X)

                    table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                                for i in range(len(random_capex_growthpct))],
                                                                ignore_index=True)


                    first_capex_projection = capex[0]*(1+table_for_capex_rev_rate[0])   
                    second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                    third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                    fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                    fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                    sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                    projected_capex = pd.DataFrame({
                        
                        'First Year Projection': first_capex_projection,
                        'Second Year Projection': second_capex_projection,
                        'Third Year Projection': third_capex_projection,
                        'Fourth Year Projection': fourth_capex_projection,
                        'Fifth Year Projection': fifth_capex_projection,
                        'Sixth Year Projection': sixth_capex_projection

                    })

                    if yn == 'x':
                        print('') 
                    
                
                else:
                        
                    random_capex_growthpct = []
                    
                    for i in range(simulations):
                        random_capex_X = []
                        
                        for i in range(projected_years):
                            random_capex = np.random.randint(selected_parameter_lower_bound*1000000,
                                                                selected_parameter_higher_bound*1000000)/1000000
                            random_capex_X.append(random_capex)
                        random_capex_growthpct.append(random_capex_X)

                    table_for_capex_rev_rate = pd.concat([pd.DataFrame([random_capex_growthpct[i]]) 
                                                                for i in range(len(random_capex_growthpct))],
                                                                ignore_index=True)


                    first_capex_projection = np.array(capex)[0]*(1+table_for_capex_rev_rate[0])   
                    second_capex_projection = first_capex_projection*(1+table_for_capex_rev_rate[1])
                    third_capex_projection = second_capex_projection*(1+table_for_capex_rev_rate[2])
                    fourth_capex_projection = third_capex_projection*(1+table_for_capex_rev_rate[3])
                    fifth_capex_projection = fourth_capex_projection*(1+table_for_capex_rev_rate[4])
                    sixth_capex_projection = fifth_capex_projection*(1+table_for_capex_rev_rate[5])

                    projected_capex = pd.DataFrame({
                        
                        'First Year Projection': first_capex_projection,
                        'Second Year Projection': second_capex_projection,
                        'Third Year Projection': third_capex_projection,
                        'Fourth Year Projection': fourth_capex_projection,
                        'Fifth Year Projection': fifth_capex_projection,
                        'Sixth Year Projection': sixth_capex_projection

                    })

                    
                    capex_yes = input('Do you want to see CapEx Monte Carlo Table?, type YES, else NO:')   
                    capex_yes = capex_yes.upper()

                    if capex_yes == 'YES':
                    
                        print('CapEx Monte Carlo Simulations')
                        print(projected_capex)

    
    elif choice == 'Linear Forecasting Model':

            projected_capex = linalg(known_years, capex, forecasting_years)   
            choice_capex = 'C'

            print('CapEx Forecasted by Linear Regression:') 
            print(projected_capex)


## Change in NWC

print('Now, we will forecast Non-Cash Working Capital (NWC)')
print('Ideal range is -5% to 5% ' + ' for growth rate of Non-Cash Working Capital.')
print('If you want to project NWC with Linear Regression, Type LINALG.')
print('If you want to grow NWC at a contant rate, type CONST')


choice_nwc = input('Your Choice:')
choice_nwc = choice_nwc.upper()


if choice_nwc == 'LINALG':

    projected_nwc = linalg(known_years[1:4], change_in_nwc[:-1], forecasting_years)

elif choice_nwc == 'CONST':

    selected_parameter_higher_bound = float(input('NWC Growth Rate: '))/100
    selected_parameter_lower_bound = (selected_parameter_higher_bound - 0.01)

    random_nwc_growthpct = []
    
    for i in range(simulations):
        random_nwc_X = []
        
        for i in range(projected_years):
            random_nwc = np.random.randint(selected_parameter_lower_bound*1000000,
                                                selected_parameter_higher_bound*1000000)/1000000
            random_nwc_X.append(random_nwc)
        random_nwc_growthpct.append(random_nwc_X)

    table_for_nwc_rev_rate = pd.concat([pd.DataFrame([random_nwc_growthpct[i]]) 
                                                for i in range(len(random_nwc_growthpct))],
                                                ignore_index=True)


    first_nwc_projection = change_in_nwc[0]*(1+table_for_nwc_rev_rate[0])   
    second_nwc_projection = first_nwc_projection*(1+table_for_nwc_rev_rate[1])
    third_nwc_projection = second_nwc_projection*(1+table_for_nwc_rev_rate[2])
    fourth_nwc_projection = third_nwc_projection*(1+table_for_nwc_rev_rate[3])
    fifth_nwc_projection = fourth_nwc_projection*(1+table_for_nwc_rev_rate[4])
    sixth_nwc_projection = fifth_nwc_projection*(1+table_for_nwc_rev_rate[5])

    projected_nwc = pd.DataFrame({
        
        'First Year Projection': first_nwc_projection,
        'Second Year Projection': second_nwc_projection,
        'Third Year Projection': third_nwc_projection,
        'Fourth Year Projection': fourth_nwc_projection,
        'Fifth Year Projection': fifth_nwc_projection,
        'Sixth Year Projection': sixth_nwc_projection

    })

## Future CashFlow

if choice == 'Linear Forecasting Model' and choice_dep == 'C' and choice_capex == 'C' and choice_nwc == 'LINALG':

    print('ALL ARE PROJECTED THROUGH LINEAR REGRESSION.')

    future_cash_flows = NOPAT + projected_capex + projected_dep - projected_nwc

    pv_fcf_1 = (future_cash_flows[0])/(1+wacc)**1
    pv_fcf_2 = (future_cash_flows[1])/(1+wacc)**2
    pv_fcf_3 = (future_cash_flows[2])/(1+wacc)**3
    pv_fcf_4 = (future_cash_flows[3])/(1+wacc)**4
    pv_fcf_5 = (future_cash_flows[4])/(1+wacc)**5
    pv_fcf_6 = (future_cash_flows[5])/(1+wacc)**6

    sum_fcf_pv = pv_fcf_1 + pv_fcf_2 + pv_fcf_3 + pv_fcf_4 + pv_fcf_5 +  pv_fcf_6
    terminal = future_cash_flows[5]*(1+growth_rate)/(wacc - growth_rate)
    pv_terminal = terminal/(1+wacc)**6
    enterprise = pv_terminal + sum_fcf_pv
    total_cash = info['totalCash']
    total_debt = info['totalDebt']
    shares_outstanding = info['sharesOutstanding']
    minority_interest = financials.loc['Net Income From Continuing Operation Net Minority Interest'].fillna(0)[0]
    equity_value = enterprise + total_cash - total_debt - minority_interest
    implied_stock_price = equity_value/shares_outstanding
    print(implied_stock_price)

    ## Creating Sensitivity Table

    growth_rates  =   [growth_rate - 3/100,growth_rate - 2/100, growth_rate-1/100,growth_rate, growth_rate+1/100, growth_rate +2 /100, growth_rate+3/100]

    wacc_rates = [wacc - 3/100, wacc - 2/100, wacc - 1/100, wacc, wacc+1/100, wacc + 2/100, wacc+3/100]

    implied_stock_price_sens = []

    if choice == 'Linear Forecasting Model' and choice_dep == 'C' and choice_capex == 'C' and choice_nwc == 'LINALG':
        
        for i in wacc_rates:

            for k in growth_rates:

                terminal = future_cash_flows[5]*(1+k)/(i-k)
                
                pv_terminal = terminal/(1+wacc)**6
                enterprise = pv_terminal + sum_fcf_pv
                total_cash = info['totalCash']
                total_debt = info['totalDebt']
                shares_outstanding = info['sharesOutstanding']
                minority_interest = financials.loc['Net Income From Continuing Operation Net Minority Interest'].fillna(0)[0]
                equity_value = enterprise + total_cash - total_debt - minority_interest
                
                implied_stock_price = equity_value/shares_outstanding
                implied_stock_price_sens.append(implied_stock_price)

                new_wacc_rates = []

        for i in wacc_rates:

            wacc_100 = np.round(i*100,3)
            new_wacc_rates.append(wacc_100)

        wacc_string = ','.join(str(x) for x in new_wacc_rates)

        df = pd.DataFrame({
        
            'WACC': growth_rates,
            wacc_string[0:5]   + '%': implied_stock_price_sens[0:len(growth_rates)],
            wacc_string[6:11]  + '%': implied_stock_price_sens[len(growth_rates):len(growth_rates)*2],
            wacc_string[12:17] + '%': implied_stock_price_sens[len(growth_rates)*2:len(growth_rates)*3],
            wacc_string[18:23] + '%': implied_stock_price_sens[len(growth_rates)*3:len(growth_rates)*4],
            wacc_string[24:29] + '%': implied_stock_price_sens[len(growth_rates)*4:len(growth_rates)*5],
            wacc_string[30:35] + '%': implied_stock_price_sens[len(growth_rates)*5:len(growth_rates)*6],
            wacc_string[36:41] + '%': implied_stock_price_sens[len(growth_rates)*6:len(growth_rates)*7]
        
        })

        df.set_index('WACC')
        df.index = ['G', 'R', 'O', 'W', 'T','H','%']

        df.style.format({'WACC': '{0:.2%}'})

        print(df)   

else:
    
    future_cash_flows = NOPAT + projected_capex + projected_dep - projected_nwc

    pv_fcf_1 = future_cash_flows['First Year Projection']/((1+wacc)**1)
    pv_fcf_2 = future_cash_flows['Second Year Projection']/((1+wacc)**2)
    pv_fcf_3 = future_cash_flows['Third Year Projection']/((1+wacc)**3)
    pv_fcf_4 = future_cash_flows['Fourth Year Projection']/((1+wacc)**4)
    pv_fcf_5 = future_cash_flows['Fifth Year Projection']/((1+wacc)**5)
    pv_fcf_6 = future_cash_flows['Sixth Year Projection']/((1+wacc)**6)

    sum_fcf_pv = pv_fcf_1 + pv_fcf_2 + pv_fcf_3 + pv_fcf_4 + pv_fcf_5 + pv_fcf_6

    future_cash_flows['Sum of PV of FCF'] = sum_fcf_pv    

    print('WACC =', np.round(wacc*100,2), '%')
    print('Input the Growth rate of the economy in which the company is registered, Growth rate can not be more than WACC.')

    if growth_rate > wacc:
        print('Growth Rate is larger than WACC, the value of company will be negative, DCF ABORTED.')

    
    terminal = future_cash_flows['Sixth Year Projection'] * (1+growth_rate)/(wacc - growth_rate)
    pv_terminal = terminal/((1+wacc)**6)
    enterprise = pv_terminal + sum_fcf_pv
    total_cash = info['totalCash']
    total_debt = info['totalDebt']
    shares_outstanding = info['sharesOutstanding']
    minority_interest = financials.loc['Net Income From Continuing Operation Net Minority Interest'].fillna(0).iloc[0]
    equity_value = enterprise + total_cash - total_debt - minority_interest
    implied_stock_price = equity_value/shares_outstanding
    print(implied_stock_price)    

    
    plot = px.histogram(implied_stock_price, title = 'Distribution of Stock Prices through simulations.')
    plot.write_html('Stock_Price_Distribution.html', auto_open = True)

    ## Summary Table
    
    mean_implied = np.mean(implied_stock_price)
    stdev_implied = np.std(implied_stock_price)
    
    print('ACCORDING TO YOUR ASSUMPTIONS:')
   
    print('Average Projected Stock Price:', np.round(np.mean(implied_stock_price),2))
    print('Standard Deviation of projected Stock Price:', np.round(np.std(implied_stock_price),2))

    print('For 68% Probability, the stock value lies between')
    print('Lower Bound for 68%:', np.round((mean_implied - stdev_implied),2))
    print('Higher Bound for 68%:', np.round((mean_implied + stdev_implied),2))

    print('For 95% Probability, the stock value lies between')
    print('Lower bound for 95%:', np.round((mean_implied - 1.96*stdev_implied),2))
    print('Higher Bound for 95%:', np.round((mean_implied + 1.96*stdev_implied),2))
    
    
    summary_df = pd.DataFrame(
        
        {
            'Ticker Name': stock,
            'Benchmark Index': index,
            'Simulations': simulations,
            'Growth Rate(%)': growth_rate*100,
            'Corporate Tax Rate(%)': tax_rate*100,
            'Risk Free Rate(%)': risk_free,
            'Index 10Y Return(%)': np.round(index_return*100,2),
            'Stock 10Y Return(%)': np.round(stock_return*100,2),
            'Stock Beta': np.round(beta_stock,2),
            'Average Projected Price': np.round(np.mean(implied_stock_price),2),
            'Standard Deviation of projected Stock Price': np.round(np.std(implied_stock_price),2),
            'Lower Bound for 68%': np.round((mean_implied - stdev_implied),2),
            'Higher Bound for 68%': np.round((mean_implied + stdev_implied),2),
            'Lower bound for 95%': np.round((mean_implied - 1.96*stdev_implied),2),
            'Higher Bound for 95%':  np.round((mean_implied + 1.96*stdev_implied),2)


        }, index = ['Summary Table']
    )

    ## Normal Dist Test (SMIRNOV TEST)
    
    ## Giving Information about the Normal Distribution Test
    
    ## Creating Excel

    nopat_des = NOPAT.describe()
    dep_des = projected_dep.describe()
    capex_des = projected_capex.describe()

    def dfs_tables (df_list, sheet_list, file_name):
       
        writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
        for dataframe, sheet in zip (df_list, sheet_list):
            dataframe.to_excel(writer, sheet_name = sheet, startrow = 0, startcol = 0)
        
        writer._save()    
        
    dfs = [np.transpose(summary_df), cash_flow_table,df_specialised, wacc_table, nopat_des, NOPAT,dep_des, projected_dep,capex_des, projected_capex, implied_stock_price]
    sheets = ['Summary','CashFlow Table','Stock History','WACC','NOPAT SUMMARY',
              'NOPAT','DEP SUMMARY', 'DEP','CAPEX SUMMARY', 'CAPEX', 'STOCK PRICE']

    dfs_tables(dfs, sheets, (stock + ' DCF' + '.xlsx'))



print('DCF COMPLETED for', stock)