import multiprocessing

import functools

import pickle

import mrtparse
from tqdm import tqdm

import sys

def as_routes_append(store, asn, routes):
    if not asn in store:
        store[asn] = set()
    store[asn].add(routes)

def merge_as_routes(a, b):
    r = {}
    for i in a.keys() | b.keys():
        if i in a:
            if i in b:
                r[i] = a[i] | b[i]
            else:
                r[i] = a[i]
        else:
            r[i] = b[i]
    return r

def rib_entry_to_asn_route_pair(e):
    if e.err:
        return dict()
    if e.data['type'][0] == mrtparse.MRT_T['TABLE_DUMP_V2']:
        # print(1)
        # print(e.data)
        if e.data['subtype'][0] == mrtparse.TD_V2_ST['PEER_INDEX_TABLE']:
            return dict()
        elif (e.data['subtype'][0] == mrtparse.TD_V2_ST['RIB_IPV4_UNICAST']
            or e.data['subtype'][0] == mrtparse.TD_V2_ST['RIB_IPV4_MULTICAST']
            or e.data['subtype'][0] == mrtparse.TD_V2_ST['RIB_IPV6_UNICAST']
            or e.data['subtype'][0] == mrtparse.TD_V2_ST['RIB_IPV6_MULTICAST']):
            num = e.data['sequence_number']
            nlri = (e.data['prefix'], e.data['prefix_length'])
            # print('num', num)
            # print('nlri', nlri)
            as_origin = set()
            for rib_entry in e.data['rib_entries']:
                org_time = rib_entry['originated_time'][0]
                for attr in rib_entry['path_attributes']:
                    # if attr['type'][0] == mrtparse.BGP_ATTR_T['ORIGIN']:
                    #     origin = mrtparse.ORIGIN_T[attr['value']]
                    #     print(origin)
                    if attr['type'][0] == mrtparse.BGP_ATTR_T['AS_PATH']:
                        as_path = []
                        for seg in attr['value']:
                            if seg['type'][0] == mrtparse.AS_PATH_SEG_T['AS_SET']:
                                as_path.append('{%s}' % ','.join(seg['value']))
                            elif seg['type'][0] == mrtparse.AS_PATH_SEG_T['AS_CONFED_SEQUENCE']:
                                as_path.append('(' + seg['value'][0])
                                as_path += seg['value'][1:-1]
                                as_path.append(seg['value'][-1] + ')')
                            elif seg['type'][0] == mrtparse.AS_PATH_SEG_T['AS_CONFED_SET']:
                                as_path.append('[%s]' % ','.join(seg['value']))
                            else:
                                as_path += seg['value']
                        # print('as_path', as_path)
                        as_origin.add(as_path[-1])       
            # print('as_origin', as_origin)
            # print(nlri, as_origin)
            as_routes = {}
            for i in as_origin:
                as_routes_append(as_routes, i, nlri)
            print(as_routes)
            return as_routes
            # return list(
            #     map(
            #         lambda x: (x, nlri), as_origin
            #     )
            # )
    return dict()

def rib_to_as_routes_dict(rib_path):
    as_routes = functools.reduce(
        merge_as_routes, 
        tqdm(map(
            rib_entry_to_asn_route_pair, 
            mrtparse.Reader(rib_path)
        ))
    )
    return as_routes

def save_pkl(obj, fn):
    with open(fn, 'wb') as f:
        pickle.dump(obj, f)

def rib_to_pkl(rib_path, pkl_fn):
    as_routes = rib_to_as_routes_dict(rib_path)
    save_pkl(as_routes, pkl_fn)

def step_1_parse_rib():
    RIB_PATH = 'rib.20211224.0000'
    PKL_FN = 'rib.pkl'

    rib_to_pkl(RIB_PATH, PKL_FN)

if __name__ == '__main__':

    rib_filename = sys.argv[1]
    rib_to_pkl(rib_filename, 'rib.pkl')
    # as_routes = dict()
    # {
    #     '1': {
    #         ('1.1.1.0', 24),
    #     }
    # }

    # with open('rib.pkl', 'rb') as f:
    #     as_routes = pickle.load(f)

    # print(as_routes['36459'])
