from __future__ import annotations

from loxygen import nodes
from loxygen.environment import Environment
from loxygen.exceptions import LoxRunTimeError
from loxygen.runtime import Callable
from loxygen.runtime import Clock
from loxygen.runtime import LoxClass
from loxygen.runtime import LoxFunction
from loxygen.runtime import LoxInstance
from loxygen.runtime import Return
from loxygen.token import Token
from loxygen.token import TokenType


class Interpreter(nodes.Visitor):
    def __init__(self):
        self.globals = Environment()
        self.globals.define("clock", Clock())
        self.locals = {}

        self.env = self.globals

    def visit_literal_expr(self, expression: nodes.Literal):
        return expression.value

    def visit_logical_expr(self, expression: nodes.Logical):
        left = self.evaluate(expression.left)
        if expression.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expression.right)

    def visit_set_expr(self, expression: nodes.Set):
        object = self.evaluate(expression.object)
        if not isinstance(object, LoxInstance):
            raise LoxRunTimeError(expression.name, "Only instances have fields.")

        value = self.evaluate(expression.value)
        object.set(expression.name, value)

        return value

    def visit_super_expr(self, expression: nodes.Super):
        distance = self.locals.get(expression)
        superclass = self.env.get_at(distance, "super")
        object = self.env.get_at(distance - 1, "this")
        method = superclass.find_method(expression.method.lexeme)
        if method is None:
            raise LoxRunTimeError(
                expression.method,
                f"Undefined property '{expression.method.lexeme}'.",
            )

        return method.bind(object)

    def visit_this_expr(self, expression: nodes.This):
        return self.look_up_variable(expression.keyword, expression)

    def visit_unary_expr(self, expression: nodes.Unary):
        right = self.evaluate(expression.right)
        match expression.operator.type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expression.operator, right)
                return -right

    @staticmethod
    def check_number_operand(operator, operand):
        if not isinstance(operand, float):
            raise LoxRunTimeError(operator, "Operand must be a number.")

    def visit_variable_expr(self, expression: nodes.Variable):
        return self.look_up_variable(expression.name, expression)

    def look_up_variable(self, name: Token, expression: nodes.Expr):
        distance = self.locals.get(expression)
        if distance is not None:
            return self.env.get_at(distance, name.lexeme)
        return self.globals.get(name)

    def visit_binary_expr(self, expression: nodes.Binary):
        left = self.evaluate(expression.left)
        right = self.evaluate(expression.right)

        match expression.operator.type:
            case TokenType.GREATER:
                self.check_number_operands(expression.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(expression.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expression.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                self.check_number_operands(expression.operator, left, right)
                return left - right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise LoxRunTimeError(
                    expression.operator,
                    "Operands must be two numbers or two strings.",
                )
            case TokenType.SLASH:
                self.check_number_operands(expression.operator, left, right)
                return left / right if right else float("nan")
            case TokenType.STAR:
                self.check_number_operands(expression.operator, left, right)
                return left * right
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

        return None

    @staticmethod
    def check_number_operands(operator, left, right):
        if not isinstance(left, float) or not isinstance(right, float):
            raise LoxRunTimeError(operator, "Operands must be numbers.")

    def visit_call_expr(self, expression: nodes.Call):
        callee = self.evaluate(expression.callee)
        arguments = [self.evaluate(argument) for argument in expression.arguments]

        if not isinstance(callee, Callable):
            raise LoxRunTimeError(
                expression.paren,
                "Can only call functions and classes.",
            )

        if (nb_args := len(arguments)) != (arity := callee.arity()):
            raise LoxRunTimeError(
                expression.paren,
                f"Expected {arity} arguments but got {nb_args}.",
            )

        return callee.call(self, arguments)

    def visit_get_expr(self, expression: nodes.Get):
        object = self.evaluate(expression.object)
        if isinstance(object, LoxInstance):
            return object.get(expression.name)

        raise LoxRunTimeError(expression.name, "Only instances have properties.")

    def visit_grouping_expr(self, expression: nodes.Grouping):
        return self.evaluate(expression.expression)

    @staticmethod
    def is_truthy(obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    @staticmethod
    def is_equal(obj1, obj2):
        if isinstance(obj1, float) and isinstance(obj2, bool):
            return False
        if isinstance(obj1, bool) and isinstance(obj2, float):
            return False

        return obj1 == obj2

    def evaluate(self, expression: nodes.Expr):
        return expression.accept(self)

    def execute(self, statement: nodes.Stmt):
        statement.accept(self)

    def resolve(self, expression: nodes.Expr, depth: int):
        self.locals[expression] = depth

    def execute_block(self, statements, environment):
        enclosing = self.env
        try:
            self.env = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.env = enclosing

    def visit_block_stmt(self, stmt: nodes.Block):
        self.execute_block(stmt.statements, Environment(self.env))

    def visit_class_stmt(self, stmt: nodes.Class):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRunTimeError(
                    stmt.superclass.name,
                    "Superclass must be a class.",
                )

        self.env.define(stmt.name.lexeme, None)
        if stmt.superclass is not None:
            self.env = Environment(self.env)
            self.env.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            is_initializer = method.name.lexeme == "init"
            function = LoxFunction(method, self.env, is_initializer)
            methods[method.name.lexeme] = function
        cls = LoxClass(stmt.name.lexeme, superclass, methods)

        if stmt.superclass is not None:
            self.env = self.env.enclosing

        self.env.assign(stmt.name, cls)

    def visit_expression_stmt(self, stmt: nodes.Expression) -> None:
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: nodes.Function) -> None:
        function = LoxFunction(stmt, self.env, False)
        self.env.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: nodes.If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: nodes.Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt: nodes.Return) -> None:
        if (value := stmt.value) is not None:
            value = self.evaluate(stmt.value)

        raise Return(value)

    def visit_var_stmt(self, stmt: nodes.Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.env.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: nodes.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    def visit_assign_expr(self, expression: nodes.Assign):
        value = self.evaluate(expression.value)
        distance = self.locals.get(expression)
        if distance is not None:
            self.env.assign_at(distance, expression.name, value)
        else:
            self.globals.assign(expression.name, value)

        return value

    def interpret(self, *statements: nodes.Stmt):
        for statement in statements:
            self.execute(statement)

    def stringify(self, obj):
        if obj is None:
            return "nil"
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, float) and (repr := str(obj)).endswith(".0"):
            return repr[:-2]

        return str(obj)
