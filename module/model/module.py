#
# Collective Knowledge (Universal predictive model)
#
# See CK LICENSE.txt for licensing details
# See CK Copyright.txt for copyright details
#
# Developer: Grigori Fursin
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# use model

def use(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    print ('use model')

    return {'return':0}

##############################################################################
# build model (universal)

def build(i):
    """

    Input:  {
              Select entries:

                (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                (module_uoa) or (experiment_module_uoa) - can be wild cards
                (data_uoa) or (experiment_data_uoa)     - can be wild cards

                (repo_uoa_list)                         - list of repos to search
                (module_uoa_list)                       - list of module to search
                (data_uoa_list)                         - list of data to search

                (search_dict)                           - search dict
                (ignore_case)                           - if 'yes', ignore case when searching

                (features_flat_keys_list)               - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (features_flat_keys_list)               - list of flat keys to extract from points into table
                                                          (for example, ##features#)
                (features_flat_keys_desc)               - list of flat key descriptions (not stable!)

                (characteristics_flat_keys_list)        - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (characteristics_flat_keys_index)       - add all flat keys starting from this index 
                                                          (for example, ##features#)

              Model:
                model_module_uoa                        - model module
                model_name                              - model name
                (model_params)                          - dict with model params
                (model_file)                            - model output file, otherwise generated as tmp file
                (keep_temp_files)                       - if 'yes', keep temp files 
                (remove_points_with_none)               - if 'yes', remote points with None
                (caption)                               - add caption to graphs, if needed

              (csv_file)                                - if !='', only record prepared table to CSV ...
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy
    import os

    o=i.get('out','')
    i['out']=''

    ktf=i.get('keep_temp_files','')

    cap=i.get('caption','')

    rpwn=i.get('remove_points_with_none','')

    cf=i.get('csv_file','')

    # Get table through experiment module for features
    ffkl=i.get('features_flat_keys_list',[])
    fdesc=i.get('features_flat_keys_desc',{})

    ffke=i.get('features_flat_keys_ext','')
    if ffke!='':
       ffkl1=[]
       for q in ffkl:
           q+=ffke
           ffkl1.append(q)
       ffkl=ffkl1

       fdesc1={}
       for q in fdesc:
           fdesc1[q+ffke]=fdesc[q]
       fdesc=fdesc1

    iif=copy.deepcopy(i)
    iif['action']='get'
    iif['module_uoa']=cfg['module_deps']['experiment']
    iif['flat_keys_list']=ffkl
    iif['flat_keys_index']=i.get('features_flat_keys_index','')
    r=ck.access(iif)
    if r['return']>0: return r
    ftable=r['table'].get('0',[])
    fkeys=r['real_keys']

    if len(ftable)==0:
       return {'return':1, 'error':'no points found'}

    # Get table through experiment module for characteristics
    iic=copy.deepcopy(i)
    iic['action']='get'
    iic['module_uoa']=cfg['module_deps']['experiment']
    iic['flat_keys_list']=i.get('characteristics_flat_keys_list',[])
    iic['flat_keys_index']=i.get('characteristics_flat_keys_index','')
    r=ck.access(iic)
    if r['return']>0: return r
    ctable=r['table'].get('0',[])
    ckeys=r['real_keys']

    if len(ctable)==0:
       return {'return':1, 'error':'no points found'}

    if rpwn=='yes':
       ftable1=[]
       ctable1=[]

       for q in range(0, len(ftable)):
           fv=ftable[q]
           cv=ctable[q]

           add=True
           for k in fv:
               if k==None:
                  add=False
                  break

           if add:
              for k in cv:
                  if k==None:
                     add=False
                     break

           if add:
              ftable1.append(fv)
              ctable1.append(cv)

       ftable=ftable1
       ctable=ctable1

    if cf!='':
       # Prepare common table from features and characteristics

       lftable=len(ftable)
       lctable=len(ctable)

       if lftable!=lctable:
          return {'return':1, 'error':'length of feature table ('+str(lftable)+'is not the same as length of characteristics table ('+str(lctable)+')'}

       dim=[]
       for q in range(0, lftable): 
           vv=[]
           for v in ftable[q]:
               vv.append(v)
           for v in ctable[q]:
               vv.append(v)
           dim.append(vv)

       # Prepare common keys
       keys=[]
       for q in fkeys:
           keys.append(q)
       for q in ckeys:
           keys.append(q)

       # Prepare temporary CSV file
       ii={'action':'convert_table_to_csv',
           'module_uoa':cfg['module_deps']['experiment'],
           'table':dim,
           'keys':keys,
           'file_name':cf,
           'csv_no_header':'no',
           'csv_separator':';',
           'csv_decimal_mark':'.'
          }
       r=ck.access(ii)
       if r['return']>0: return r

       return {'return':0}

    mmuoa=i['model_module_uoa']
    mn=i['model_name']
    mof=i.get('model_file','')
    if mof!='' and os.path.isfile(mof): os.remove(mof)

    # Calling model
    ii={'action':'build',
        'module_uoa':mmuoa,
        'model_name':mn,
        'model_params':i.get('model_params',{}),
        'model_file':mof,
        'features_table': ftable,
        'features_keys': fkeys,
        'features_desc': fdesc,
        'characteristics_table': ctable,
        'characteristics_keys': ckeys,
        'keep_temp_files':ktf,
        'caption':cap,
        'out':o
       }
    r=ck.access(ii)
    if r['return']>0: return r

    mif=r.get('model_input_file','')
    mf=r['model_file']

    if o=='con':
       if ktf=='yes' and mif!='':
         ck.out('Temp model input file '+mif)
       ck.out('Generated model was saved into file '+mf)

    i['out']=o

    return r

##############################################################################
# validate model (universal)

def validate(i):
    """

    Input:  {
              Select entries:

                (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                (module_uoa) or (experiment_module_uoa) - can be wild cards
                (data_uoa) or (experiment_data_uoa)     - can be wild cards

                (repo_uoa_list)                         - list of repos to search
                (module_uoa_list)                       - list of module to search
                (data_uoa_list)                         - list of data to search

                (search_dict)                           - search dict
                (ignore_case)                           - if 'yes', ignore case when searching

                (features_flat_keys_list)               - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (features_flat_keys_index)              - add all flat keys starting from this index 
                                                          (for example, ##features#)

                (characteristics_flat_keys_list)        - list of flat keys to extract from points into table
                                                          (order is important: for example, for plot -> X,Y,Z)
                (characteristics_flat_keys_index)       - add all flat keys starting from this index 
                                                          (for example, ##features#)

              Model:
                model_module_uoa                        - model module
                model_name                              - model name
                model_file                              - model file
                (keep_temp_files)                       - if 'yes', keep temp files 
                (remove_points_with_none)               - if 'yes', remote points with None
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              rmse
              prediction_rate
              observations
              mispredictions
            }

    """

    import copy
    import math
    import os

    o=i.get('out','')
    i['out']=''

    rpwn=i.get('remove_points_with_none','')

    mmuoa=i['model_module_uoa']
    mn=i['model_name']
    mf=i['model_file']

    mf8=mf+'.model.validation-with-labels.csv'
    if os.path.isfile(mf8): os.remove(mf8)

    ktf=i.get('keep_temp_files','')

    ffkl=i.get('features_flat_keys_list',[])
    fdesc=i.get('features_flat_keys_desc',{})

    ffke=i.get('features_flat_keys_ext','')
    if ffke!='':
       ffkl1=[]
       for q in ffkl:
           q+=ffke
           ffkl1.append(q)
       ffkl=ffkl1

       fdesc1={}
       for q in fdesc:
           fdesc1[q+ffke]=fdesc[q]
       fdesc=fdesc1

    # Get table through experiment module for features
    iif=copy.deepcopy(i)
    iif['action']='get'
    iif['module_uoa']=cfg['module_deps']['experiment']
    iif['flat_keys_list']=ffkl
    iif['flat_keys_index']=i.get('features_flat_keys_index','')
    r=ck.access(iif)
    if r['return']>0: return r
    ftable=r['table'].get('0',[])
    fkeys=r['real_keys']

    if len(ftable)==0:
       return {'return':1, 'error':'no points found'}

    mtable=r['mtable'].get('0',[])

    # Get table through experiment module for characteristics
    iic=copy.deepcopy(i)
    iic['action']='get'
    iic['module_uoa']=cfg['module_deps']['experiment']
    iic['flat_keys_list']=i.get('characteristics_flat_keys_list',[])
    iic['flat_keys_index']=i.get('characteristics_flat_keys_index','')
    r=ck.access(iic)
    if r['return']>0: return r

    ctable=r['table'].get('0',[])
    ckeys=r['real_keys']

    if rpwn=='yes':
       ftable1=[]
       ctable1=[]

       for q in range(0, len(ftable)):
           fv=ftable[q]
           cv=ctable[q]

           add=True
           for k in fv:
               if k==None:
                  add=False
                  break

           if add:
              for k in cv:
                  if k==None:
                     add=False
                     break

           if add:
              ftable1.append(fv)
              ctable1.append(cv)

       ftable=ftable1
       ctable=ctable1

    lctable=len(ctable)
    if lctable==0:
       return {'return':1, 'error':'no points found'}

    # Calling model
    ii={'action':'validate',
        'module_uoa':mmuoa,
        'model_name':mn,
        'model_file':mf,
        'features_table': ftable,
        'features_keys': fkeys,
        'keep_temp_files':ktf,
        'out':o
       }
    r=ck.access(ii)
    if r['return']>0: return r

    pt=r['prediction_table']
    lt=r['label_table']
    lpt=len(pt)

    if lctable!=lpt:
       return {'return':1, 'error':'length of characteristic table ('+str(lctable)+') is not the same as table with predictions ('+str(lpt)+')'}

    # Checking model
    s=0.0

    sx='Label:;Original value;predicted value'
    kk=mtable[0].get('features',{}).get('features',{})
    for a in kk:
        sx+=';'+a
    sx+='\n'

    imispredictions=0
    for k in range(0, lctable):
        v=ctable[k][0]
        pv=pt[k][0]

        label=lt[k][0]

        kk=mtable[k].get('features',{}).get('features',{})

        if type(v)==float:
           sv="%11.3f" % v
           pv=float(pv)
           pt[k][0]=pv
           spv="%11.3f" % pv
        else:
           sv=str(v)
           spv=str(pv)

        sx+=label+';'+sv+';'+spv
        for a in kk:
            sx+=';'+str(kk[a])
        sx+='\n'

#              sx+=';'+str(kk["derived_type_of_prog"])
#              sx+=';'+str(kk["type"])
#              sx+=';'+str(kk["test"])
#              sx+=';'+str(kk["test_id"])
#              sx+=';'+str(kk["version"])
#              sx+=';'+str(kk["compression"])
#              sx+=';'+str(kk["derived_samples_by_primitives"])
#              sx+=';'+str(kk["resolution"])
#              sx+=';'+str(kk["resw"])
#              sx+=';'+str(kk["resx"])
#              sx+=';'+str(kk["resy"])

        sdiff=''
        if type(v)==float or type(v)==int:
           if v==0:
              if v!=pv:
                 sdiff='***'
                 imispredictions+=1
           else:
              s+=(v-pv)*(v-pv)
              diff=abs(pv-v)/v
              x1=''
              if diff>0.1: #10%
                 x1=' ***'
                 imispredictions+=1
              sdiff="%7.3f" % diff + x1         

        else:
           if type(v)==bool:
              # hack
              xfloat=True
              try: xpv=float(pv)
              except Exception as e: xfloat=False

              if xfloat:
                 if xpv<0.5: 
                    spv='False ('+("%11.3f" % xpv)+')'
                    pv='False'
                 else: 
                    spv='True ('+("%11.3f" % xpv)+')'
                    pv='True'

              if str(pv)=='True': pt[k][0]=True
              else: pt[k][0]=False

           if str(v)!=str(pv):
              s+=1
              sdiff='***'
              imispredictions+=1

        if o=='con':
           import json
           x=json.dumps(ftable[k])
           line=str(1+k)+') '+x+' => '+sv+' '+spv+' '+sdiff
           ck.out(line)

    rmse=math.sqrt(s/lctable)
    rate=float(lctable-imispredictions)/float(lctable)

    r=ck.save_text_file({'text_file':mf8, 'string':sx})
    if r['return']>0: return r

    if o=='con':
       ck.out('')      

       ck.out('Model RMSE =      '+str(rmse))
       ck.out('Prediction rate = '+("%4.3f" % (rate*100))+'%')
       ck.out('Mispredictions =  '+str(imispredictions)+' out of '+str(lctable))

    # Visualize?
    if i.get('visualize','')=='yes':
       if o=='con':
          ck.out('')
          ck.out('Attempting to visualize ...')

       table={"0":[], "1":[]}
       for k in range(0, lctable):
           table["0"].append([0, ctable[k][0]])
           table["1"].append([0, pt[k][0]])

       ii={'action':'plot',
           'module_uoa':cfg['module_deps']['experiment.graph'],
           'table':table}
       iig=i.get('graph_params',{})
       ii.update(iig)
       r=ck.access(ii)
       if r['return']>0: return r

    i['out']=o
    return {'return':0, 'rmse':rmse, 'prediction_rate':rate, 'observations':lctable, 'mispredictions':imispredictions}

##############################################################################
# convert table to CSV

def convert_to_csv(i):
    """
    Input:  {
              Input from 'build' function

              csv_file - CSV file to record
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    return build(i)
