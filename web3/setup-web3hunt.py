# -*- coding: utf-8 -*-
"""Provision a FRESH web3hunt/artex instance: LLM profiles -> skill -> tools -> mission.
Usage: python setup-web3hunt.py --base http://localhost:8790 --token <first-run-token>
No secrets inside; gateway api_key values are local dummies.
"""
import argparse, json, os, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))

def req(base, token, m, p, o=None, t=90):
    d = json.dumps(o).encode() if o is not None else None
    h = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    r = urllib.request.Request(base + p, data=d, headers=h, method=m)
    try:
        with urllib.request.urlopen(r, timeout=t) as x:
            return x.status, x.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--token', required=True)
    a = ap.parse_args()
    R = lambda m, p, o=None: req(a.base, a.token, m, p, o)

    profs = json.load(open(os.path.join(HERE, 'mission', 'llm-profiles.json')))
    pids = []
    for pr in profs:
        c, b = R('POST', '/api/llm/profiles', pr)
        pid = json.loads(b).get('id')
        pids.append(pid)
        print('profile', pr['name'], '->', c, pid)

    hunt = json.load(open(os.path.join(HERE, 'mission', 'hunt.json')))
    c, b = R('POST', '/api/tasks', {'name': hunt['name'], 'description': hunt['name'],
                                    'goal': hunt['root_goal'], 'llm_profile_ids': pids})
    tid = str(json.loads(b).get('id'))
    print('task ->', c, tid)
    for g in hunt['sub_goals']:
        body = {'text': g['text']}
        if g.get('vulnclass'):
            body['vulnclass'] = g['vulnclass']
        c, b = R('POST', '/api/tasks/%s/goals' % tid, body)
        print(' goal %.50s... -> %s' % (g['text'], c))
    c, b = R('PUT', '/api/tasks/%s/llm' % tid,
             {'llm_profile_ids': pids, 'active_llm_profile_id': pids[0]})
    print('pin llm ->', c)

    skdir = os.path.join(HERE, 'skills', 'web3-contract-audit')
    desc = ('General Web3/EVM contract audit and on-chain analysis harness for any deployed contract '
            'on any chain. Use to find exploitable logic in live code, confirm exploits on a mainnet fork, '
            'trace and size stolen funds, and build rescue PoCs.')
    c, b = R('POST', '/api/skills', {'name': 'web3-contract-audit', 'description': desc})
    print('skill create ->', c, b[:80])
    for dp, _, fns in os.walk(skdir):
        for f in fns:
            rel = os.path.relpath(os.path.join(dp, f), skdir).replace(os.sep, '/')
            txt = open(os.path.join(dp, f), encoding='utf-8').read()
            c, b = R('PUT', '/api/skills/web3-contract-audit/files/' + rel, {'content': txt})
            print(' file', rel, '->', c)

    tdir = os.path.join(HERE, 'tools')
    for f in sorted(os.listdir(tdir)):
        if not f.endswith('.json'):
            continue
        c, b = R('POST', '/api/tools/custom', json.load(open(os.path.join(tdir, f))))
        print(' tool', f, '->', c, b[:60])
    print('DONE. Hunt task id:', tid)

if __name__ == '__main__':
    main()
