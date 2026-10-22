"""Housing-only descriptions; no metro measure, inference or causal claim."""
import numpy as np

def price_descriptives(frame,minimum=30):
    valid=frame.loc[np.isfinite(frame.per_m2) & frame.per_m2.gt(0)]
    if len(valid)<minimum:
        return {'status':'insufficient_sample','n':len(valid),'unit':'toman_per_m2','variants':[]}
    periods=valid.month.dropna().unique()
    if len(periods)!=1:
        raise ValueError('Housing price descriptions require a single common month')
    def describe(name,data):
        if len(data)<minimum:
            return {'name':name,'n':len(data),'status':'insufficient_sample','median_per_m2':None,'q25_per_m2':None,'q75_per_m2':None}
        return {'name':name,'n':len(data),'status':'computed','median_per_m2':float(data.per_m2.median()),'q25_per_m2':float(data.per_m2.quantile(.25)),'q75_per_m2':float(data.per_m2.quantile(.75))}
    lower,upper=valid.per_m2.quantile([.005,.995])
    variants=[describe('all_candidate_records',valid),describe('without_0_5_percent_tails',valid.loc[valid.per_m2.between(lower,upper)]),describe('candidate_deduplicated',valid.loc[~valid.duplicate_candidate])]
    return {'status':'computed','unit':'toman_per_m2','price_basis':'total_apartment_asking_price_divided_by_area_m2','period':str(periods[0]),'n':len(valid),'median_per_m2':variants[0]['median_per_m2'],'q25_per_m2':variants[0]['q25_per_m2'],'q75_per_m2':variants[0]['q75_per_m2'],'median_total_asking_price_toman':float(valid.price_value.median()),'area_median_m2':float(valid.building_size.median()),'tail_rule':{'quantiles':[.005,.995],'lower_per_m2':float(lower),'upper_per_m2':float(upper),'flagged_n':int((~valid.per_m2.between(lower,upper)).sum()),'default_excludes_tails':False},'variants':variants,'scope_note':'Same-month candidate advertisements including missing-coordinate records; no metro-access restriction. Median and IQR are observed price distributions, not confidence intervals or transaction prices.'}

def housing_figure(summary,folder,contract):
    if summary['status']!='computed': return
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f7f5ef','axes.facecolor':'#f7f5ef','svg.hashsalt':'metropremium-housing-v1'})
    rows=[r for r in summary['variants'] if r['status']=='computed']
    labels={'all_candidate_records':'All candidate records (primary)','without_0_5_percent_tails':'Without lower/upper 0.5% tails (sensitivity)','candidate_deduplicated':'Attribute-deduplicated candidates (sensitivity)'}
    fig,ax=plt.subplots(figsize=(12,6))
    fig.subplots_adjust(left=.36,right=.97,top=.82,bottom=.23)
    for i,row in enumerate(rows):
        q1,median,q3=[row[key]/1e6 for key in ['q25_per_m2','median_per_m2','q75_per_m2']]
        ax.plot([q1,q3],[i,i],color='#70a6a0',linewidth=12,solid_capstyle='butt')
        ax.plot([median,median],[i-.13,i+.13],color='#183342',linewidth=3)
    ax.set_yticks(range(len(rows)),[f"{labels[r['name']]}\nN={r['n']:,}" for r in rows])
    ax.invert_yaxis()
    ax.set_ylim(len(rows)-.5,-.5)
    ax.set_xlabel('Asking price per m² — million toman')
    ax.set_title(f"Tehran apartment-sale listings | {summary['period']}\nMedian (navy mark) and interquartile range (teal segment)",loc='left',pad=20)
    fig.text(.025,.10,'Unit and total-price interpretation: owner confirmation; publisher verification not claimed.',fontsize=9)
    fig.text(.025,.065,'Official source: divarofficial/real_estate_ads | Price = total asking price / area in m²',fontsize=9)
    fig.text(.025,.03,'Historical advertisements, not transactions. No metro association or causal effect estimated.',fontsize=9)
    fig.savefig(folder/'housing-price-summary.png',dpi=240)
    svg=folder/'housing-price-summary.svg'
    fig.savefig(svg,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    plt.close(fig)
