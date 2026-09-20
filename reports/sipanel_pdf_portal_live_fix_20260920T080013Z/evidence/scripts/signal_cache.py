# cross-process cache invalidation after the website language change made from the shell (no data change)
import json
W = env['website'].sudo().browse(1)
out = {'langs_db': W.language_ids.mapped('code'), 'cached_values_before': None}
try:
    out['cached_values_before'] = W._get_cached_values().get('language_ids') if isinstance(W._get_cached_values(), dict) else str(W._get_cached_values())[:200]
except Exception as e:
    out['cached_values_before'] = 'err ' + str(e)[:100]
env.registry.clear_cache()
env.registry.clear_cache('routing')
env.registry.clear_cache('templates')
if hasattr(env.registry, 'signal_changes'):
    env.registry.signal_changes()
    out['signal_changes'] = True
env.cr.commit()
print('SIG_JSON=' + json.dumps(out, default=str))
