from scipy.stats import poisson


r = int(poisson.rvs(0.6, size=1))

print(r)