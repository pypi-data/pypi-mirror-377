import numpy as np

np.random.seed(42)


kappa=0.65
gamma=0.41
tau=0.98
alpha=0.32
epsilon=0.34
Eo=0.4
TE=0.04
vo=0.08
r0=25.0
theta0=40.3
t_min=0.0
rtol=1e-5
atol=1e-8
ialpha = 1.0 / alpha


def do_bold_step(r_in, s, f, ftilde, vtilde, qtilde, v, q, dtt):
    

    s[1] = s[0] + dtt * (r_in - kappa * s[0] - gamma * (f[0] - 1))
    f[0] = np.clip(f[0], 1, None)
    ftilde[1] = ftilde[0] + dtt * (s[0] / f[0])
    fv = v[0] ** ialpha  # outflow
    vtilde[1] = vtilde[0] + dtt * ((f[0] - fv) / (tau * v[0]))
    q[0] = np.clip(q[0], 0.01, None)
    ff = (1 - (1 - Eo) ** (1 / f[0])) / Eo  # oxygen extraction
    qtilde[1] = qtilde[0] + dtt * ((f[0] * ff - fv * q[0] / v[0]) / (tau * q[0]))

    f[1] = np.exp(ftilde[1])
    v[1] = np.exp(vtilde[1])
    q[1] = np.exp(qtilde[1])

    f[0] = f[1]
    s[0] = s[1]
    ftilde[0] = ftilde[1]
    vtilde[0] = vtilde[1]
    qtilde[0] = qtilde[1]
    v[0] = v[1]
    q[0] = q[1]


def test_do_bold_step():
    
    # initialize with random values
    nn = 3
    r_in = np.random.rand(nn)
    s = np.random.rand(2, nn)
    f = np.random.rand(2, nn)
    ftilde = np.random.rand(2, nn)
    vtilde = np.random.rand(2, nn)
    qtilde = np.random.rand(2, nn)
    v = np.random.rand(2, nn)
    q = np.random.rand(2, nn)    
    dtt = 0.01

    do_bold_step(r_in, s, f, ftilde, vtilde, qtilde, v, q, dtt)

    #print each vector with 4 decimal places and in one row
    print(np.array2string(s[0], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(s[1], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(f[0], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(f[1], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(ftilde[0], precision=4, separator=', ', suppress_small=True)
    )
    print(np.array2string(ftilde[1], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(vtilde[0], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(vtilde[1], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(qtilde[0], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(qtilde[1], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(v[0], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(v[1], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(q[0], precision=4, separator=', ', suppress_small=True))
    print(np.array2string(q[1], precision=4, separator=', ', suppress_small=True))
    
    
    
test_do_bold_step()