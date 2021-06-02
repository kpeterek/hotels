def star_data_input(files:list,filename:str):
    plt.style.use('seaborn')
    plt.rcParams['lines.linewidth'] = 2
    plt.rcParams['lines.linestyle'] = '--'
    plt.style.context('dark_background')
    # path_list = PATH.split('\n')
    dodge_census = pd.read_pickle(r"C:\Users\KyleP\Box\YB Hotels\CBRE Hotels Pipeline Data\Dodge Data\census.pkl")
    cols = [0,1,2,3,5,6,7,8,12,13,14,15,17,18,19,20,24,25,26,27,29,30,31,32,34]
    
    star_df = pd.DataFrame()
    comp_set = pd.DataFrame()
    for path in files:
        try:
            date = pd.to_datetime(pd.read_excel(path,sheet_name='Glance',skiprows=4).iloc[0,1],
                                  infer_datetime_format=True)+MonthEnd(1)
            comps = pd.read_excel(path,sheet_name='Response',skiprows=21,usecols='C:L',header=0).dropna(axis=0,how = 'all').dropna(axis=1,how='all').dropna(subset=['Name'])
            star = pd.read_excel(path,sheet_name='Comp',skiprows=18,usecols='B:T',nrows=34,header=1,
                             index_col=0,parse_dates=True).T
            star.index = pd.date_range(end=date,periods = 18,freq='M')
            sub_prop = comps.iloc[0,0]
            star['STARID'] = sub_prop
            star_df = star_df.append(star).drop_duplicates().sort_index(ascending=True)
            comps['Subj_prop'] = sub_prop
            comp_set = comp_set.append(comps).drop_duplicates().sort_index(ascending=True)
        except:
            pass
                   
    star_df = star_df.append(star).drop_duplicates().sort_index(ascending=True)
    comp_set = comp_set.append(comps).drop_duplicates().sort_index(ascending=True)
    star_df = star_df.iloc[:,cols]
    # star_df['StarID'] = sub_prop
    # star_df.columns = ['RevPAR_my_prop','RevPAR_comp','ADR_my_prop','ADR_comp','OCC_my_prop','OCC_comp','StarID']
    star_df.iloc[:,4:6] = star_df.iloc[:,4:6]/100
    star_df.to_clipboard(header=False)
    star_df.columns = ['OCC_my_prop','OCC_comp','OCC_Index','OCC_Rank', 'OCC_per_chg_my_prop','OCC_per_chg_comp','OCC_per_chg_index','OCC_per_chg_rank','ADR_my_prop','ADR_comp','ADR_Index','ADR_Rank','ADR_per_chg_my_prop','ADR_per_chg_comp','ADR_per_chg_index','ADR_per_chg_rank','RevPAR_my_prop','RevPAR_comp','RevPAR_Index','RevPAR_Rank','RevPAR_per_chg_my_prop','RevPAR_per_chg_comp','RevPAR_per_chg_index','RevPAR_per_chg_rank','STARID']
    star_df.drop_duplicates(subset=['OCC_my_prop','ADR_my_prop','RevPAR_my_prop'],inplace=True)
    print(dodge_census[dodge_census.StarID == sub_prop].T.iloc[1,3:33])
    print(comp_set)
    with PdfPages(filename+'.pdf') as pdf:
        for star in star_df.STARID.unique():
            try:    
            # plt.rcParams(10,10)
                fig,(ax1,ax2,ax3) = plt.subplots(nrows=3,ncols=1,sharex=True)
                # plt.title()
                # fig.raise_window()
                # fig.titlesize('small')
                prop_name= comp_set[comp_set.Subj_prop == star].iloc[0,1]['Name'].item()
                # star_df[star_df.STARID == star].iloc[:,[0,1,8,9,16,17]].plot(title = dodge_census.Property[dodge_census.StarID ==  star].item() +' RevPAR, ADR, Occupancy', subplots=True)
                ax1.plot(star_df[star_df.STARID == star].iloc[:,[0]],color = '#006A4D', label='My Property')
                ax1.plot(star_df[star_df.STARID == star].iloc[:,[1]],color = '#EC008C', label = 'Comp Set')
                ax1.legend()
                ax1.set_title('Occupancy')
                ax2.plot(star_df[star_df.STARID == star].iloc[:,[8]],color = '#006A4D', label='My Property')
                ax2.plot(star_df[star_df.STARID == star].iloc[:,[9]],color = '#EC008C',label = 'Comp Set')
                ax2.legend()
                ax2.set_title('ADR')
                ax3.plot(star_df[star_df.STARID == star].iloc[:,[16]],color = '#006A4D', label='My Property')
                ax3.plot(star_df[star_df.STARID == star].iloc[:,[17]],color = '#EC008C',label = 'Comp Set')
                ax3.legend()
                ax3.set_title('RevPAR')
                # plt.plot(star_df[star_df.STARID == star].iloc[:,[0,1]],label='Occupancy',color)
                plt.tight_layout()
                plt.suptitle(prop_name, fontsize=14)
                fig.subplots_adjust(top=0.85)   
                plt.show()
                pdf.savefig(fig)
                plt.close()
                # fig.ylim(min, max*1.15)
            except Exception:
                print(f'error found in {prop_name} with STR ID of {star}')
                pass
        
        for i,starid in enumerate(star_df.STARID.unique()):
            try:
                prop_name = dodge_census[dodge_census.StarID == starid]['Property'].item()
            except ValueError:
                prop_name= comp_set[comp_set.Subj_prop == starid].iloc[0,1]['Name'].item()
            print(f'Page #{i+1}: {prop_name}')
    return star_df , comp_set
