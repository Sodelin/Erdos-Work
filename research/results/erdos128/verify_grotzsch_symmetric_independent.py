"""Independent exact audit of the symmetric Groetzsch certificate.

Uses direct bilinear cross-products for Bernstein coefficients and an exact
vertical sweep for geometric coverage. Does not import the primary verifier.
Run with Python 3; the JSON certificate must be beside this file.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json


def determinant(u, v):
    return u[0] * v[1] - u[1] * v[0]


def subtract(u, v):
    return tuple(a - b for a, b in zip(u, v))


def vertical_cut(triangle, x):
    points = []
    for p, q in zip(triangle, triangle[1:] + triangle[:1]):
        if min(p[0], q[0]) <= x <= max(p[0], q[0]):
            if p[0] == q[0]:
                if p[0] == x:
                    points.extend([p[1], q[1]])
            else:
                points.append(p[1] + (x-p[0]) * (q[1]-p[1]) / (q[0]-p[0]))
    return (min(points), max(points)) if points else None


def main():
    certificate = json.loads(Path(__file__).with_name(
        'grotzsch_symmetric_certificate.json').read_text())
    triangles = [[tuple(Q(v) for v in p) for p in cell['triangle']]
                 for cell in certificate['cells']]
    domain = [tuple(Q(v) for v in p)
              for p in certificate['initial_triangle']]
    assert set(domain) == {(Q(1, 5), Q(0)), (Q(3, 25), Q(2, 25)),
                           (Q(1, 15), Q(2, 25))}
    for triangle in triangles + [domain]:
        assert len(triangle) == 3
        assert determinant(subtract(triangle[1], triangle[0]),
                           subtract(triangle[2], triangle[0])) != 0

    edges = set()
    for i in range(5):
        j = (i + 1) % 5
        for edge in [(i, j), (i, 5+j), (j, 5+i), (10, 5+i)]:
            edges.add(tuple(sorted(edge)))
    assert len(edges) == 20
    assert not any(all(tuple(sorted(e)) in edges for e in combinations(t, 2))
                   for t in combinations(range(11), 3))

    maximum_coefficient = Q(0)
    for triangle, cell in zip(triangles, certificate['cells']):
        mask, pivot = cell['full_mask'], cell['pivot']
        assert type(mask) is int and 0 <= mask < (1 << 11)
        assert type(pivot) is int and 0 <= pivot < 11
        assert not (mask >> pivot & 1)
        selections = []
        for a, b in triangle:
            weights = [a]*5 + [b]*5 + [1-5*a-5*b]
            selected = [weights[i] if mask >> i & 1 else Q(0)
                        for i in range(11)]
            selected[pivot] = Q(1, 2) - sum(selected)
            assert sum(weights) == 1 and min(weights) >= 0
            assert sum(selected) == Q(1, 2)
            assert all(0 <= x <= w for x, w in zip(selected, weights))
            selections.append(selected)
        # If y=sum lambda_i*y_i, its objective has diagonal coefficients
        # F(y_i) and off-diagonal Bernstein coefficients y_i^T A y_j / 2.
        # This calculation does not use objective values at edge midpoints.
        for i in range(3):
            for j in range(i, 3):
                coefficient = sum(
                    selections[i][u]*selections[j][v]
                    + selections[j][u]*selections[i][v]
                    for u, v in edges) / 2
                assert coefficient <= Q(1, 50)
                maximum_coefficient = max(maximum_coefficient, coefficient)

    # Include every segment-intersection abscissa. Consequently the ordering
    # of affine vertical-interval endpoints cannot change inside a strip.
    segments = [(a, b) for triangle in triangles + [domain]
                for a, b in zip(triangle, triangle[1:] + triangle[:1])]
    critical_x = {p[0] for segment in segments for p in segment}
    for (p, q), (r, s) in combinations(segments, 2):
        d, e, h = subtract(q, p), subtract(s, r), subtract(r, p)
        denominator = determinant(d, e)
        if denominator:
            u = determinant(h, e) / denominator
            v = determinant(h, d) / denominator
            if 0 <= u <= 1 and 0 <= v <= 1:
                critical_x.add(p[0] + u*d[0])
    ordered_x = sorted(critical_x)
    sweep_x = ordered_x + [(a+b)/2 for a, b in zip(ordered_x, ordered_x[1:])]
    for x in sweep_x:
        outer = vertical_cut(domain, x)
        assert outer is not None
        intervals = sorted(interval for triangle in triangles
                           if (interval := vertical_cut(triangle, x)) is not None)
        covered_end = outer[0]
        for low, high in intervals:
            assert outer[0] <= low <= high <= outer[1]
            assert low <= covered_end, ('coverage gap', x, covered_end, low)
            covered_end = max(covered_end, high)
        assert covered_end == outer[1]

    print(json.dumps({
        'result': 'INDEPENDENT PASS',
        'triangles': len(triangles),
        'distinct_witnesses': len({(c['full_mask'], c['pivot'])
                                  for c in certificate['cells']}),
        'maximum_Bernstein_coefficient': str(maximum_coefficient),
        'critical_x_coordinates': len(critical_x),
        'vertical_sweep_checks': len(sweep_x),
        'arithmetic': 'Exact rational arithmetic',
        'verified_scope': 'Symmetric residual triangle; explicit sparse halves',
        'general_conjecture_solved': False,
    }, indent=2))


if __name__ == '__main__':
    main()
