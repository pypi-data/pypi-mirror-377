import os
import ast
import inspect
import textwrap


class Helper:
    
    @staticmethod
    def find_func_node_from_file(func):
        try:
            source_file = inspect.getsourcefile(func) or inspect.getfile(func)
        except (TypeError, OSError):
            return None
        
        if not source_file or not os.path.exists(source_file):
            return None
        
        with open(source_file, "r", encoding="utf-8") as f:
            src = f.read()
            
        try:
            mod = ast.parse(src)
        except SyntaxError:
            return None
        
        target_lineno = getattr(func, "__code__", None) and func.__code__.co_firstlineno
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
                if getattr(node, "lineno", None) == target_lineno:
                    return node
                
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
                return node
            
        return None


    @staticmethod
    def find_func_node_from_snippet(func):
        try:
            src_snip = inspect.getsource(func)
        except (OSError, TypeError, IOError):
            return None
        
        src_snip = textwrap.dedent(src_snip)
        try:
            mod = ast.parse(src_snip)
        except SyntaxError:
            return None
        
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
                return node
            
        return None


    @staticmethod
    def get_function_ast_node(func):
        node = Helper.find_func_node_from_file(func)
        if node is not None:
            return node
        
        return Helper.find_func_node_from_snippet(func)


    @staticmethod
    def is_ast_body_empty(node: ast.AST) -> bool:
        if not node or not hasattr(node, "body"):
            return False
        
        body = node.body
        if len(body) == 0:
            return True
        
        if len(body) == 1:
            stmt = body[0]
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                return True
            
        return False


    @staticmethod
    def is_empty_function(func) -> bool:
        node = Helper.get_function_ast_node(func)
        if node is not None:
            return Helper.is_ast_body_empty(node)
        
        code = getattr(func, "__code__", None)
        if code is None:
            return False
        
        co_names = getattr(code, "co_names", ())
        co_consts = getattr(code, "co_consts", ())
        if not co_names and (co_consts == (None,) or co_consts == (None,)):
            return True
        
        return False
