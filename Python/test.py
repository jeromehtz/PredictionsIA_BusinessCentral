import pandas as pd
import os
currentPath = os.getcwd()
print(currentPath+"\items_sales_data.csv")
dfSales = pd.read_csv("items_sales_data.csv", sep=';')
dfCopy = dfSales.reset_index(drop=True)
def dupliquer_lignes(df):
    dfCopy = df.reset_index(drop=True)
    List = []
    for index, row in df.iterrows():
        print(row)
        j = 0
        row['id']=index
        List.append(row)
    return pd.DataFrame(List)

        
dfSalesCopy = dupliquer_lignes(dfSales)
print(dfSalesCopy)