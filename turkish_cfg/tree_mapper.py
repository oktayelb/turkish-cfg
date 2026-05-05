from __future__ import annotations

from lark import Tree, Token

from .parser import Derivation, ParseResult


class TreeMapper:
    def render(self, result: ParseResult) -> str:
        if not result.best:
            return "(no derivation)"
        return self.render_derivation(result.best, result.tokens)

    def render_derivation(self, derivation: Derivation, tokens: list[str]) -> str:
        leaf_idx = 0

        def build_ascii_tree(node: Tree | Token | str, prefix: str = "", is_last: bool = True) -> str:
            nonlocal leaf_idx
            
            branch = "└── " if is_last else "├── "
            pipe = "    " if is_last else "│   "
            
            res = ""
            if isinstance(node, Tree):
                # Print the non-terminal category (e.g., 'sentence', 'pre_verbal')
                res += f"{prefix}{branch}{node.data}\n"
                children = node.children
                for i, child in enumerate(children):
                    is_last_child = (i == len(children) - 1)
                    res += build_ascii_tree(child, prefix + pipe, is_last_child)
            else:
                # It's a terminal node (e.g., 'P1', 'VP')
                if leaf_idx < len(tokens):
                    surface = tokens[leaf_idx]
                    state = derivation.states[leaf_idx]
                    # Map the syntax node directly to the surface word
                    leaf_str = f"{node} ➔ {surface} (root: {state.root})"
                    leaf_idx += 1
                else:
                    leaf_str = str(node)
                    
                res += f"{prefix}{branch}{leaf_str}\n"
                
            return res

        # Build the root of the tree without a preceding branch
        tree_str = f"{derivation.tree.data}\n"
        children = derivation.tree.children
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            tree_str += build_ascii_tree(child, "", is_last_child)

        # Assemble the final formatted output
        lines = [
            "--- CFG DERIVATION TREE ---",
            tree_str.rstrip(),
            "",
            "--- MORPHOLOGICAL FEATURES ---"
        ]
        
        for surface, state in zip(tokens, derivation.states):
            raw = state.features.get("raw_savyar") or state.root
            lines.append(f"• {surface}: {state.category} (root={state.root}, raw={raw})")
            
        return "\n".join(lines)