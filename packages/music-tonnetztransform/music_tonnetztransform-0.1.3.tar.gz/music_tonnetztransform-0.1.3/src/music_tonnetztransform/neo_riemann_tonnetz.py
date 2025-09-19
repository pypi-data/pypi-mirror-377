import re

class Tonnetz:
  DEG_IN_SCALE = 12

  # Operations table
  OPERATIONS = {
    'L': {'0,3,7': {7: 1}, '0,4,7': {0: -1}},
    'P': {'0,3,7': {3: 1}, '0,4,7': {4: -1}},
    'R': {'0,3,7': {0: -2}, '0,4,7': {7: 2}},
    'S23': {'0,3,6,8': {0: -1, 3: -1}, '0,2,5,8': {5: 1, 8: 1}},
    'S32': {'0,3,6,8': {6: 1, 8: 1}, '0,2,5,8': {0: -1, 2: -1}},
    'S34': {'0,3,6,8': {0: 1, 8: 1}, '0,2,5,8': {0: -1, 8: -1}},
    'S43': {'0,3,6,8': {3: -1, 6: -1}, '0,2,5,8': {2: 1, 5: 1}},
    'S56': {'0,3,6,8': {0: -1, 6: -1}, '0,2,5,8': {2: 1, 8: 1}},
    'S65': {'0,3,6,8': {3: 1, 8: 1}, '0,2,5,8': {0: -1, 5: -1}},
    'C32': {'0,3,6,8': {6: -1, 8: 1}, '0,2,5,8': {0: -1, 2: 1}},
    'C34': {'0,3,6,8': {0: -1, 8: 1}, '0,2,5,8': {0: -1, 8: 1}},
    'C65': {'0,3,6,8': {3: -1, 8: 1}, '0,2,5,8': {0: -1, 5: 1}},
  }

  # Transformation table
  TRANSFORMATIONS = {
    'P': 'op',
    'R': 'op',
    'L': 'op',
    'N': 'RLP',
    'S': 'LPR',
    'H': 'LPL',
    'S23': 'op',
    'S32': 'op',
    'S34': 'op',
    'S43': 'op',
    'S56': 'op',
    'S65': 'op',
    'C32': 'op',
    'C34': 'op',
    'C65': 'op',
  }

  def __init__(self, DEG_IN_SCALE=None):
    self.DEG_IN_SCALE = int(DEG_IN_SCALE) if DEG_IN_SCALE is not None else self.DEG_IN_SCALE
    if self.DEG_IN_SCALE < 2:
      raise ValueError('degrees in scale must be greater than one')

  def _apply_operation(self, token, pset_str, pset2orig):
    if token not in self.OPERATIONS or pset_str not in self.OPERATIONS[token]:
      raise ValueError(f"no set class [{pset_str}] for token '{token}'")
    for i, delta in self.OPERATIONS[token][pset_str].items():
      for pidx in pset2orig[i]:
        pidx[0] += delta
    new_set = []
    for v in pset2orig.values():
      for p in v:
        new_set.append(p[0])
    return sorted(new_set)

  def normalize(self, pset):
    if not pset:
      raise ValueError('pitch set must contain something')
    origmap = {}
    for p in pset:
      k = p % self.DEG_IN_SCALE
      origmap.setdefault(k, []).append([p])
    if len(origmap) == 1:
      return (','.join(str(k) for k in origmap), origmap)
    nset = sorted(origmap.keys())
    equivs = []
    for i in range(len(nset)):
      equivs.append([nset[(i + j) % len(nset)] for j in range(len(nset))])
    order = list(reversed(range(1, len(nset))))
    normal = []
    for i in order:
      min_span = self.DEG_IN_SCALE
      min_span_idx = []
      for eidx, eq in enumerate(equivs):
        span = (eq[i] - eq[0]) % self.DEG_IN_SCALE
        if span < min_span:
          min_span = span
          min_span_idx = [eidx]
        elif span == min_span:
          min_span_idx.append(eidx)
      if len(min_span_idx) == 1:
        normal = equivs[min_span_idx[0]]
        break
      else:
        equivs = [equivs[idx] for idx in min_span_idx]
    if not normal:
      normal = equivs[0]
    if normal[0] != 0:
      trans = self.DEG_IN_SCALE - normal[0]
      newmap = {}
      for i in normal:
        prev = i
        i = (i + trans) % self.DEG_IN_SCALE
        newmap[i] = origmap[prev]
      origmap = newmap
      normal = [(i + trans) % self.DEG_IN_SCALE for i in normal]
    return (','.join(str(i) for i in normal), origmap)

  def taskify_tokens(self, tokens, tasks=None):
    if tasks is None:
      tasks = []
    if not isinstance(tokens, (list, tuple)):
      tokens = re.findall(r'([A-Z][a-z0-9]*)', tokens)
    for t in tokens:
      if t in self.TRANSFORMATIONS:
        val = self.TRANSFORMATIONS[t]
        if val == 'op':
          tasks.append((t, self._apply_operation))
        elif isinstance(val, str):
          self.taskify_tokens(val, tasks)
        else:
          raise ValueError('unknown token in transformation table')
      else:
        raise ValueError(f"unimplemented transformation token '{t}'")
    return tasks

  def techno(self, measurecount=1):
    return (['tonn', 'tz'] * (8 * measurecount))

  def transform(self, tokens, pset):
    if not tokens:
      raise ValueError('tokens must be defined')
    if not pset:
      raise ValueError('pitch set must contain something')
    if isinstance(tokens, (list, tuple)) and tokens and isinstance(tokens[0], tuple):
      tasks = tokens
    else:
      tasks = self.taskify_tokens(tokens)
    new_pset = [[p] for p in pset]
    for task in tasks:
      norm, pset2orig = self.normalize([p[0] for p in new_pset])
      # pset2orig: {pitch_class: [[original_pitch], ...]}
      # We need to pass references to the original pitches so they can be mutated
      # So we build a mapping from pitch class to list of references
      # Already done in normalize
      new_pset = task[1](task[0], norm, pset2orig)
      new_pset = [[p] for p in new_pset]
    return [p[0] for p in new_pset]
