"""
Analyze and print Dig's results
"""
import random
import pdb
from collections import Counter

import sage.all

import settings
import helpers.vcommon as CM

from data.inv.base import Inv

DBG = pdb.set_trace

mlog = CM.getLogger(__name__, settings.logger_level)


class Analysis:
    def __init__(self, dig, dinvs, dtraces, inps, total_time):
        """
        inps can be None
        symstates can be None 
        """
        self.dig = dig
        self.dinvs = dinvs
        self.dtraces = dtraces
        self.inps = inps
        self.total_time = total_time

    def analyze_symstates(self, symstates):

        def get_str(d):
            return "{} ({})".format(
                sum(d[k] for k in d),
                ', '.join('{} {}'.format(k, d[k]) for k in sorted(d.keys())))

        solver_calls = Counter()
        while not symstates.solver_calls.empty():
            (stat, is_succ) = symstates.solver_calls.get()
            stat = str(stat)
            solver_calls[stat] += 1

        def get_inv_typ(inv):
            assert inv is None or isinstance(inv, Inv), inv
            if inv is None:
                print('W: unknown inv type: {}'.format(inv))
                return "Unknown"
            else:
                return inv.__class__.__name__

            # inv = str(inv)
            # if "lambda" in inv:
            #     typ = "MinMax"
            # elif ">=" in inv or "<=" in inv:
            #     typ = "Ieq"
            # elif "==" in inv:
            #     typ = "Eqt"
            # else:
            #     print('W: unknown inv type: {}'.format(inv))
            #     typ = "Unknown"

            # print(inv, typ)

            # return typ

        def get_change(x, y):
            return "{}->{}".format(x, y)

        depth_stat_changes = Counter()
        change_stats = Counter()
        change_typs = Counter()  # unsat->sat
        change_depths = Counter()  # 9->10, 10->11
        while not symstates.depth_changes.empty():
            (inv,  stat0, depth0, stat1, depth1) = symstates.depth_changes.get()

            typ = get_inv_typ(inv)
            change_stats[typ] += 1

            change_typ = get_change(stat0, stat1)
            change_typs[change_typ] += 1

            change_depth = get_change(depth0, depth1)
            change_depths[change_depth] += 1

        solver_calls_s = "solver calls {}".format(get_str(solver_calls))
        change_stats_s = "stats {}".format(get_str(change_stats))
        change_typs_s = "change typs {}".format(get_str(change_typs))
        change_depths_s = "change depths {}".format(get_str(change_depths))

        ss = [solver_calls_s, change_stats_s, change_typs_s, change_depths_s]
        return ', '.join(ss)

    def doit(self):
        dig = self.dig
        inv_typs = ', '.join('{} {}'.format(self.dinvs.typ_ctr[t], t)
                             for t in sorted(self.dinvs.typ_ctr))

        symstates_s = ''
        try:
            if dig.symstates:
                symstates_s = self.analyze_symstates(dig.symstates)
        except AttributeError:  # DigTraces doesn't have symstates
            pass

        ss = ["file {}".format(dig.filename),
              "locs {}".format(len(self.dinvs)),
              "invs {} ({})".format(self.dinvs.siz, inv_typs),
              "traces {}".format(self.dtraces.siz),
              "inps {}".format(len(self.inps) if self.inps else 0),
              "time {:.2f}s".format(self.total_time),
              symstates_s,
              "rand seed {}, test ({}, {})".format(
                  dig.seed, random.randint(0, 100), sage.all.randint(0, 100))
              ]
        print("***",  ', '.join(s for s in ss if s))
        print(self.dinvs.__str__(print_stat=False))