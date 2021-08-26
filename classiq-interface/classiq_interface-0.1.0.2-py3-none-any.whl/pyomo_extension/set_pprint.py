@staticmethod
def _pprint_members(x):
    if x.isfinite():
        return "{" + str(sorted(x.ordered_data()))[1:-1] + "}"
    else:
        ans = " | ".join(str(_) for _ in x.ranges())
        if " | " in ans:
            return "(" + ans + ")"
        if ans:
            return ans
        else:
            return "[]"
