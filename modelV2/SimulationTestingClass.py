from Simulation import Simulation

sim = Simulation("test", 4, 4)

print(sim.id)
print(sim.max_window)
sim.make_Vn()
print(sim.vn)
print(sim.number_of_routers)