#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import numpy as np
import pandas as pd
from tcrvalid.load_models import *
from tcrvalid.physio_embedding import SeqArrayDictConverter
from tcrvalid.defaults import *
from sklearn.cluster import DBSCAN

def get_features(df,trb_model=None,tra_model=None):
    """ Use dataframe of labeled TCRs and TCR-VALID TRA/TRB models to get features
    
    parameters
    -----------
    
    df: pd.DataFrame
        Dataframe of TCRs - expect labeled dataframe for this function. 
        In particular - pre_feature_TRB and/or pre_feature_TRA should be available
        columns containg the sequences to be put through TCR-VALID model. 
        Here those columns contain CDR2-CD3 sequences
        
    trb_model: tf model
        If None, don't include TRB features. Else use representation of this model. If
        tra_model also not None, features from two models are concatenated.
        
    tra_model: tf model
        If None, don't include TRA features. Else use representation of this model. If
        trb_model also not None, features from two models are concatenated. 
    
    """
    if trb_model is not None:
        f_l_trb = mapping.seqs_to_array(df.pre_feature.values,maxlen=28)
        x_l_trb,_,_ = trb_model.predict(f_l_trb)
    if tra_model is not None:
        f_l_tra = mapping.seqs_to_array(df.pre_feature_TRA.values,maxlen=28)
        x_l_tra,_,_ = tra_model.predict(f_l_tra)

    #y_l = df_labelled.label.values

    if tra_model is not None and trb_model is not None:
        print(x_l_trb.shape)
        print(x_l_tra.shape)
        x_l = np.concatenate([x_l_trb, x_l_tra],axis=1)
    elif tra_model is None:
        x_l = x_l_trb
    elif trb_model is None:
        x_l = x_l_tra
    else:
        raise ValueError()

    return x_l

if __name__=='__main__':

    if len(sys.argv) != 3:
        print("Usage: python %s <in_file> <out_file>" % sys.argv[0])
        sys.exit(1)

    args = sys.argv
    infile=sys.argv[1]
    outfile=sys.argv[2]

    from_keras = True
    model_names = {
        'TRB': ['1_2_full_40']
    }

    mapping = SeqArrayDictConverter()
    loaded_trb_models = load_named_models(model_names['TRB'],chain='TRB',as_keras=from_keras)
    trb_model = loaded_trb_models[model_names['TRB'][0]]
    
    df = pd.read_csv(infile,sep="\t")
    
    df.loc[:,'junction_aa'] = df.cdr3aa
    df['pre_feature'] = df.junction_aa.map(lambda x: x[1:-1])
    
    x_l = get_features(
      df,
      trb_model=trb_model,
      tra_model=None
    )
    
    eps=3.0
    min_samples=2
    metric='manhattan'
    eps_format=':.1f'
    
    dbs = DBSCAN(eps=eps,min_samples=min_samples,metric=metric)
    dbs.fit(x_l)
    eps_name = str('eps_{'+eps_format+'}').format(eps)
    df[eps_name] = dbs.labels_ # put cluster labels back into df that goes with representations

    df.to_csv(outfile, sep='\t', index=False, header=True)
