from __future__ import annotations
import ast
from pathlib import Path
from typing import Any


def _py_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*.py") if "__pycache__" not in p.parts)


def _module_name(root: Path, file: Path) -> str:
    rel = file.relative_to(root.parent).with_suffix("")
    return ".".join(rel.parts)


def analyze_python_tree(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    root = path if path.is_dir() else path.parent
    files = _py_files(path)
    modules = {_module_name(root, f): f for f in files}
    short_to_full = {m.split(".")[-1]: m for m in modules}
    metrics=[]
    edges=set()
    legacy_imports=[]
    for module, file in modules.items():
        text=file.read_text(encoding="utf-8")
        tree=ast.parse(text)
        loc=sum(1 for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#"))
        funcs=sum(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) for n in ast.walk(tree))
        classes=sum(isinstance(n,ast.ClassDef) for n in ast.walk(tree))
        for n in ast.walk(tree):
            names=[]
            if isinstance(n,ast.Import): names=[a.name for a in n.names]
            elif isinstance(n,ast.ImportFrom):
                if n.module: names=[n.module]
            for name in names:
                if name.startswith("legacy_app"):
                    legacy_imports.append({"module":module,"import":name})
                target=None
                if name in modules: target=name
                else:
                    last=name.split(".")[-1]
                    target=short_to_full.get(last)
                if target and target != module: edges.add((module,target))
        metrics.append({"module":module,"file":str(file).replace("\\","/"),"loc":loc,"functions":funcs,"classes":classes})
    graph={m:set() for m in modules}
    for a,b in edges: graph.setdefault(a,set()).add(b)
    cycles=[]
    def walk(start,node,path_stack):
        for nxt in graph.get(node,set()):
            if nxt==start:
                cycle=path_stack+[nxt]
                normalized=tuple(cycle[:-1])
                if normalized and not any(set(normalized)==set(c) for c in cycles): cycles.append(list(normalized))
            elif nxt not in path_stack:
                walk(start,nxt,path_stack+[nxt])
    for m in graph: walk(m,m,[m])
    largest=max((x["loc"] for x in metrics),default=0)
    return {"module_count":len(metrics),"largest_module_loc":largest,"total_loc":sum(x["loc"] for x in metrics),"function_count":sum(x["functions"] for x in metrics),"class_count":sum(x["classes"] for x in metrics),"dependency_edges":len(edges),"circular_dependencies":cycles,"legacy_imports":legacy_imports,"modules":metrics}


def compare_architecture() -> dict[str, Any]:
    before=analyze_python_tree("legacy_app/billing/monolith.py")
    after=analyze_python_tree("modern_app/billing")
    return {"before":before,"after":after,"checks":{"modern_has_no_legacy_imports":not after["legacy_imports"],"modern_has_no_cycles":not after["circular_dependencies"],"largest_module_reduced":after["largest_module_loc"] < before["largest_module_loc"]}}


def render_architecture_markdown(result: dict[str, Any]) -> str:
    b,a=result["before"],result["after"]
    return f"""# Structural Modernization Evidence

| Metric | Before | After |
|---|---:|---:|
| Python modules | {b['module_count']} | {a['module_count']} |
| Largest module LOC | {b['largest_module_loc']} | {a['largest_module_loc']} |
| Total non-comment LOC | {b['total_loc']} | {a['total_loc']} |
| Functions | {b['function_count']} | {a['function_count']} |
| Classes | {b['class_count']} | {a['class_count']} |
| Dependency edges | {b['dependency_edges']} | {a['dependency_edges']} |
| Circular dependencies | {len(b['circular_dependencies'])} | {len(a['circular_dependencies'])} |
| Modern imports from legacy | — | {len(a['legacy_imports'])} |

## Structural checks

- Modern application has no imports from `legacy_app`: **{'PASS' if result['checks']['modern_has_no_legacy_imports'] else 'FAIL'}**
- Modern application has no internal dependency cycles detected by Aegis: **{'PASS' if result['checks']['modern_has_no_cycles'] else 'FAIL'}**
- Largest module is smaller than the legacy monolith: **{'PASS' if result['checks']['largest_module_reduced'] else 'FAIL'}**

These are descriptive structural metrics, not a subjective architecture score.
"""
