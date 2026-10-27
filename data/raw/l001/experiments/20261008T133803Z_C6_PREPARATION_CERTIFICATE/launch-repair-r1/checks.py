"""One finite preflight and a separate exact-rational local decision audit."""
from common import *
from inherited.series import bounds, interval
from collections import defaultdict
import math, subprocess

def rational_decision(raw):
    """Recompute interval algebra with Fraction, without flow.decision or Arb."""
    def add(a,b):return (a[0]+b[0],a[1]+b[1])
    def mul(a,b):
        v=[x*y for x in a for y in b];return (min(v),max(v))
    def neg(a):return (-a[1],-a[0])
    def point(a):return (a,a)
    def mag(a):return max(abs(x) for x in a)
    zero=point(Q(0)); one=Q(1)
    def summ(v):
        out=zero
        for a in v:out=add(out,a)
        return out
    C=[[Q(x) for x in row] for row in raw['preconditioner']]
    F=[tuple(map(Q,x)) for x in raw['residual_at_center']]
    J=[[tuple(map(Q,x)) for x in row] for row in raw['jacobian_over_box']]
    c=list(map(Q,raw['center']));r=list(map(Q,raw['radii']))
    A=[list(row) for row in C];det=one
    for k in range(5):
        pivot=next((i for i in range(k,5) if A[i][k]),None)
        if pivot is None:raise ArithmeticError('Singular frozen preconditioner')
        if pivot!=k:A[k],A[pivot]=A[pivot],A[k];det=-det
        d=A[k][k];det*=d
        for i in range(k+1,5):
            z=A[i][k]/d
            for j in range(k+1,5):A[i][j]-=z*A[k][j]
            A[i][k]=Q(0)
    M=[[add(point(Q(i==j)),neg(summ(mul(point(C[i][k]),J[k][j]) for k in range(5)))) for j in range(5)] for i in range(5)]
    b=[neg(summ(mul(point(C[i][k]),F[k]) for k in range(5))) for i in range(5)]
    rad=[mag(b[i])+sum(mag(M[i][j])*r[j] for j in range(5)) for i in range(5)]
    norm=[sum(mag(M[i][j])*r[j] for j in range(5))/r[i] for i in range(5)]
    passed=all(a<Q(CFG['scientific_gates']['strict_image_radius_fraction'])*v for a,v in zip(rad,r)) and all(v<=Q(CFG['scientific_gates']['weighted_contraction_max']) for v in norm)
    return {'passed':passed,'preconditioner_determinant':str(det),
       'image_radius':[str(v) for v in rad],'image_radius_ratio':[str(v/u) for v,u in zip(rad,r)],
       'weighted_row_norm':[str(v) for v in norm],
       'root_enclosure':[[str(v-a),str(v+a)] for v,a in zip(c,rad)],
       'method':'Exact Fraction interval algebra, separate implementation from producer Arb decision.',
       'failure_is_not_exclusion':True}

def raw_decision(center,box):
    D=rec.read(ROOT/'DESIGN.json');c=list(map(Q,D['center']));r=list(map(Q,D['radii']))
    return {'schema':'lin-c6-raw-interval-decision/v1','method':'krawczyk','dimension':5,
       'coordinate_names':CFG['unknowns'],'bits':center['bits'],
       'center':D['center'],'radii':D['radii'],
       'box':[[str(v-a),str(v+a)] for v,a in zip(c,r)],
       'preconditioner':D['preconditioner'],
       'residual_at_center':[[str(t) for t in bounds(v)] for v in center['map']['F']],
       'jacobian_over_box':[[[str(t) for t in bounds(v)] for v in row] for row in box['map']['J']],
       'residual_over_box':[[str(t) for t in bounds(v)] for v in box['map']['F']],
       'source_guard':center['guard']}

def numerical_state(st):
    return {k:v for k,v in st.items() if k not in ('elapsed_seconds','cpu_seconds')}

def preflight(g):
    import flow, physics, mapping
    ctx.prec=768
    out=ROOT/'preflight';out.mkdir(exist_ok=True)
    checks={};evidence={}
    # Exact polynomial endpoint identities; no sampling of the H5/H7 controls.
    identities=[]
    for j in (5,7):
        for owner in (0,1):
            c=physics.shape_unit(j,owner)
            for side in (0,1):
                for n in range(j+1):
                    value=sum((v*math.prod(range(k-n+1,k+1))*side**(k-n) for k,v in enumerate(c) if k>=n),fmpq(0))
                    identities.append(value==int(n==j and side==owner))
    checks['exact_H5_H7_endpoint_controls']=all(identities)
    evidence['exact_shape_identities']=len(identities)
    # tx identity expanded in independent commutative monomials.
    terms=defaultdict(Q)
    def put(co,*names):terms[tuple(sorted(names))]+=Q(co)
    for co,names in [(1,('e','Bx','At')),(1,('e','Bt','Ax')),(-1,('e','At','Ax')),('-1/3',('e','Ft','Fx')),(-1,('e','Bt','Ax')),('1/6',('sigma','Up','Ft')),(-1,('e','At','Bx')),(1,('e','At','Ax')),('1/3',('e','Ft','Fx')),('-1/6',('sigma','Up','Ft'))]:put(co,*names)
    checks['exact_tx_wall_identity']=all(v==0 for v in terms.values())
    evidence['metric_even_corner_coefficients']={str(n):[math.comb(n-1,j-1) for j in range(2,n+1,2)] for n in (2,4,6)}
    # Re-evaluate the saved candidate's entire original-equation time jet,
    # reading saved polynomials only and importing no old executing runtime.
    ref=mapping.Reference();cand=loadin('c6_p100');par={k:arb(exact(v)) for k,v in loadin('native_binding')['model_exact'].items()};par['k']=ref.k
    residual_max=fmpq(0)
    for side in (0,1):
        h=ref.jets(fmpq(side),fmpq(side),7)
        jets={k:physics.Jet([v/(math.factorial(n)*ref.D**n) for n,v in enumerate(values)]) for k,values in h.items()}
        rows=physics.time_rows(jets['A'],jets['A']+jets['q'],jets['Phi'],jets['ell'],par,side)
        for i in range(4):
            for j in range(3):
                residual_max=max(residual_max,mapping.magnitude(rows[i][j].v-arb(exact(cand['rows'][side][i][j]))))
    checks['saved_original_equation_24_rows']=residual_max<exact('1e-25')
    evidence['saved_rows_max_absolute_difference']=str(residual_max)
    # Fresh-process exact native state recovery at a real validated cell.
    st=flow.initial(768,'center',g);flow.advance(st);rec.save(out,st,g)
    starting_digest=rec.read(out/'LATEST.json')['digest']
    import __main__
    __main__.publish_progress('preflight','RUNNING',st,phase='REAL_CHECKPOINT_STATUS_CONTROL')
    checks['progress_counter_serializes_as_native_integer']=type(rec.read(ROOT/'progress'/'preflight.json')['total_cells']) is int
    expected=rec.unpack(rec.pack(st));flow.advance(expected)
    child=subprocess.run([sys.executable,'-B',str(ROOT/'run.py'),'resume-control','--guard',g],check=True,capture_output=True,text=True)
    got=rec.read(out/'FRESH_PROCESS.json')
    checks['fresh_process_identical_next_cell']=got['numeric_fingerprint']==rec.fingerprint(numerical_state(expected))
    checks['fresh_process_exact_launch_state']=got['loaded_fingerprint']==rec.fingerprint(numerical_state(st))
    evidence['resume_child']=got
    # A deliberately uncommitted file must have no effect on the live pointer.
    rec.atomic(out/'checkpoints'/'unused.uncommitted',{'uncommitted':True})
    checks['uncommitted_file_ignored']=rec.fingerprint(numerical_state(rec.load(out,g)))==rec.fingerprint(numerical_state(st)) and rec.read(out/'LATEST.json')['digest']==starting_digest
    rejected=False
    try:rec.load(out,'changed-binding-must-fail')
    except AssertionError:rejected=True
    checks['changed_binding_rejected']=rejected
    D=rec.read(ROOT/'DESIGN.json');checks['design_origin_still_bound']=all(rec.sha(inputs()[k])==v for k,v in D['input_hashes'].items())
    # Exercise independent decision both ways on exact synthetic linear maps.
    raw={'preconditioner':[[str(int(i==j)) for j in range(5)] for i in range(5)],
         'residual_at_center':[['0','0']]*5,'jacobian_over_box':[[[str(int(i==j))]*2 for j in range(5)] for i in range(5)],'center':['0']*5,'radii':['1']*5}
    checks['rational_pass_control']=rational_decision(raw)['passed']
    raw['residual_at_center'][0]=['2','2'];checks['rational_incomplete_control']=not rational_decision(raw)['passed']
    result={'utc':rec.now(),'guard':g,'checks':checks,'evidence':evidence,'all_passed':all(checks.values()),
        'scope':'Finite implementation and exact-recovery preflight, not a scientific certificate.'}
    rec.atomic(ROOT/'PREFLIGHT.json',result,True)
    if not result['all_passed']:raise ArithmeticError('Frozen preflight failed')
    return result
