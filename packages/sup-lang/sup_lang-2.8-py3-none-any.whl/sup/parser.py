from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from . import ast as AST
from .errors import SupSyntaxError, nearest_phrase

TokenType = str


@dataclass
class Token:
    type: TokenType
    value: str | float | int | None
    line: int
    column: int


class Lexer:
    def __init__(self, source: str, lexicon: dict[str, list[str]]):
        # Normalize source: strip UTF-8 BOM if present; keep newlines for line numbers
        if source and source[:1] == "\ufeff":
            source = source.lstrip("\ufeff")
        self.source = source
        self.lines = source.splitlines()
        self.lexicon = self._prepare_lexicon(lexicon)
        self.max_phrase_len = max(len(k.split()) for k in self.lexicon.keys())

    def _prepare_lexicon(self, lex: dict[str, list[str]]) -> dict[str, str]:
        phrase_to_key: dict[str, str] = {}
        for key, syns in lex.items():
            for s in syns:
                phrase_to_key[s.lower()] = key
        # Add control phrases not guaranteed in lexicon
        defaults = {
            "and": "and",
            "from": "from",
            "by": "by_kw",
            "set": "set",
            "to": "to",
            "then": "then",
            "times": "times",
            "sup": "sup",
            "bye": "bye",
            "note": "note",
            # Builtin phrases (fallbacks if missing in lexicon file)
            "env get": "env_get",
            "join path": "join_path",
            "regex replace": "regex_replace",
            "regex match": "regex_match",
            "regex search": "regex_search",
            "glob": "glob",
            "json stringify": "json_stringify",
            "json parse": "json_parse",
            "read file": "read_file",
            "write file": "write_file",
        }
        for p, k in defaults.items():
            phrase_to_key.setdefault(p, k)
        return phrase_to_key

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        for line_idx, raw_line in enumerate(self.lines, start=1):
            line = raw_line.strip()
            if not line:
                continue
            llower = line.lower()
            if llower.startswith("note"):
                continue
            # Tokenize a line by consuming longest phrases
            i = 0
            while i < len(line):
                if line[i].isspace():
                    i += 1
                    continue
                # String literal
                if line[i] == '"':
                    j = i + 1
                    buf = []
                    while j < len(line):
                        ch = line[j]
                        if ch == "\\" and j + 1 < len(line):
                            buf.append(line[j + 1])
                            j += 2
                            continue
                        if ch == '"':
                            tokens.append(
                                Token("STRING", "".join(buf), line_idx, i + 1)
                            )
                            i = j + 1
                            break
                        buf.append(ch)
                        j += 1
                    else:
                        raise SupSyntaxError(
                            message="Unterminated string literal.",
                            line=line_idx,
                            column=i + 1,
                        )
                    continue
                # Comma
                if line[i] == ",":
                    tokens.append(Token("COMMA", None, line_idx, i + 1))
                    i += 1
                    continue
                # Number literal (allow unary minus)
                num_m = re.match(r"-?\d+(?:\.\d+)?", line[i:])
                if num_m:
                    num_txt = num_m.group(0)
                    value = float(num_txt) if "." in num_txt else int(num_txt)
                    tokens.append(Token("NUMBER", value, line_idx, i + 1))
                    i += len(num_txt)
                    continue
                # Identifier (allow dots for module access)
                ident_m = re.match(r"[A-Za-z_][A-Za-z0-9_\.]*", line[i:])
                if ident_m:
                    # Try to match multi-word phrases starting here
                    j = i
                    best: tuple[str, str] | None = None  # (phrase, key)
                    # Consider up to max_phrase_len words
                    words = line[i:]
                    for span_words in range(self.max_phrase_len, 0, -1):
                        # Build a phrase of span_words starting at i
                        phrase = self._take_words(words, span_words)
                        if not phrase:
                            continue
                        key = self.lexicon.get(phrase.lower())
                        if key:
                            best = (phrase, key)
                            break
                    if best:
                        phrase, key = best
                        ttype, tval = self._key_to_token(key)
                        tokens.append(Token(ttype, tval, line_idx, i + 1))
                        i += len(phrase)
                        continue
                    # Fallback: plain identifier
                    ident = ident_m.group(0)
                    tokens.append(Token("IDENT", ident, line_idx, i + 1))
                    i += len(ident)
                    continue
                # Unknown char
                raise SupSyntaxError(
                    message=f"Unexpected character '{line[i]}'.",
                    line=line_idx,
                    column=i + 1,
                )
            # End of line
            tokens.append(Token("NEWLINE", None, line_idx, len(line) + 1))
        tokens.append(Token("EOF", None, len(self.lines) + 1, 1))
        return tokens

    def _take_words(self, text: str, n: int) -> str | None:
        # Return the substring consisting of the first n words of text if there are at least n words
        m = re.match(r"(?:\s*)(\S+(?:\s+\S+){%d})" % (n - 1), text)
        return m.group(1) if m else None

    def _key_to_token(self, key: str) -> tuple[TokenType, str | None]:
        mapping = {
            "add": ("ADD", None),
            "subtract": ("SUB", None),
            "multiply": ("MUL", None),
            "divide": ("DIV", None),
            "print": ("PRINT", None),
            "result": ("RESULT", None),
            "if": ("IF", None),
            "endif": ("ENDIF", None),
            "else": ("ELSE", None),
            "repeat": ("REPEAT", None),
            "endrepeat": ("ENDREPEAT", None),
            "while": ("WHILE", None),
            "endwhile": ("ENDWHILE", None),
            "foreach": ("FOREACH", None),
            "endfor": ("ENDFOR", None),
            "is_greater": ("REL", ">"),
            "is_less": ("REL", "<"),
            "is_equal": ("REL", "=="),
            "is_not_equal": ("REL", "!="),
            "is_greater_equal": ("REL", ">="),
            "is_less_equal": ("REL", "<="),
            "and": ("AND", None),
            "or": ("OR", None),
            "not": ("NOT", None),
            "from": ("FROM", None),
            "by_kw": ("BY", None),
            "set": ("SET", None),
            "to": ("TO", None),
            "make": ("MAKE", None),
            "list": ("LIST", None),
            "map": ("MAP", None),
            "of": ("OF", None),
            "in": ("IN", None),
            "push": ("PUSH", None),
            "pop": ("POP", None),
            "get": ("GET", None),
            "delete": ("DELETE", None),
            "length_kw": ("LENGTH", None),
            "upper": ("UPPER", None),
            "lower": ("LOWER", None),
            "concat": ("CONCAT", None),
            "power": ("POWER", None),
            "sqrt": ("SQRT", None),
            "absolute": ("ABS", None),
            # Additional stdlib/builtins
            "min": ("MIN", None),
            "max": ("MAX", None),
            "floor": ("FLOOR", None),
            "ceil": ("CEIL", None),
            "trim": ("TRIM", None),
            "contains": ("CONTAINS", None),
            "join": ("JOIN", None),
            "now": ("NOW", None),
            "read_file": ("READ_FILE", None),
            "write_file": ("WRITE_FILE", None),
            "json_parse": ("JSON_PARSE", None),
            "json_stringify": ("JSON_STRINGIFY", None),
            # env/path/fs/regex/glob
            "env_get": ("ENV_GET", None),
            "env_set": ("ENV_SET", None),
            "cwd": ("CWD", None),
            "join_path": ("JOIN_PATH", None),
            "basename": ("BASENAME", None),
            "dirname": ("DIRNAME", None),
            "exists": ("EXISTS", None),
            "glob": ("GLOB", None),
            "regex_match": ("REGEX_MATCH", None),
            "regex_search": ("REGEX_SEARCH", None),
            "regex_replace": ("REGEX_REPLACE", None),
            # subprocess/csv/zip/sqlite
            "subprocess_run": ("SUBPROCESS_RUN", None),
            "csv_read": ("CSV_READ", None),
            "csv_write": ("CSV_WRITE", None),
            "zip_create": ("ZIP_CREATE", None),
            "zip_extract": ("ZIP_EXTRACT", None),
            "sqlite_exec": ("SQLITE_EXEC", None),
            "sqlite_query": ("SQLITE_QUERY", None),
            "define": ("DEFINE", None),
            "function": ("FUNCTION", None),
            "called": ("CALLED", None),
            "with": ("WITH", None),
            "return": ("RETURN", None),
            "endfunction": ("ENDFUNCTION", None),
            "call": ("CALL", None),
            "ask": ("ASK", None),
            "for": ("FOR", None),
            "the": ("THE", None),
            "then": ("THEN", None),
            "times": ("TIMES", None),
            "sup": ("SUP", None),
            "bye": ("BYE", None),
            "note": ("NOTE", None),
            # errors
            "try": ("TRY", None),
            "catch": ("CATCH", None),
            "finally": ("FINALLY", None),
            "end_try": ("ENDTRY", None),
            "throw": ("THROW", None),
            # imports
            "import": ("IMPORT", None),
            "as": ("AS", None),
        }
        return mapping.get(key, ("IDENT", key))


class Parser:
    def __init__(self) -> None:
        lex_path = os.environ.get(
            "SUP_LEXICON",
            os.path.join(os.path.dirname(__file__), "lexicon", "english.json"),
        )
        with open(lex_path, encoding="utf-8") as f:
            self.lexicon = json.load(f)

    def parse(self, source: str) -> AST.Program:
        lexer = Lexer(source, self.lexicon)
        self.tokens = lexer.tokenize()
        self.pos = 0
        prog = self.program()
        return prog

    # Token utilities
    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def match(self, *types: TokenType) -> Token | None:
        if self.peek().type in types:
            return self.advance()
        return None

    def expect(self, t: TokenType, message: str) -> Token:
        tok = self.peek()
        if tok.type != t:
            suggestion = None
            if t in {"ADD", "SUB", "MUL", "DIV", "PRINT", "IF", "REPEAT"}:
                # Suggest nearest phrase
                candidates = [
                    p
                    for p, key in Lexer("", self.lexicon)
                    ._prepare_lexicon(self.lexicon)
                    .items()
                    if self._key_to_type(key) == t
                ]
                suggestion = nearest_phrase(
                    tok.value if isinstance(tok.value, str) else tok.type, candidates
                )
            raise SupSyntaxError(
                message=message, line=tok.line, column=tok.column, suggestion=suggestion
            )
        return self.advance()

    def _key_to_type(self, key: str) -> TokenType:
        return Lexer("", self.lexicon)._key_to_token(key)[0]

    # Grammar
    def program(self) -> AST.Program:
        # program := 'sup' NL statements 'bye'
        # Allow 'sup' at first non-empty line
        self._skip_newlines()
        self.expect("SUP", "Program must start with 'sup'.")
        self._consume_newline("Expected newline after 'sup'.")
        statements = self.statements()
        # Expect 'bye' on its own line or after optional newlines
        self._skip_newlines()
        self.expect("BYE", "Program must end with 'bye'.")
        return AST.Program(statements=statements)

    def _skip_newlines(self) -> None:
        while self.match("NEWLINE"):
            pass

    def _consume_newline(self, msg: str) -> None:
        if not self.match("NEWLINE"):
            tok = self.peek()
            raise SupSyntaxError(message=msg, line=tok.line, column=tok.column)

    def statements(self) -> list[AST.Node]:
        stmts: list[AST.Node] = []
        while True:
            # Stop at EOF, BYE, ENDIF, ENDREPEAT, ENDFUNCTION, ENDWHILE, ENDFOR, ELSE (handled by if)
            if self.peek().type in {
                "EOF",
                "BYE",
                "ENDIF",
                "ENDREPEAT",
                "ENDFUNCTION",
                "ENDWHILE",
                "ENDFOR",
                "ELSE",
                "ENDTRY",
                "CATCH",
                "FINALLY",
            }:
                break
            if self.peek().type == "NEWLINE":
                self.advance()
                continue
            stmts.append(self.statement())
            # After each statement, consume optional NEWLINE
            if self.peek().type == "NEWLINE":
                self.advance()
        return stmts

    def statement(self) -> AST.Node:
        tok = self.peek()
        if tok.type == "SET":
            return self.assignment()
        if tok.type == "PRINT":
            return self.print_stmt()
        if tok.type == "IF":
            return self.if_block()
        if tok.type == "REPEAT":
            return self.repeat_block()
        if tok.type == "WHILE":
            return self.while_block()
        if tok.type == "FOREACH":
            return self.foreach_block()
        if tok.type == "ASK":
            return self.ask_stmt()
        if tok.type == "DEFINE":
            return self.func_def()
        if tok.type == "RETURN":
            return self.return_stmt()
        if tok.type == "CALL":
            return self.call_stmt()
        if tok.type == "TRY":
            return self.try_block()
        if tok.type == "THROW":
            return self.throw_stmt()
        if tok.type == "IMPORT":
            return self.import_stmt()
        if tok.type == "FROM":
            return self.from_import_stmt()
        # expr statement
        expr = self.expression()
        node = AST.ExprStmt(expr=expr)
        node.line = tok.line
        return node

    def assignment(self) -> AST.Assignment | AST.SetKey:
        start = self.expect("SET", "Expected 'set'.")
        # Map set form: set <key> to <value> in <target>
        if self.peek().type in {"STRING", "IDENT", "RESULT"}:
            key_tok = self.advance()
            if self.match("TO"):
                value_expr = self.expression()
                if self.match("IN"):
                    target_expr = self.value()
                    node2 = AST.SetKey(
                        key=self._token_to_value_node(key_tok),
                        value=value_expr,
                        target=target_expr,
                    )
                    node2.line = start.line
                    return node2
                else:
                    # Fall back to normal assignment where first token was IDENT
                    if key_tok.type in {"IDENT", "RESULT"}:
                        name_val = (
                            "result" if key_tok.type == "RESULT" else str(key_tok.value)
                        )
                        expr = value_expr
                        node = AST.Assignment(name=name_val, expr=expr)
                        node.line = start.line
                        return node
                    # If key was STRING and no 'in', it's invalid
                    raise SupSyntaxError(
                        message="Expected 'in' for map assignment.",
                        line=start.line,
                        column=None,
                    )
            else:
                # No 'to' -> treat as normal assignment requiring IDENT
                if key_tok.type != "IDENT":
                    raise SupSyntaxError(
                        message="Expected variable name after 'set'.",
                        line=key_tok.line,
                        column=key_tok.column,
                    )
                name_val = str(key_tok.value)
                self.expect("TO", "Expected 'to' in assignment.")
                expr = self.expression()
                node = AST.Assignment(name=name_val, expr=expr)
                node.line = start.line
                return node
        # Fallback
        # Allow 'result' as a special variable name
        if self.peek().type == "RESULT":
            _ = self.advance()
            name_val = "result"
        else:
            name_tok = self.expect("IDENT", "Expected variable name after 'set'.")
            name_val = str(name_tok.value)
        self.expect("TO", "Expected 'to' in assignment.")
        expr = self.expression()
        node = AST.Assignment(name=name_val, expr=expr)
        node.line = start.line
        return node

    def print_stmt(self) -> AST.Print:
        start = self.expect("PRINT", "Expected 'print'.")
        # Either 'the result' or 'result' or expression
        if self.match("THE"):
            if self.match("RESULT"):
                node = AST.Print(expr=None)
                node.line = start.line
                return node
            # 'the' IDENT/LIST/MAP
            if self.peek().type in {"IDENT", "LIST", "MAP"}:
                t = self.advance()
                name = (
                    "list"
                    if t.type == "LIST"
                    else ("map" if t.type == "MAP" else str(t.value))
                )
                node = AST.Print(expr=AST.Identifier(name=name))
                node.line = start.line
                return node
        if self.match("RESULT"):
            node = AST.Print(expr=None)
            node.line = start.line
            return node
        # else expression
        expr = self.expression()
        node = AST.Print(expr=expr)
        node.line = start.line
        return node

    def ask_stmt(self) -> AST.Ask:
        # Accept either ASK tokenization or 'ask for' via lexicon mapping
        start = self.expect("ASK", "Expected 'ask'.")
        self.expect("FOR", "Expected 'for' after 'ask'.")
        name_tok = self.expect("IDENT", "Expected identifier after 'ask for'.")
        node = AST.Ask(name=str(name_tok.value))
        node.line = start.line
        return node

    def if_block(self) -> AST.If:
        start = self.expect("IF", "Expected 'if'.")
        # Support both comparison and boolean expressions
        cond = self.bool_expr()
        # optional THEN
        if self.match("THEN"):
            pass
        self._consume_newline("Expected newline after condition.")
        body = self.statements()
        else_body: list[AST.Node] | None = None
        if self.match("ELSE"):
            self._consume_newline("Expected newline after 'else'.")
            else_body = self.statements()
        self.expect("ENDIF", "Expected 'end if'.")
        node = AST.If(cond=cond, body=body, else_body=else_body)
        node.line = start.line
        return node

    def while_block(self) -> AST.While:
        start = self.expect("WHILE", "Expected 'while'.")
        cond = self.bool_expr()
        self._consume_newline("Expected newline after while condition.")
        body = self.statements()
        self.expect("ENDWHILE", "Expected 'end while'.")
        node = AST.While(cond=cond, body=body)
        node.line = start.line
        return node

    def foreach_block(self) -> AST.ForEach:
        start = self.expect("FOREACH", "Expected 'for each'.")
        var_tok = self.expect("IDENT", "Expected loop variable after 'for each'.")
        self.expect("IN", "Expected 'in' after loop variable.")
        iterable = self.value()
        self._consume_newline("Expected newline after for each header.")
        body = self.statements()
        self.expect("ENDFOR", "Expected 'end for'.")
        node = AST.ForEach(var=str(var_tok.value), iterable=iterable, body=body)
        node.line = start.line
        return node

    # Boolean expressions with precedence: NOT > AND > OR, comparisons within
    def bool_expr(self) -> AST.Node:
        node = self.bool_term()
        while self.match("OR"):
            right = self.bool_term()
            node = AST.BoolBinary(op="or", left=node, right=right)
        return node

    def bool_term(self) -> AST.Node:
        node = self.bool_factor()
        while self.match("AND"):
            right = self.bool_factor()
            node = AST.BoolBinary(op="and", left=node, right=right)
        return node

    def bool_factor(self) -> AST.Node:
        if self.match("NOT"):
            expr = self.bool_factor()
            return AST.NotOp(expr=expr)
        # comparison: value REL value
        left = self.value()
        if self.peek().type == "REL":
            op_tok = self.advance()
            right = self.value()
            return AST.Compare(op=str(op_tok.value), left=left, right=right)
        return left

    def repeat_block(self) -> AST.Repeat:
        start = self.expect("REPEAT", "Expected 'repeat'.")
        count = self.value()
        self.expect("TIMES", "Expected 'times' after repeat count.")
        self._consume_newline("Expected newline after 'times'.")
        body = self.statements()
        self.expect("ENDREPEAT", "Expected 'end repeat'.")
        node = AST.Repeat(count_expr=count, body=body)
        node.line = start.line
        return node

    def func_def(self) -> AST.FunctionDef:
        start = self.expect("DEFINE", "Expected 'define'.")
        self.expect("FUNCTION", "Expected 'function'.")
        self.expect("CALLED", "Expected 'called'.")
        name_tok = self.expect("IDENT", "Expected function name.")
        params: list[str] = []
        if self.match("WITH"):
            first = self.expect("IDENT", "Expected parameter after 'with'.")
            params.append(str(first.value))
            while self.match("AND"):
                pt = self.expect("IDENT", "Expected parameter name after 'and'.")
                params.append(str(pt.value))
        self._consume_newline("Expected newline after function header.")
        body = self.statements()
        self.expect("ENDFUNCTION", "Expected 'end function'.")
        node = AST.FunctionDef(name=str(name_tok.value), params=params, body=body)
        node.line = start.line
        return node

    def return_stmt(self) -> AST.Return:
        start = self.expect("RETURN", "Expected 'return'.")
        # optional expression until newline/end
        if self.peek().type in {"NEWLINE", "EOF", "ENDIF", "ENDREPEAT", "ENDFUNCTION"}:
            expr = None
        else:
            expr = self.expression()
        node = AST.Return(expr=expr)
        node.line = start.line
        return node

    def call_stmt(self) -> AST.ExprStmt:
        call = self.call_expr()
        node = AST.ExprStmt(expr=call)
        node.line = getattr(call, "line", None)
        return node

    def try_block(self) -> AST.TryCatch:
        start = self.expect("TRY", "Expected 'try'.")
        self._consume_newline("Expected newline after 'try'.")
        body = self.statements()
        catch_name: str | None = None
        catch_body: list[AST.Node] | None = None
        finally_body: list[AST.Node] | None = None
        if self.match("CATCH"):
            if self.peek().type == "IDENT":
                catch_name = str(self.advance().value)
            self._consume_newline("Expected newline after 'catch'.")
            catch_body = self.statements()
        if self.match("FINALLY"):
            self._consume_newline("Expected newline after 'finally'.")
            finally_body = self.statements()
        self.expect("ENDTRY", "Expected 'end try'.")
        node = AST.TryCatch(
            body=body,
            catch_name=catch_name,
            catch_body=catch_body,
            finally_body=finally_body,
        )
        node.line = start.line
        return node

    def throw_stmt(self) -> AST.Throw:
        start = self.expect("THROW", "Expected 'throw'.")
        val = self.expression()
        node = AST.Throw(value=val)
        node.line = start.line
        return node

    def import_stmt(self) -> AST.Import:
        start = self.expect("IMPORT", "Expected 'import'.")
        mod_tok = self.expect("IDENT", "Expected module name.")
        alias: str | None = None
        if self.match("AS"):
            alias = str(self.expect("IDENT", "Expected alias.").value)
        node = AST.Import(module=str(mod_tok.value), alias=alias)
        node.line = start.line
        return node

    def from_import_stmt(self) -> AST.FromImport:
        start = self.expect("FROM", "Expected 'from'.")
        mod_tok = self.expect("IDENT", "Expected module name.")
        self.expect("IMPORT", "Expected 'import'.")
        names: list[tuple[str, str | None]] = []
        # name [as alias] {, name [as alias]}
        while True:
            name_tok = self.expect("IDENT", "Expected symbol name.")
            alias: str | None = None
            if self.match("AS"):
                alias = str(self.expect("IDENT", "Expected alias.").value)
            names.append((str(name_tok.value), alias))
            if not self.match("COMMA"):
                break
        node = AST.FromImport(module=str(mod_tok.value), names=names)
        node.line = start.line
        return node

    def expression(self) -> AST.Node:
        tok = self.peek()
        if tok.type in {"ADD", "SUB", "MUL", "DIV"}:
            if tok.type == "ADD":
                return self.add_expr()
            if tok.type == "SUB":
                return self.sub_expr()
            if tok.type == "MUL":
                return self.mul_expr()
            if tok.type == "DIV":
                return self.div_expr()
        if tok.type == "CALL":
            return self.call_expr()
        # Builtins and collections
        if tok.type == "MAKE":
            return self.make_expr()
        if tok.type in {
            "PUSH",
            "POP",
            "GET",
            "DELETE",
            "LENGTH",
            "UPPER",
            "LOWER",
            "CONCAT",
            "POWER",
            "SQRT",
            "ABS",
            "MIN",
            "MAX",
            "FLOOR",
            "CEIL",
            "TRIM",
            "NOW",
            "CONTAINS",
            "JOIN",
            "READ_FILE",
            "WRITE_FILE",
            "JSON_PARSE",
            "JSON_STRINGIFY",
            "ENV_GET",
            "ENV_SET",
            "CWD",
            "JOIN_PATH",
            "BASENAME",
            "DIRNAME",
            "EXISTS",
            "GLOB",
            "REGEX_MATCH",
            "REGEX_SEARCH",
            "REGEX_REPLACE",
            "SUBPROCESS_RUN",
            "CSV_READ",
            "CSV_WRITE",
            "ZIP_CREATE",
            "ZIP_EXTRACT",
            "SQLITE_EXEC",
            "SQLITE_QUERY",
        }:
            return self.collection_or_builtin()
        return self.value()

    def call_expr(self) -> AST.Call:
        start = self.expect("CALL", "Expected 'call'.")
        name_tok = self.expect("IDENT", "Expected function name to call.")
        args: list[AST.Node] = []
        if self.match("WITH"):
            args.append(self.expression())
            while self.match("AND"):
                args.append(self.expression())
        node = AST.Call(name=str(name_tok.value), args=args)
        node.line = start.line
        return node

    def make_expr(self) -> AST.Node:
        start = self.expect("MAKE", "Expected 'make'.")
        if self.match("LIST"):
            items: list[AST.Node] = []
            if self.match("OF"):
                # parse comma-separated values
                items.append(self.value())
                while self.match("COMMA"):
                    items.append(self.value())
            # else: allow empty list literal via just 'make list'
            node_list = AST.MakeList(items=items)
            node_list.line = start.line
            return node_list
        if self.match("MAP"):
            node_map = AST.MakeMap()
            node_map.line = start.line
            return node_map
        raise SupSyntaxError(
            message="Expected 'list' or 'map' after 'make'.",
            line=start.line,
            column=start.column,
        )

    def collection_or_builtin(self) -> AST.Node:
        tok = self.peek()
        if tok.type == "PUSH":
            start = self.advance()
            item = self.value()
            self.expect("TO", "Expected 'to' after value in 'push'.")
            target = self.value()
            n_push: AST.Node = AST.Push(item=item, target=target)
            n_push.line = start.line
            return n_push
        if tok.type == "POP":
            start = self.advance()
            if self.match("FROM"):
                target = self.value()
            else:
                target = self.value()
            n_pop: AST.Node = AST.Pop(target=target)
            n_pop.line = start.line
            return n_pop
        if tok.type == "GET":
            start = self.advance()
            key = self.value()
            self.expect("FROM", "Expected 'from' after key in 'get'.")
            target = self.value()
            n2: AST.Node = AST.GetKey(key=key, target=target)
            n2.line = start.line
            return n2
        if tok.type == "DELETE":
            start = self.advance()
            key = self.value()
            self.expect("FROM", "Expected 'from' after key in 'delete'.")
            target = self.value()
            n3: AST.Node = AST.DeleteKey(key=key, target=target)
            n3.line = start.line
            return n3
        if tok.type == "LENGTH":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'length'.")
            # allow nested expressions such as 'length of join of "," and list'
            target = self.expression()
            n4: AST.Node = AST.Length(target=target)
            n4.line = start.line
            return n4
        # Builtin string/math operations with 'of' and/or binary forms
        # Unary/zero-arg builtins
        if tok.type in {
            "UPPER",
            "LOWER",
            "SQRT",
            "ABS",
            "FLOOR",
            "CEIL",
            "TRIM",
            "NOW",
        }:
            start = self.advance()
            name = tok.type.lower()
            args: list[AST.Node] = []
            if tok.type != "NOW":
                self.expect("OF", f"Expected 'of' after '{name}'.")
                args.append(self.value())
            node = AST.BuiltinCall(name=name, args=args)
            node.line = start.line
            return node
        if tok.type == "CONCAT":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'concat'.")
            a = self.expression()
            self.expect("AND", "Expected 'and' in concat.")
            b = self.expression()
            node = AST.BuiltinCall(name="concat", args=[a, b])
            node.line = start.line
            return node
        # Binary builtins
        if tok.type in {"POWER", "MIN", "MAX", "CONTAINS"}:
            start = self.advance()
            self.expect("OF", f"Expected 'of' after '{tok.type.lower()}'.")
            a = self.expression()
            self.expect("AND", "Expected 'and' in binary builtin.")
            b = self.expression()
            name = (
                "power"
                if tok.type == "POWER"
                else (
                    "min"
                    if tok.type == "MIN"
                    else ("max" if tok.type == "MAX" else "contains")
                )
            )
            n5: AST.Node = AST.BuiltinCall(name=name, args=[a, b])
            n5.line = start.line
            return n5
        if tok.type == "JOIN":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'join'.")
            sep = self.value()
            self.expect("AND", "Expected 'and' in join.")
            lst = self.value()
            n6: AST.Node = AST.BuiltinCall(name="join", args=[sep, lst])
            n6.line = start.line
            return n6
        if tok.type == "JOIN_PATH":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'join path'.")
            a = self.value()
            self.expect("AND", "Expected 'and' in join path.")
            b = self.value()
            n7: AST.Node = AST.BuiltinCall(name="join_path", args=[a, b])
            n7.line = start.line
            return n7
        if tok.type == "READ_FILE":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'read file'.")
            path = self.value()
            n8: AST.Node = AST.BuiltinCall(name="read_file", args=[path])
            n8.line = start.line
            return n8
        if tok.type == "WRITE_FILE":
            start = self.advance()
            # Support both 'write file of <path> and <data>' and 'write file <path> and <data>'
            if self.peek().type == "OF":
                self.advance()
            path = self.value()
            self.expect("AND", "Expected 'and' in write file.")
            data = self.value()
            n9: AST.Node = AST.BuiltinCall(name="write_file", args=[path, data])
            n9.line = start.line
            return n9
        if tok.type == "JSON_PARSE":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'json parse'.")
            s = self.expression()
            n10: AST.Node = AST.BuiltinCall(name="json_parse", args=[s])
            n10.line = start.line
            return n10
        if tok.type == "JSON_STRINGIFY":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'json stringify'.")
            v = self.expression()
            n11: AST.Node = AST.BuiltinCall(name="json_stringify", args=[v])
            n11.line = start.line
            return n11
        if tok.type == "ENV_GET":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'env get'.")
            k = self.value()
            n12: AST.Node = AST.BuiltinCall(name="env_get", args=[k])
            n12.line = start.line
            return n12
        if tok.type == "CWD":
            start = self.advance()
            n13: AST.Node = AST.BuiltinCall(name="cwd", args=[])
            n13.line = start.line
            return n13
        if tok.type == "BASENAME":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'basename'.")
            p = self.value()
            n14: AST.Node = AST.BuiltinCall(name="basename", args=[p])
            n14.line = start.line
            return n14
        if tok.type == "DIRNAME":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'dirname'.")
            p = self.value()
            n15: AST.Node = AST.BuiltinCall(name="dirname", args=[p])
            n15.line = start.line
            return n15
        if tok.type == "EXISTS":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'exists'.")
            p = self.expression()
            n16: AST.Node = AST.BuiltinCall(name="exists", args=[p])
            n16.line = start.line
            return n16
        if tok.type == "GLOB":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'glob'.")
            pattern = self.value()
            n17: AST.Node = AST.BuiltinCall(name="glob", args=[pattern])
            n17.line = start.line
            return n17
        if tok.type == "REGEX_REPLACE":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'regex replace'.")
            pat = self.expression()
            self.expect("AND", "Expected 'and' in regex replace.")
            text = self.expression()
            self.expect("AND", "Expected second 'and' in regex replace.")
            repl = self.expression()
            n18: AST.Node = AST.BuiltinCall(
                name="regex_replace", args=[pat, text, repl]
            )
            n18.line = start.line
            return n18
        if tok.type == "SUBPROCESS_RUN":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'subprocess run'.")
            cmd = self.value()
            args = [cmd]
            if self.match("AND"):
                args.append(self.value())
            n19: AST.Node = AST.BuiltinCall(name="subprocess_run", args=args)
            n19.line = start.line
            return n19
        if tok.type == "CSV_READ":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'csv read'.")
            p = self.expression()
            n20: AST.Node = AST.BuiltinCall(name="csv_read", args=[p])
            n20.line = start.line
            return n20
        if tok.type == "CSV_WRITE":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'csv write'.")
            p = self.expression()
            self.expect("AND", "Expected 'and' in csv write.")
            rows = self.expression()
            n21: AST.Node = AST.BuiltinCall(name="csv_write", args=[p, rows])
            n21.line = start.line
            return n21
        if tok.type == "ZIP_CREATE":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'zip create'.")
            zp = self.expression()
            self.expect("AND", "Expected 'and' in zip create.")
            files = self.expression()
            n22: AST.Node = AST.BuiltinCall(name="zip_create", args=[zp, files])
            n22.line = start.line
            return n22
        if tok.type == "ZIP_EXTRACT":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'zip extract'.")
            zp = self.value()
            self.expect("AND", "Expected 'and' in zip extract.")
            out = self.value()
            n23: AST.Node = AST.BuiltinCall(name="zip_extract", args=[zp, out])
            n23.line = start.line
            return n23
        if tok.type == "SQLITE_EXEC":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'sqlite exec'.")
            db = self.value()
            self.expect("AND", "Expected 'and' in sqlite exec.")
            sql = self.value()
            args = [db, sql]
            if self.match("AND"):
                args.append(self.expression())
            n24: AST.Node = AST.BuiltinCall(name="sqlite_exec", args=args)
            n24.line = start.line
            return n24
        if tok.type == "SQLITE_QUERY":
            start = self.advance()
            self.expect("OF", "Expected 'of' after 'sqlite query'.")
            db = self.value()
            self.expect("AND", "Expected 'and' in sqlite query.")
            sql = self.value()
            args = [db, sql]
            if self.match("AND"):
                args.append(self.expression())
            n25: AST.Node = AST.BuiltinCall(name="sqlite_query", args=args)
            n25.line = start.line
            return n25
        # No more builtins
        raise SupSyntaxError(message="Unsupported builtin or collection operation.")

    def add_expr(self) -> AST.Binary:
        start = self.expect("ADD", "Expected 'add'.")
        left = self.value()
        self.expect("AND", "Expected 'and' in addition.")
        right = self.value()
        node = AST.Binary(op="+", left=left, right=right)
        node.line = start.line
        return node

    def sub_expr(self) -> AST.Binary:
        start = self.expect("SUB", "Expected 'subtract'.")
        first = self.value()
        if self.match("AND"):
            second = self.value()
            left, right = first, second
        else:
            self.expect("FROM", "Expected 'and' or 'from' in subtraction.")
            second = self.value()
            # 'subtract A from B' => B - A
            left, right = second, first
        node = AST.Binary(op="-", left=left, right=right)
        node.line = start.line
        return node

    def mul_expr(self) -> AST.Binary:
        start = self.expect("MUL", "Expected 'multiply'.")
        left = self.value()
        self.expect("AND", "Expected 'and' in multiplication.")
        right = self.value()
        node = AST.Binary(op="*", left=left, right=right)
        node.line = start.line
        return node

    def div_expr(self) -> AST.Binary:
        start = self.expect("DIV", "Expected 'divide'.")
        left = self.value()
        self.expect("BY", "Expected 'by' in division.")
        right = self.value()
        node = AST.Binary(op="/", left=left, right=right)
        node.line = start.line
        return node

    def condition(self) -> tuple[AST.Node, str, AST.Node]:
        left = self.value()
        rel = self.expect("REL", "Expected relational operator.")
        right = self.value()
        return (left, str(rel.value), right)

    def value(self) -> AST.Node:
        tok = self.peek()
        if tok.type == "NUMBER":
            t = self.advance()
            num_node = AST.Number(value=t.value)  # type: ignore[arg-type]
            num_node.line = t.line
            return num_node
        if tok.type == "STRING":
            t = self.advance()
            str_node = AST.String(value=str(t.value))
            str_node.line = t.line
            return str_node
        if tok.type == "RESULT":
            t = self.advance()
            res_ident = AST.Identifier(name="result")
            res_ident.line = t.line
            return res_ident
        if tok.type in {"LIST", "MAP"}:
            t = self.advance()
            lm_ident = AST.Identifier(name=("list" if t.type == "LIST" else "map"))
            lm_ident.line = t.line
            return lm_ident
        if tok.type == "IDENT":
            t = self.advance()
            ident_node = AST.Identifier(name=str(t.value))
            ident_node.line = t.line
            return ident_node
        # Allow function calls as values
        if tok.type == "CALL":
            return self.call_expr()
        # Nested expression allowed
        if tok.type in {"ADD", "SUB", "MUL", "DIV"}:
            return self.expression()
        raise SupSyntaxError(
            message="Expected a value (number, variable, or expression).",
            line=tok.line,
            column=tok.column,
        )

    def _token_to_value_node(self, tok: Token) -> AST.Node:
        if tok.type == "STRING":
            str_node = AST.String(value=str(tok.value))
            str_node.line = tok.line
            return str_node
        if tok.type == "IDENT":
            ident_node = AST.Identifier(name=str(tok.value))
            ident_node.line = tok.line
            return ident_node
        raise SupSyntaxError(
            message="Invalid key token.", line=tok.line, column=tok.column
        )
