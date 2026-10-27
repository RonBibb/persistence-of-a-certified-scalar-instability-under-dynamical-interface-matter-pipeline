"""Serialization cannot make failure metadata depend on rational conversion."""
import json
import os

def attempt(fun):
    try:
        return {'value':fun()}
    except Exception as exc:
        return {'error':type(exc).__name__+': '+str(exc)}

def raw(x):
    return {'str':attempt(lambda:str(x)), 'repr':attempt(lambda:repr(x)),
            'finite':attempt(lambda:bool(x.is_finite())),
            'exact':attempt(lambda:bool(x.is_exact())),
            'midpoint':attempt(lambda:str(x.mid())),
            'radius':attempt(lambda:str(x.rad()))}

def detailed(x):
    out=raw(x)
    out['lo']=attempt(lambda:str(x.lower().fmpq()))
    out['hi']=attempt(lambda:str(x.upper().fmpq()))
    return out

def publish(path,data):
    # Exclusive name, fully serialized before opening; fsync precedes conversion phase.
    payload=json.dumps(data,indent=2)
    with path.open('x') as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
