import os
import shutil
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def ABC(percentage):
    if percentage > 0 and percentage < 70:
        return 'A'
    elif percentage >= 70 and percentage < 90:
        return 'B'
    elif percentage >= 90:
        return 'C'

def prep(df):
    df['TotalC'] = df['Annual Demand'] * df['Unit price']
    Stotal = df['TotalC'].sum()
    df['DPercentage']=(1/len(df))*100
    df['CPercentage']=(df['TotalC']/Stotal)*100
    df = df.sort_values(by=['CPercentage'], ascending=False)
    df['CummulativeCP'] = df['CPercentage'].cumsum()
    df['CummulativeDP'] = df['DPercentage'].cumsum()
    df['Class']=df['CummulativeCP'].apply(ABC)
    return df,Stotal
    
    
def summary(df,Stotal):
    cls=['A','B','C']
    temp=[]
    for i in cls:
        temp.append(i)
        temp.append(df[df.Class == i]['TotalC'].sum())
        temp.append((df[df.Class == i]['TotalC'].sum()/Stotal)*100)
        temp.append(df.Class.value_counts()[i])
        temp.append(df.Class.value_counts()[i]/len(df)*100)
    return temp


def save(fig,title):
    fig.write_html('plots/'+title+'.html',
                    full_html=False,
                    include_plotlyjs='cdn')
    
def donut(summ):
    specs = [[{'type':'domain'}, {'type':'domain'}], [{'type':'domain'}, {'type':'domain'}]]
    fig = make_subplots(rows=2, cols=2, specs=specs)
    fig.add_trace(go.Pie(labels=summ.index, values=summ['Total Cost'], title='Total Cost'), 1, 1)
    fig.add_trace(go.Pie(labels=summ.index, values=summ['Cost Percentage'], title='Cost %'), 1, 2)
    fig.add_trace(go.Pie(labels=summ.index, values=summ['Frequency'], title='Frequency'), 2, 1)
    fig.add_trace(go.Pie(labels=summ.index, values=summ['Share Percentage'], title='Share %'), 2,2)
    fig.update_traces(hole=.75, hoverinfo="label+percent+name")
    fig = go.Figure(fig)
    fig.update_layout(title_text='Donut Plot')
    save(fig,'Donut')
    
    
def run():
    try:
        os.makedirs('plots')
    except FileExistsError:
        pass
    shutil.copyfile('temp/result.html', 'plots/result.html')
    df=pd.read_csv('data/inventory.csv')
    agg = {'Item-code': 'first', 'Annual Demand': 'sum', 'Unit price': 'first'}
    df = df.groupby(df['Item-code']).aggregate(agg)
    df,Stotal=prep(df)
    data=np.array(summary(df,Stotal))
    summ = pd.DataFrame(np.array_split(data, 3),
                            columns=['Class','Total Cost','Cost Percentage','Frequency','Share Percentage'])
    tab = go.Figure(data=[go.Table(header=dict(values=list(summ.columns)),
                               cells=dict(values=[summ['Class'],summ['Total Cost'], summ['Cost Percentage'], summ['Frequency'], summ['Share Percentage']]))])             
    tab.update_layout(title_text='Summary')
    save(tab,'Table')
    summ.set_index(summ['Class'],inplace=True)
    summ.drop(['Class'],axis=1,inplace=True)
    pareto = px.line(df, x='CummulativeDP', y='CummulativeCP',color='Class', title='Pareto curve')
    save(pareto,'Pareto Curve')
    donut(summ)
    tab2 = go.Figure(data=[go.Table(header=dict(values=list(summ.index)),
                               cells=dict(values=[df.query('Class=="A"')['Item-code'],df.query('Class=="B"')['Item-code'],df.query('Class=="C"')['Item-code']]))])
    tab2.update_layout(title_text='Items')
    save(tab2,'Table2')
    
        
    
if __name__ == "__main__":
    run()

