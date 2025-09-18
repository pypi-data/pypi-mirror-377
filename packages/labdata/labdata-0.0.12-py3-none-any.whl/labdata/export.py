# to load export to another table (e.g. for a data release).
from .utils import *

def _get_table(schema,table_name):
    obj = schema
    for t in table_name.split('.'):
        obj = getattr(obj,t)
    return obj

def table_to_object_name(string):
    string = string.split('.')[-1].strip('`').strip('#')
    components = [k for k in string.split('__') if k != '']
    components = '._'.join(components)
    components = components.split('_')
    return ''.join(x.title() for x in components)

def parse_query_to_export(query,schema,allowed_schemas = None):
    if allowed_schemas is None:
        allowed_schemas  = [query.database]
        if '_computed' in query.database:
            allowed_schemas += [query.database.replace('_computed','')]
        if not '_computed' in query.database:
            allowed_schemas += [query.database + '_computed']
    tables = [(table_to_object_name(k)) for k in query.parents() if k.split('.')[0].strip('`') in allowed_schemas]
    tables = np.unique(tables)
    lines = []
    projections = dict()
    for line in query.definition.split('\n'):
        for t in tables:
            if t in line:
                lines.append(line.strip(' '))
                break
        if 'proj' in line:
            s = line.split('.proj(')
            tbl = s[0].split(' ')[-1] # key name
            s = s[1].strip(',)').strip(' )')
            p = eval(f'dict({s})')
            invdict = dict()
            for k,v in p.items():
                invdict[v] = k
            if not tbl in projections.keys():
                projections[tbl] = []
            projections[tbl].append(invdict)
    parent_queries = {table_to_object_name(query.table_name):query} # include the original query.
    for table in tables:
        if table in projections.keys():                
            parent_queries[table] = _get_table(schema,table) & [query.proj(**p) for p in projections[table]]
        else:
            parent_queries[table] = _get_table(schema,table) & query
        if len(parent_queries[table].parents()):
            qq = parse_query_to_export(parent_queries[table],schema)
            for q in qq.keys():
                if q in parent_queries.keys(): # merge with other tables
                    if len(qq[q]):
                        qq[q] = (_get_table(schema,q).proj() & parent_queries[q]).proj() & (_get_table(schema,q).proj() & qq[q]).proj()
                parent_queries[q] = qq[q]
    missing = dict()
    for q in parent_queries.keys():
        if len(parent_queries[q].parts()):
            tbl = [(table_to_object_name(k)) for k in parent_queries[q].parts() if k.split('.')[0].strip('`') in allowed_schemas]
            for t in tbl:
                qry = _get_table(schema,t) & parent_queries[q]
                if t in parent_queries.keys():
                    parent_queries[t] = qry # replace with the full query
                else:
                    missing[t] = qry
    parent_queries = dict(parent_queries,**missing)
    # delete takes time, better to just try to upload.
    # for k in list(parent_queries.keys()):
    #     if len(parent_queries[k])==0:
    #         del parent_queries[k]
    #         print(k)
    return parent_queries

def migrate_to_project(query,orig,new, allowed_schemas = None,  already_inserted = ['File'],max_loop_counts = 100):
    parent_queries = parse_query_to_export(query,orig)

    if allowed_schemas is None:
        allowed_schemas  = [query.database]
        if not '_computed' in query.database:
            allowed_schemas += [query.database + '_computed']
    
    to_insert = list(parent_queries.keys())
    # this will skip the global tables
    for t in parent_queries.keys():
        # parent_queries
        if not new.schema_project in _get_table(new,t).database:
            already_inserted += [t]
            to_insert.pop(to_insert.index(t))
    
    loop_count = 0
    while True: # inserts have to be done in order.
        for p in to_insert:
            q = parent_queries[p].parents()
            tables = [(table_to_object_name(k)) for k in q if k.split('.')[0].strip('`') in allowed_schemas]
            insert = False
            if not len(tables): # insert right away
                insert = True
            else:
                insert = True
                for t in tables:
                    if not t in already_inserted:
                        insert = False
            if insert:
                dat = (_get_table(orig,p) & parent_queries[p].proj()).fetch(as_dict = True)
                _get_table(new,p).insert(dat,skip_duplicates = True,allow_direct_insert=True)
                if 'LABDATA_VERBOSE' in os.environ.keys():
                    print(f'Inserted {p} [{len(dat)} rows] to {new.schema_project}')
                already_inserted.append(p)
                to_insert.pop(to_insert.index(p,))
        if not len(to_insert):
            break
        loop_count+=1
        if loop_count > max_loop_counts:
            raise(OSError(f'Could not export dataset after {loop_count} iterations.'))


def parallel_migrate(keys,hook, project1, project2,n_jobs = 10):
    def _parallel_migrate(key,project1,project2,hook):
        import os
        os.environ['LABDATA_VERBOSE'] = '1'
        import sys
        from labdata.export import load_project_schema,migrate_to_project
        schema = load_project_schema(project1)
        query = getattr(schema,hook) & key
        otherproject = load_project_schema(project2)
        migrate_to_project(query,schema,new = otherproject, allowed_schemas = None,  already_inserted = ['File'])
        otherproject.dj.conn.connection.close()

    from joblib import Parallel,delayed
    from tqdm import tqdm 
    Parallel(n_jobs = n_jobs)(delayed(_parallel_migrate)(k,project1,project2,hook) for k in tqdm(keys))