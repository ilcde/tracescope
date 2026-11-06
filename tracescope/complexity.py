"""Conservative AST cost model. Unsupported effects return unknown, never a guessed badge."""
import ast

def analyze(source,language='python'):
    unknown={'classification':'unknown','bound':None,'space':None,'reason':'Unsupported effects or input-dependent control flow prevent a justified bound.','reasonVi':'Hiệu ứng chưa hỗ trợ hoặc luồng điều khiển phụ thuộc dữ liệu khiến chưa thể chứng minh cận.','assumptions':[],'ranges':[]}
    if language!='python':return dict(unknown,reason='Static bound analysis currently supports a restricted Python subset only.',reasonVi='Phân tích cận tĩnh hiện chỉ hỗ trợ một tập con Python có giới hạn.')
    try:tree=ast.parse(source)
    except SyntaxError:return unknown
    ranges=[];variables=set();space=False
    class Unsupported(Exception):pass
    def expression(node):
        nonlocal space
        if isinstance(node,(ast.Constant,ast.Name)):return
        if isinstance(node,(ast.BinOp,ast.UnaryOp,ast.Compare,ast.BoolOp)):
            for child in ast.iter_child_nodes(node):
                if isinstance(child,ast.expr):expression(child)
            if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Pow):raise Unsupported()
            return
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('len',):
            for child in node.args:expression(child)
            return
        if isinstance(node,ast.Subscript):expression(node.value);expression(node.slice);return
        raise Unsupported()
    def block(nodes,indices=None):
        indices=indices or {};power=0;log=0
        for node in nodes:
            if isinstance(node,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
                if node.value:expression(node.value)
                targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                if any(not isinstance(t,ast.Name) for t in targets):raise Unsupported()
            elif isinstance(node,(ast.Pass,ast.Return)):
                if isinstance(node,ast.Return) and node.value:expression(node.value)
            elif isinstance(node,ast.For):
                if not isinstance(node.target,ast.Name) or not isinstance(node.iter,ast.Call) or not isinstance(node.iter.func,ast.Name) or node.iter.func.id!='range':raise Unsupported()
                args=node.iter.args
                if len(args)!=1:raise Unsupported()
                bound=args[0]
                if isinstance(bound,ast.Name):variables.add(indices.get(bound.id,bound.id));factor=1
                elif isinstance(bound,ast.Constant) and isinstance(bound.value,int) and bound.value>=0:factor=0
                else:raise Unsupported()
                # Mutating loop-bound variables is outside this model.
                if isinstance(bound,ast.Name) and any(isinstance(x,(ast.Assign,ast.AugAssign,ast.AnnAssign)) and any(isinstance(t,ast.Name) and t.id==bound.id for t in (x.targets if isinstance(x,ast.Assign) else [x.target])) for child in node.body for x in ast.walk(child)):raise Unsupported()
                p,l=block(node.body,{**indices,node.target.id:bound.id if isinstance(bound,ast.Name) else 'constant'})
                if (p+factor,l)>(power,log):power,log=p+factor,l
                ranges.append({'start':node.lineno,'end':node.end_lineno,'rule':'bounded range iteration','ruleVi':'lặp range có cận'})
            elif isinstance(node,ast.If):
                expression(node.test);p1,l1=block(node.body,indices);p2,l2=block(node.orelse,indices);power,log=max((power,log),(p1,l1),(p2,l2))
            elif isinstance(node,ast.FunctionDef):
                p,l=block(node.body,indices);power,log=max((power,log),(p,l))
            else:raise Unsupported()
        return power,log
    try:
        power,log=block(tree.body)
        if len(variables)>1:return dict(unknown,reason='Multiple independent size symbols require a multivariate model.',reasonVi='Nhiều biến kích thước độc lập cần mô hình đa biến.')
        n=next(iter(variables),'n');term='1' if power==0 else n if power==1 else n+'^'+str(power)
        return {'classification':'justified bound','bound':'O('+term+')','space':'O(1) auxiliary scalar slots',
                'reason':'Upper bound from bounded range iteration and sequential composition; no unsupported calls were accepted.',
                'reasonVi':'Cận trên suy ra từ vòng lặp range có cận và phép hợp thành tuần tự; không chấp nhận lời gọi chưa biết chi phí.',
                'assumptions':['Nonnegative range sizes remain invariant','Unit-cost scalar arithmetic; Python integer bit-growth excluded','Input/output storage excluded; no claim about process RSS'],
                'assumptionsVi':['Kích thước range không âm và không thay đổi','Phép toán vô hướng có chi phí đơn vị; chưa tính độ dài số nguyên','Không tính bộ nhớ đầu vào/đầu ra; không suy ra RSS'], 'ranges':ranges,'sizeVariables':list(variables)}
    except Unsupported:return unknown
