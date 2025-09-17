from pathlib import Path
from collections import defaultdict
import json
import hashlib
import os


class GraphPipeline:
    def __init__(self, root_folder: str):
        self.root_folder = Path(root_folder)
        self.result = {}
        self.graph = defaultdict(list)
        self.nodes = {}

    def add_node(self, cls, dependencies=None):
        name = cls.__class__.__name__
        identity = hex(id(cls))
        self.nodes[identity] = cls
        if dependencies:
            for dep in dependencies:
                dependent_identity = hex(id(dep))
                dep_name = dependent_identity if isinstance(dep, type) else dep
                self.graph[dep_name].append(name)
        else:
            self.graph[identity] = self.graph.get(identity, [])

    def execute(self):
        pdf_files = list(self.root_folder.rglob("*.pdf"))

        for pdf_file in pdf_files:
            print(pdf_file)
            final_result = []
            for name, step in self.nodes.items():
                if name in self.graph.keys():
                    hash_ = self.compute_hash(step)
                    path = Path(pdf_file.parent / hash_)
                    path.mkdir(parents=True, exist_ok=True)
                    file_path = path / Path(pdf_file.name).with_suffix(".md")

                    if file_path.exists():
                        print("     Filepath exist, reading the md file")
                        result = file_path.read_text(encoding="utf-8")
                    else:
                        print("     Filepath does not exist, running the step")
                        result = step(pdf_file)
                        file_path.write_text(result, encoding="utf-8")

                        json_parameter = file_path.parent / "parameter.json"
                        attrs = {k: v for k, v in step.__dict__.items() if not k.startswith("_")}
                        json_parameter.write_text(json.dumps(attrs, indent=2), encoding="utf-8")
                else:
                    hash_ = self.compute_hash(step)
                    if step.name:
                        name = step.name
                    else:
                        name = ""
                    path = Path(file_path.parent / (name + "_" + hash_))
                    file_path_result = path / "result.json"
                    json_parameter = file_path_result.parent / "parameter.json"


                    if not file_path_result.exists():
                        print("     Filepath does not exist, running the step")
                        text = file_path.read_text(encoding="utf-8")
                        path.mkdir(parents=True, exist_ok=True)
                        result = step(text)
                        file_path_result.write_text(result, encoding="utf-8")
                        print(hash_)
                        attrs = {k: v for k, v in step.__dict__.items() if not k.startswith("_") and k != "client" and k[0] != "_" and k != "provider"}
                        # 🔑 Make it JSON-safe
                        serializable_attrs = self._make_serializable(attrs)
                        json_parameter.write_text(
                            json.dumps(serializable_attrs, indent=2, sort_keys=True, ensure_ascii=True),
                            encoding="utf-8"
                            )
                    else:
                        print("     Folder exist, reading the result")
                        result = file_path_result.read_text(encoding="utf-8")

                final_result.append(result)

            self.result[pdf_file] = final_result

    # ---------------------------
    # 🔑 Stable hashing utilities
    # ---------------------------

    @staticmethod
    def _make_serializable(obj):
        """Convert objects into a JSON-stable representation."""
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple, set)):
            return [GraphPipeline._make_serializable(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: GraphPipeline._make_serializable(v) for k, v in sorted(obj.items())}
        elif hasattr(obj, "__dict__"):
            # For custom objects, serialize their __dict__
            return GraphPipeline._make_serializable(vars(obj))
        else:
            # Fallback: type name + repr ensures stability across runs
            return f"{type(obj).__name__}:{repr(obj)}"

    @staticmethod
    def compute_hash(cls) -> str:
        """Compute a stable hash of a step instance across runs."""
        attrs = {
            k: v
            for k, v in cls.__dict__.items()
            if k != "hash" and not k.startswith("_") and k != "client" and k != "provider"
        }
        serializable_attrs = GraphPipeline._make_serializable(attrs)
        attrs_str = json.dumps(serializable_attrs, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(attrs_str.encode()).hexdigest()[:8]
