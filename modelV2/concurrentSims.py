import simpy


class Asset():
    """
    asset that needs some maintenace
    creating the asset starts the assets processes

    to keep thins simple, I modeled  just the maintenace task and skipped a prime task that would
    get interuppted when it was time to do maintence
    """

    def __init__(self, env, id, maintTasks):
        """
        store attributes, kick opp mantence process
        """
        self.id = id
        self.env = env
        self.maintTasks = maintTasks

        self.env.process(self.do_maintence())

    def do_maintence(self):
        """
        waits till time to do maintence
        grabs a work location resource
        do each maintence task
        each maintaince task has a list of resouces that are grabbed at the same time
        and once they have all been seized
        then the maintence task's list of processes are all kicked off at the same time
        affter all the process are finish, then all the resources are released
        """

        yield self.env.timeout(3)

        print(f'{self.env.now} object {self.id} is starting maintense')

        # grab work location
        with workLocRes.request() as workReq:
            yield workReq
            print(f'{self.env.now} object {self.id} got work loc, starting tasks')

            # for each maintTask, get the list of resources, and tasks
            for res, tasks in self.maintTasks:
                print(f'{self.env.now} -- object {self.id} start loop tasks')

                # get the requests for the needed resources
                print(f'{self.env.now} object {self.id} res 1: {res1.count}, res 2: {res2.count}')
                resList = []
                for r in res:
                    req = r.request()
                    req.r = r  # save the resource in the request
                    resList.append(req)
                # one yield that waits for all the requests
                yield self.env.all_of(resList)
                print(f'{self.env.now} object {self.id} res 1: {res1.count}, res 2: {res2.count}')

                # start all the tasks and save the events
                taskList = []
                for t in tasks:
                    taskList.append(self.env.process(t(self.env, self.id)))
                # one yield that waits for all the processes to finish
                yield self.env.all_of(taskList)

                for r in resList:
                    r.r.release(r)
                print(f'{self.env.now} object {self.id} res 1: {res1.count}, res 2: {res2.count}')
                print(f'{self.env.now} -- object {self.id} finish loop tasks')

            print(f'{self.env.now} object {self.id} finish all tasks')


# some processes for a maintence task
def task1(env, obj_id):
    print(f'{env.now} starting task 1 for object {obj_id}')
    yield env.timeout(3)
    print(f'{env.now} finish task 1 for object {obj_id}')


def task2(env, obj_id):
    print(f'{env.now} starting task 2 for object {obj_id}')
    yield env.timeout(3)
    print(f'{env.now} finish task 2 for object {obj_id}')


def task3(env, obj_id):
    print(f'{env.now} starting task 3 for object {obj_id}')
    yield env.timeout(3)
    print(f'{env.now} finish task 3 for object {obj_id}')


env = simpy.Environment()

workLocRes = simpy.Resource(env, capacity=3)
res1 = simpy.Resource(env, capacity=4)
res2 = simpy.Resource(env, capacity=5)

# build the maintence task with nested list of resources, and nested processes
maintTask = []
maintTask.append(([res1], [task1]))
maintTask.append(([res1, res2], [task2, task3]))

## is of simpy resources and generators

# creating asset also starts it
a = Asset(env, 1, maintTask)

env.run(20)
