"""Side-effect-free breakpoint predicates over exact primitive locals only."""
import ast, operator
OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.FloorDiv:operator.floordiv,ast.Mod:operator.mod}
CMPS={ast.Eq:operator.eq,ast.NotEq:operator.ne,ast.Lt:operator.lt,ast.LtE:operator.le,ast.Gt:operator.gt,ast.GtE:operator.ge,ast.Is:operator.is_,ast.IsNot:operator.is_not}

def predicate(source):
    if not source:return lambda values:True
    if not isinstance(source,str) or len(source)>300:raise ValueError('Breakpoint condition must be at most 300 characters')
    tree=ast.parse(source,mode='eval')
    allowed=(ast.Expression,ast.Name,ast.Load,ast.Constant,ast.Compare,ast.BoolOp,ast.And,ast.Or,ast.UnaryOp,ast.Not,ast.USub,ast.UAdd,ast.BinOp,*OPS,*CMPS)
    if any(not isinstance(node,allowed) for node in ast.walk(tree)):raise ValueError('Conditions accept primitive names, constants, comparisons and bounded arithmetic only; no calls, attributes or indexing')
    def scalar(value):
        if type(value) not in (int,float,bool,str,type(None)):raise ValueError('Non-primitive operand')
        if type(value) is int and value.bit_length()>1024:raise ValueError('Integer condition quota')
        if type(value) is str and len(value)>1000:raise ValueError('String condition quota')
        return value
    def evaluate(node,values):
        if isinstance(node,ast.Name):return scalar(values[node.id])
        if isinstance(node,ast.Constant):return scalar(node.value)
        if isinstance(node,ast.BoolOp):
            return all(bool(evaluate(v,values)) for v in node.values) if isinstance(node.op,ast.And) else any(bool(evaluate(v,values)) for v in node.values)
        if isinstance(node,ast.UnaryOp):
            value=evaluate(node.operand,values)
            return not value if isinstance(node.op,ast.Not) else scalar(-value if isinstance(node.op,ast.USub) else +value)
        if isinstance(node,ast.BinOp):
            left,right=evaluate(node.left,values),evaluate(node.right,values)
            if type(left) not in (int,float,bool) or type(right) not in (int,float,bool):raise ValueError('Arithmetic accepts numbers only')
            return scalar(OPS[type(node.op)](left,right))
        if isinstance(node,ast.Compare):
            left=evaluate(node.left,values)
            for operation,other in zip(node.ops,node.comparators):
                right=evaluate(other,values)
                if not CMPS[type(operation)](left,right):return False
                left=right
            return True
        raise ValueError('Unsupported condition')
    def check(values):
        try:return bool(evaluate(tree.body,values))
        except (ValueError,KeyError,TypeError,ArithmeticError):return False
    return check
