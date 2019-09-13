import copy
import numpy as np

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def nelder_mead(f, x_start,
                step=1, no_improve_thr=10e-6,
                no_improv_break=10, max_iter=0,
                alpha=1., gamma=2., rho=0.5, sigma=0.5):
    '''
        @param f (function): function to optimize, must return a scalar score
            and operate over a numpy array of the same dimensions as x_start
        @param x_start (numpy array): initial position
        @param step (float): look-around radius in initial step
        @no_improv_thr,  no_improv_break (float, int): break after no_improv_break iterations with
            an improvement lower than no_improv_thr
        @max_iter (int): always break after this number of iterations.
            Set it to 0 to loop indefinitely.
        @alpha, gamma, rho, sigma (floats): parameters of the algorithm
            (see Wikipedia page for reference)
        return: tuple (best parameter array, best score)
    '''

    # init
    n = len(x_start)
    prev_best = f(x_start)
    no_improv = 0
    res = [[x_start, prev_best]]

    for i in range(n):
        x = np.copy(x_start)
        if isinstance(step, (list, np.ndarray)):
            x[i] = x[i] + step[i]
        else:
            x[i] = x[i] + step
        score = f(x)
        res.append([x, score])

    print(res)

    # simplex iter
    iters = 0
    while 1:
        print('iter', iters)
        # order
        res.sort(key=lambda x: x[1])
        best = res[0][1]

        # break after max_iter
        if max_iter > 0 and iters >= max_iter:
            return res[0]
        iters += 1

        # break after no_improv_break iterations with no improvement
        print('...best so far: %f' % best)

        if best < prev_best - no_improve_thr*np.abs(prev_best):
            no_improv = 0
            prev_best = best
        else:
            no_improv += 1

        if no_improv >= no_improv_break:
            return res[0]

        # centroid
        x0 = np.zeros(n)
        for tup in res[:-1]:
            x0 += tup[0] / n

        print('centroid', x0)

        # reflection
        xr = x0 + alpha*(x0 - res[-1][0])
        rscore = f(xr)
        if res[0][1] <= rscore < res[-2][1]:
            del res[-1]
            res.append([xr, rscore])
            continue

        # expansion
        if rscore < res[0][1]:
            xe = x0 + gamma*(xr - x0)
            escore = f(xe)
            if escore < rscore:
                del res[-1]
                res.append([xe, escore])
                continue
            else:
                del res[-1]
                res.append([xr, rscore])
                continue

        # contraction
        xc = x0 + rho*(res[-1][0] - x0)
        cscore = f(xc)
        if cscore < res[-1][1]:
            del res[-1]
            res.append([xc, cscore])
            continue

        # reduction
        x1 = res[0][0]
        nres = []
        for tup in res:
            redx = x1 + sigma*(tup[0] - x1)
            score = f(redx)
            nres.append([redx, score])
        res = nres

async def nelder_mead_async(f, x_start,
                step=1, no_improve_thr=10e-6,
                no_improv_break=10, max_iter=0,
                alpha=1., gamma=2., rho=0.5, sigma=0.5,
                progress_handler=None, message_handler=None):
    '''
        @param f (function): function to optimize, must return a scalar score
            and operate over a numpy array of the same dimensions as x_start
        @param x_start (numpy array): initial position
        @param step (float): look-around radius in initial step
        @no_improv_thr,  no_improv_break (float, int): break after no_improv_break iterations with
            an improvement lower than no_improv_thr
        @max_iter (int): always break after this number of iterations.
            Set it to 0 to loop indefinitely.
        @alpha, gamma, rho, sigma (floats): parameters of the algorithm
            (see Wikipedia page for reference)
        return: tuple (best parameter array, best score)
    '''

    # init
    n = len(x_start)
    prev_best = await f(x_start)
    no_improv = 0
    res = [[x_start, prev_best]]

    for i in range(n):
        x = np.copy(x_start)
        if isinstance(step, (list, np.ndarray)):
            x[i] = x[i] + step[i]
        else:
            x[i] = x[i] + step
        score = await f(x)
        res.append([x, score])

    print(res)

    # simplex iter
    iters = 0
    while 1:
        print('iter', iters)
        # order
        res.sort(key=lambda x: x[1])
        best = res[0][1]

        # break after max_iter
        if max_iter > 0 and iters >= max_iter:
            return res[0]
        iters += 1

        if progress_handler is not None:
            progress_handler(iters, max_iter)
        message_handler('Best SumSq: %d' % best)

        # break after no_improv_break iterations with no improvement
        if best < prev_best - no_improve_thr*np.abs(prev_best):
            no_improv = 0
            prev_best = best
        else:
            no_improv += 1

        if no_improv >= no_improv_break:
            return res[0]

        # centroid
        x0 = np.zeros(n)
        for tup in res[:-1]:
            x0 += tup[0] / n

        print('centroid', x0)

        # reflection
        xr = x0 + alpha*(x0 - res[-1][0])
        rscore = await f(xr)
        if res[0][1] <= rscore < res[-2][1]:
            del res[-1]
            res.append([xr, rscore])
            logger.debug('Using reflected point')
            continue

        # expansion
        if rscore < res[0][1]:
            xe = x0 + gamma*(xr - x0)
            escore = await f(xe)
            if escore < rscore:
                del res[-1]
                res.append([xe, escore])
                logger.debug('Using expanded point')
                continue
            else:
                del res[-1]
                res.append([xr, rscore])
                logger.debug('Using reflected point after expansion')
                continue

        # contraction
        xc = x0 + rho*(res[-1][0] - x0)
        cscore = await f(xc)
        if cscore < res[-1][1]:
            del res[-1]
            res.append([xc, cscore])
            logger.debug('Using contracted point')
            continue

        # reduction
        x1 = res[0][0]
        nres = []
        for tup in res:
            redx = x1 + sigma*(tup[0] - x1)
            score = await f(redx)
            nres.append([redx, score])
        res = nres
        logger.debug('Reducing points')
