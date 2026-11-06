"""Inspection never calls user repr, properties or arbitrary iteration hooks."""
import math, types, itertools

class Inspector:
    def __init__(self):
        self.identities = {}
        self.next_id = 1

    def value(self, value, seen=None, depth=0):
        seen = set() if seen is None else seen
        t = type(value)
        name = type.__getattribute__(t, '__name__') if type(t) is type else 'object (custom metaclass)'
        base = dict(type=name, state='available', size=None, address=None)
        if value is None: return dict(base, value='None', type='NoneType')
        if t is bool: return dict(base, value='True' if value else 'False')
        if t is int:
            if value.bit_length()>12000:return dict(base,value='<integer exceeds capture quota>',state='truncated',encoding='decimal',signed=True)
            return dict(base, value=str(value), encoding='decimal', signed=True)
        if t is float: return dict(base, value=str(value), encoding='IEEE754-binary64', size=8)
        if t is str: return dict(base, value=value[:300], state='truncated' if len(value)>300 else 'available', encoding='Unicode', length=len(value))
        if t is bytes: return dict(base, value=value[:64].hex(), encoding='hex', length=len(value))
        if t in (types.FunctionType, types.BuiltinFunctionType, types.ModuleType, type):
            return dict(base, value='<'+name+'>', state='uncaptured')
        oid = id(value)
        # Keep references alive for run-scoped IDs; bounded by event/object quotas.
        if oid not in self.identities:
            if len(self.identities)>=4000:return dict(base,value='<identity quota>',state='truncated')
            self.identities[oid] = (str(self.next_id), value)
            self.next_id += 1
        identity = self.identities[oid][0]
        base.update(identity=identity, value='@'+identity)
        if oid in seen: return dict(base, relation='aliases')
        if depth >= 3: return dict(base, state='truncated')
        seen.add(oid)
        if t in (list, tuple): items = [(str(i),v) for i,v in enumerate(value[:32])]
        elif t is dict:
            items = []
            for i,(k,v) in enumerate(dict.items(value)):
                if i >= 32: break
                key = str(k) if type(k) in (str,int,bool,float) else '<key '+str(i)+'>'
                items.append((key,v))
        elif t in (set,frozenset):
            items = [(str(i),v) for i,v in enumerate(itertools.islice(value,32))]
        else:
            if type(t) is not type:return dict(base,state='uncaptured')
            # Invoke only CPython's storage descriptors directly. Do not resolve
            # attributes on the instance, execute properties, or call user hooks.
            classes=type.__getattribute__(t,'__mro__')
            mappings=[type.__getattribute__(cls,'__dict__') for cls in classes]
            if any('__getattribute__' in mapping for mapping in mappings[:-1]):return dict(base,state='uncaptured')
            fields={};storage=False
            for mapping in mappings:
                descriptor=mapping.get('__dict__')
                if type(descriptor) is types.GetSetDescriptorType:
                    raw=descriptor.__get__(value,t)
                    if type(raw) is dict:
                        storage=True
                        for key,item in itertools.islice(dict.items(raw),32):
                            if type(key) is str:fields.setdefault(key,item)
                for key,descriptor in mapping.items():
                    if type(descriptor) is types.MemberDescriptorType and len(fields)<32:
                        storage=True
                        try:fields.setdefault(key,descriptor.__get__(value,t))
                        except AttributeError:pass
            if not storage:return dict(base,state='uncaptured')
            return dict(base,children={key:self.value(item,seen,depth+1) for key,item in fields.items()},length=len(fields),state='truncated' if len(fields)>=32 else 'available')
        children = {k:self.value(v,seen,depth+1) for k,v in items}
        return dict(base, children=children, length=len(value), state='truncated' if len(value)>32 else 'available')

    def locals(self, values):
        return {k:self.value(v) for k,v in list(values.items())[:64] if not k.startswith('__')}
