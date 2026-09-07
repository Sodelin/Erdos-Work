"""Exact certificate for all rotationally symmetric Groetzsch weightings.

Weights are a on each of the five cycle vertices, b on each of their five
Mycielski shadows, and c=1-5a-5b on the apex. This file proves the sparse-half
bound on the residual region alpha <= 2/5 by checking an exact finite covering
and explicit feasible sparse-half witnesses. The complement alpha >= 2/5 is
covered by Razborov, Sparse halves in triangle-free graphs (arXiv:2104.09406),
Theorem 3.6, extended from rational blowups to real weights by continuity.

All verification arithmetic is rational. No floating point, solver, or search
package is used. Run: python verify_grotzsch_symmetric.py
This certificate does not cover arbitrary nonsymmetric weightings.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json


def cross(a, b, p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def twice_area(poly):
    return abs(sum(a[0]*b[1]-a[1]*b[0]
                   for a,b in zip(poly,poly[1:]+poly[:1]))) if poly else F(0)


def clip_left(poly, a, b):
    out=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        vp,vq=cross(a,b,p),cross(a,b,q)
        if vp>=0:
            out.append(p)
        if vp*vq<0:
            out.append(tuple((vp*q[i]-vq*p[i])/(vp-vq) for i in range(2)))
    return out


def intersection(poly, tri):
    out=list(poly)
    for a,b in zip(tri,tri[1:]+tri[:1]):
        out=clip_left(out,a,b)
    return out


def canonical_triangle(tri):
    if cross(*tri)<0:
        tri=[tri[0],tri[2],tri[1]]
    assert cross(*tri)>0
    return tri


def decode_tri(tri):
    return canonical_triangle([tuple(map(F,p)) for p in tri])


def weights(p):
    a,b=p
    return [a]*5+[b]*5+[1-5*a-5*b]


edges=set()
for i in range(5):
    j=(i+1)%5
    edges.update([tuple(sorted((i,j))),tuple(sorted((i,j+5))),
                  tuple(sorted((j,i+5))),(i+5,10)])
edges=sorted(edges)
assert len(edges)==20
assert not any(all(tuple(sorted(e)) in edges for e in combinations(t,2))
               for t in combinations(range(11),3))

# Independently check the independent-set types used to identify alpha.
# With apex: at most two cycle vertices and no shadow. Without apex:
# (cycle,shadow) counts are dominated by (0,5),(1,3), or (2,2).
# a+3b <= max(5b,2a+2b) for a,b >=0, so alpha=max(5b,2a+2b,c+2a).
for mask in range(1<<11):
    if any((mask>>u)&1 and (mask>>v)&1 for u,v in edges):
        continue
    k=sum((mask>>i)&1 for i in range(5))
    l=sum((mask>>i)&1 for i in range(5,10))
    h=(mask>>10)&1
    assert (h and l==0 and k<=2) or (not h and k<=2 and l<={0:5,1:3,2:2}[k])
assert all(not any(u in s and v in s for u,v in edges)
           for s in [set(range(5,10)),{0,2,5,7},{0,2,10}])

cert=json.loads(Path(__file__).with_name('grotzsch_symmetric_certificate.json').read_text())
initial=decode_tri(cert['initial_triangle'])
# Exact vertex enumeration for the residual region a,b,c>=0 and alpha<=2/5.
# Every entry is a nonnegative affine form q0+q1*a+q2*b.
forms=[(F(0),F(1),F(0)),(F(0),F(0),F(1)),
       (F(1),F(-5),F(-5)),(F(2,5),F(0),F(-5)),
       (F(2,5),F(-2),F(-2)),(F(-3,5),F(3),F(5))]
residual_vertices=set()
for u,v in combinations(forms,2):
    det=u[1]*v[2]-u[2]*v[1]
    if not det:
        continue
    p=((-u[0]*v[2]+u[2]*v[0])/det,
       (-u[1]*v[0]+u[0]*v[1])/det)
    if all(q[0]+q[1]*p[0]+q[2]*p[1]>=0 for q in forms):
        residual_vertices.add(p)
assert residual_vertices==set(initial)

triangles=[]
max_coefficient=F(0)
patterns=set()
for cell in cert['cells']:
    tri=decode_tri(cell['triangle'])
    assert all(cross(a,b,p)>=0 for a,b in zip(initial,initial[1:]+initial[:1]) for p in tri)
    mask,pivot=cell['full_mask'],cell['pivot']
    assert isinstance(mask,int) and 0<=mask<(1<<11)
    assert isinstance(pivot,int) and 0<=pivot<11 and not ((mask>>pivot)&1)
    def objective(p,check=False):
        w=weights(p)
        y=[w[i] if (mask>>i)&1 else F(0) for i in range(11)]
        y[pivot]=F(1,2)-sum(y)
        if check:
            assert sum(w)==1 and min(w)>=0 and sum(y)==F(1,2)
            assert all(0<=yi<=wi for yi,wi in zip(y,w))
        return sum(y[u]*y[v] for u,v in edges)
    # All coordinates of w and y are affine, hence feasibility at vertices
    # guarantees feasibility throughout the triangle.
    values=[objective(p,True) for p in tri]
    coeff=values+[2*objective(tuple((tri[i][h]+tri[j][h])/2 for h in range(2)))
                  -(values[i]+values[j])/2 for i,j in combinations(range(3),2)]
    # Degree-two Bernstein representation over a triangle is a convex
    # combination of these six coefficients, including on its boundary.
    assert max(coeff)<=F(1,50), (cell,coeff)
    max_coefficient=max(max_coefficient,max(coeff))
    triangles.append(tri)
    patterns.add((mask,pivot))

# Verify the covering independently of the generator's subdivision log.
# Containment, no positive-area intersections, and equal total area establish
# full coverage because this is a finite union of closed triangles.
for a,b in combinations(triangles,2):
    assert twice_area(intersection(a,b))==0
assert sum(twice_area(t) for t in triangles)==twice_area(initial)

print(json.dumps({
    'result':'PASS',
    'verified_scope':'All rotationally symmetric Groetzsch weightings with alpha <= 2/5',
    'triangles':len(triangles),
    'distinct_witnesses':len(patterns),
    'largest_Bernstein_coefficient':str(max_coefficient),
    'covered_area':str(twice_area(initial)/2),
    'arithmetic':'Exact fractions; explicit witnesses; independent geometric coverage check',
    'all_symmetric_weights':'Follows on adjoining the known alpha >= 2/5 theorem and continuity',
    'arbitrary_nonsymmetric_weights':'Not established by this certificate'
},indent=2))
