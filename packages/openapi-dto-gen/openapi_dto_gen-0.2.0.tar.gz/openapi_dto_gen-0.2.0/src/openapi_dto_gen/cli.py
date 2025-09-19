"""Command-line interface for the OpenAPI to Java DTO generator.

This module contains a `main` function that can be invoked as a console
script to convert OpenAPI/Swagger specification files into Java data
transfer objects (DTOs). The implementation is adapted from a standalone
script, reorganized into a package-friendly module.
"""

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Set, List

import yaml  # type: ignore

# Java reserved words; if a generated class or field collides with one of
# these identifiers, an underscore is appended to avoid compilation errors.
RESERVED = {
    "abstract","assert","boolean","break","byte","case","catch","char","class","const",
    "continue","default","do","double","else","enum","extends","final","finally","float",
    "for","goto","if","implements","import","instanceof","int","interface","long","native",
    "new","package","private","protected","public","return","short","static","strictfp","super",
    "switch","synchronized","this","throw","throws","transient","try","void","volatile","while",
    "record","var","yield","sealed","permits","non-sealed"
}


def to_pascal_case(name: str) -> str:
    """Convert an arbitrary string into PascalCase and ensure it is a valid Java identifier."""
    name = re.sub(r'[^0-9A-Za-z]+', ' ', name)
    parts = [p for p in name.strip().split(' ') if p]
    s = ''.join(p[:1].upper() + p[1:] for p in parts) or "ClassName"
    if s[0].isdigit():
        s = "_" + s
    if s in RESERVED:
        s = s + "_"
    return s


def to_camel_case(name: str) -> str:
    """Convert an arbitrary string into camelCase for Java field names."""
    if not name:
        return "field"
    name = re.sub(r'[^0-9A-Za-z]+', ' ', name)
    parts = [p for p in name.strip().split(' ') if p]
    if not parts:
        return "field"
    s = parts[0].lower() + ''.join(p[:1].upper() + p[1:] for p in parts[1:])
    if s[0].isdigit():
        s = "_" + s
    if s in RESERVED:
        s = s + "_"
    return s


def sanitize_identifier(name: str) -> str:
    """Sanitize a string so it can be used as a Java identifier (e.g. enum constants)."""
    s = re.sub(r'[^0-9A-Za-z_]', '_', name or "field")
    if s[0].isdigit():
        s = "_" + s
    if s in RESERVED:
        s = s + "_"
    return s


def last_ref_name(ref: str) -> str:
    """Return the last segment of a JSON pointer (e.g. '#/components/schemas/User' → 'User')."""
    return ref.split('/')[-1]


def is_enum_schema(schema: Dict[str, Any]) -> bool:
    """Determine whether a schema defines an enum at the top level."""
    return bool(schema) and ("enum" in schema) and isinstance(schema.get("enum"), list)


def merge_allOf(schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten an `allOf` schema into a single object schema by merging properties and required fields."""
    allof_list = schema.get("allOf", [])
    combined: Dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    for part in allof_list:
        if "$ref" in part:
            ref_name = last_ref_name(part["$ref"])
            base = components.get(ref_name, {})
            base_expanded = expand_allOf(base, components)
            combined = merge_object_schemas(combined, base_expanded)
        else:
            part_expanded = expand_allOf(part, components)
            combined = merge_object_schemas(combined, part_expanded)
    # After merge, also merge any sibling properties alongside allOf
    sibling = {k: v for k, v in schema.items() if k != "allOf"}
    combined = merge_object_schemas(combined, sibling)
    return combined


def merge_object_schemas(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two object-like schemas, combining their properties and required fields."""
    out = dict(a)
    if b.get("type") == "object" or "properties" in b or "additionalProperties" in b:
        out.setdefault("type", "object")
        out.setdefault("properties", {})
        # merge properties
        out["properties"] = {**out["properties"], **b.get("properties", {})}
        # merge required (union)
        req_a = set(out.get("required", []) or [])
        req_b = set(b.get("required", []) or [])
        out["required"] = sorted(req_a | req_b)
        # merge additionalProperties
        if "additionalProperties" in b:
            out["additionalProperties"] = b["additionalProperties"]
    else:
        # if b is not object-like, overlay fields
        out = {**out, **b}
    return out


def expand_allOf(schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively expand any allOf composition in the provided schema."""
    if "allOf" in schema:
        return merge_allOf(schema, components)
    return schema


def map_primitive(schema: Dict[str, Any]) -> Tuple[str, Set[str], List[str]]:
    """Map a primitive OpenAPI schema to a Java type, its imports, and doc comments."""
    t = schema.get("type")
    fmt = schema.get("format")
    comments: List[str] = []

    # Enums at property-level → use String, document allowed values
    if is_enum_schema(schema):
        comments.append(f"Allowed values: {', '.join(map(str, schema['enum']))}")
        return ("String", set(), comments)

    if t == "string":
        if fmt == "date":
            return ("LocalDate", {"java.time.LocalDate"}, comments)
        if fmt == "date-time":
            return ("OffsetDateTime", {"java.time.OffsetDateTime"}, comments)
        if fmt in ("byte", "binary"):
            return ("byte[]", set(), comments)
        return ("String", set(), comments)

    if t == "integer":
        if fmt == "int64":
            return ("Long", set(), comments)
        # default to 32-bit
        return ("Integer", set(), comments)

    if t == "number":
        if fmt == "float":
            return ("Float", set(), comments)
        if fmt == "double":
            return ("Double", set(), comments)
        return ("BigDecimal", {"java.math.BigDecimal"}, comments)

    if t == "boolean":
        return ("Boolean", set(), comments)

    if t == "array":
        items = schema.get("items", {}) or {}
        inner, imps, comm = to_java_type(items)
        return (f"List<{inner}>", imps | {"java.util.List"}, comments + comm)

    if t == "object":
        addl = schema.get("additionalProperties", None)
        if addl is True or addl is None:
            # free-form
            return ("Map<String, Object>", {"java.util.Map"}, comments)
        if isinstance(addl, dict):
            inner, imps, comm = to_java_type(addl)
            return (f"Map<String, {inner}>", imps | {"java.util.Map"}, comments + comm)
        # explicit properties (will be handled by caller)
        return ("Map<String, Object>", {"java.util.Map"}, comments)

    # oneOf/anyOf → fallback to Object
    for k in ("oneOf", "anyOf"):
        if k in schema:
            options = []
            for opt in schema[k]:
                if "$ref" in opt:
                    options.append(last_ref_name(opt["$ref"]))
                else:
                    if "type" in opt:
                        options.append(opt["type"])
            if options:
                comments.append(f"{k} possible types: {', '.join(options)}")
            return ("Object", set(), comments)

    # $ref handled outside
    return ("Object", set(), comments)


def to_java_type(schema: Dict[str, Any]) -> Tuple[str, Set[str], List[str]]:
    """Determine the Java type for an OpenAPI schema, recursively resolving $ref."""
    if "$ref" in schema:
        return (to_pascal_case(last_ref_name(schema["$ref"])), set(), [])
    return map_primitive(schema)


def collect_top_level_enums(components: Dict[str, Any]) -> Dict[str, List[str]]:
    """Collect all top-level enum schemas under components.schemas."""
    enums: Dict[str, List[str]] = {}
    for name, sch in (components or {}).items():
        if is_enum_schema(sch):
            enums[name] = sch["enum"]
    return enums


def class_javadoc(description: str | None) -> str:
    """Create a Javadoc block for a class from its description."""
    if not description:
        return ""
    lines = description.strip().splitlines()
    body = "\n".join(f" * {ln}" for ln in lines)
    return f"/**\n{body}\n */\n"


def field_javadoc(description: str | None, extra_comments: List[str]) -> str:
    """Create a Javadoc block for a field from its description and extra notes."""
    notes: List[str] = []
    if description:
        notes.extend(description.strip().splitlines())
    notes.extend(extra_comments or [])
    if not notes:
        return ""
    body = "\n".join(f"     * {ln}" for ln in notes)
    return f"    /**\n{body}\n     */\n"


def generate_enum_java(name: str, values: List[Any], package: str) -> str:
    """Generate source code for a Java enum given its values."""
    cls_name = to_pascal_case(name)
    consts = []
    for v in values:
        if isinstance(v, str):
            c = sanitize_identifier(v.upper())
        else:
            c = "V_" + sanitize_identifier(str(v).upper())
        consts.append(c)
    constants = ",\n    ".join(consts)
    return f"""package {package};

public enum {cls_name} {{
    {constants};
}}
"""


def generate_class_java(
    name: str,
    schema: Dict[str, Any],
    package: str,
    use_lombok: bool,
) -> Tuple[str, Set[str]]:
    """Generate source code for a Java class based on the provided schema."""
    cls_name = to_pascal_case(name)
    imports: Set[str] = set()
    description = schema.get("description")
    props = (schema.get("properties") or {})

    # Determine type: if not object-like and no properties and no additionalProperties
    if schema.get("type") not in (None, "object") and not props and not schema.get("additionalProperties"):
        # nothing to emit for non-object top-levels
        return ("", set())

    # Collect fields
    fields_src: List[str] = []
    for raw_name, prop in props.items():
        java_name = to_camel_case(raw_name)
        jtype, imps, comments = to_java_type(prop or {})
        imports |= imps
        fdesc = prop.get("description")
        # nullable? prefer wrappers already; add note
        if prop.get("nullable") or prop.get("x-nullable"):
            comments.append("nullable")
        # Build field
        ann_json = f'    @JsonProperty("{raw_name}")\n'
        jdoc = field_javadoc(fdesc, comments)
        fields_src.append(
            f"{jdoc}{ann_json}    private {jtype} {java_name};"
        )

    # additionalProperties only object → map DTO
    addl = schema.get("additionalProperties")
    addl_block = ""
    if addl is True:
        imports.add("java.util.Map")
        addl_block = '    @JsonIgnore\n    private Map<String, Object> additionalProperties;\n'
    elif isinstance(addl, dict):
        jt, imps, _ = to_java_type(addl)
        imports |= imps | {"java.util.Map"}
        addl_block = f'    @JsonIgnore\n    private Map<String, {jt}> additionalProperties;\n'

    # imports
    base_imports = {"com.fasterxml.jackson.annotation.JsonInclude",
                    "com.fasterxml.jackson.annotation.JsonProperty",
                    "com.fasterxml.jackson.annotation.JsonIgnore"}
    imports |= base_imports

    lombok_imports: Set[str] = set()
    lombok_annotations = ""
    if use_lombok:
        lombok_imports = {
            "lombok.Data",
            "lombok.NoArgsConstructor",
            "lombok.AllArgsConstructor",
            "lombok.Builder"
        }
        lombok_annotations = "@Data\n@NoArgsConstructor\n@AllArgsConstructor\n@Builder\n"

    # Compose imports block
    imports_block = ""
    if imports or lombok_imports:
        all_imps = sorted(list(imports | lombok_imports))
        imports_block = "\n".join(f"import {imp};" for imp in all_imps) + "\n\n"

    # Compose class
    jdoc = class_javadoc(description)
    fields_str = "\n\n".join(fields_src + ([addl_block] if addl_block else []))

    src = f"""package {package};

{imports_block}{jdoc}@JsonInclude(JsonInclude.Include.NON_NULL)
{lombok_annotations}public class {cls_name} {{

{fields_str}
}}
"""
    return (src, imports)


def build_schema_for_class(raw_schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    """Expand any allOf composition for a top-level schema before generating code."""
    s = expand_allOf(raw_schema, components)
    # If $ref at top-level (rare), replace with referenced schema
    if "$ref" in s:
        ref_name = last_ref_name(s["$ref"])
        s = expand_allOf(components.get(ref_name, {}), components)
    return s


def generate_common_dto(common_fields: Dict[str, Set[str]], package: str) -> str:
    """Generate a CommonDTO class that contains the common fields with overloaded setters.

    Each field is declared as an Object and an overloaded setter is emitted for each
    distinct Java type encountered across the specifications. A generic getter is
    also provided. Lombok is intentionally not used on this class to avoid
    collisions between generated setters and overloaded methods.
    """
    class_name = "CommonDTO"
    # Always import the Jackson annotations used for DTOs
    imports = {
        "com.fasterxml.jackson.annotation.JsonInclude",
        "com.fasterxml.jackson.annotation.JsonProperty",
    }
    lines: List[str] = []
    # Field declarations and methods
    for raw_name, jtypes in sorted(common_fields.items()):
        camel_name = to_camel_case(raw_name)
        # Field declaration with JsonProperty annotation
        lines.append(f"    @JsonProperty(\"{raw_name}\")")
        lines.append(f"    private Object {camel_name};\n")
        # Overloaded setters for each distinct Java type
        for jtype in sorted(jtypes):
            # Method signature uses capitalised name for setter
            method_name = f"set{camel_name[:1].upper()}{camel_name[1:]}"
            lines.append(f"    public void {method_name}({jtype} {camel_name}) {{ this.{camel_name} = {camel_name}; }}")
        # Getter
        method_name = f"get{camel_name[:1].upper()}{camel_name[1:]}"
        lines.append(f"    public Object {method_name}() {{ return this.{camel_name}; }}\n")

    # Compose imports block
    imports_block = "\n".join(f"import {imp};" for imp in sorted(imports)) + "\n\n" if imports else ""
    fields_and_methods = "\n\n".join(lines)
    src = f"""package {package};

{imports_block}@JsonInclude(JsonInclude.Include.NON_NULL)
public class {class_name} {{

{fields_and_methods}
}}
"""
    return src


def main() -> None:
    """Entry point for the command-line interface."""
    ap = argparse.ArgumentParser(description="Generate Java DTOs from OpenAPI (Swagger) YAML/JSON.")
    ap.add_argument(
        "--in",
        dest="infile",
        required=True,
        help=(
            "Path to OpenAPI YAML/JSON. For multiple files, supply a comma-separated list."
        ),
    )
    ap.add_argument("--out", dest="outdir", required=True, help="Output directory for .java files")
    ap.add_argument("--package", dest="package", required=True, help="Java package, e.g. com.example.dto")
    ap.add_argument("--lombok", dest="lombok", action="store_true", help="Use Lombok annotations")
    args = ap.parse_args()

    # Split input files (comma-separated)
    in_paths = [p.strip() for p in args.infile.split(",") if p.strip()]
    if not in_paths:
        print("No input files provided.")
        return

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Track generated names to avoid duplicates when multiple specifications define the same schema
    generated_names: Set[str] = set()
    # List of all components for common field detection
    components_list: List[Dict[str, Any]] = []

    for in_path in in_paths:
        # Load OpenAPI spec
        with open(in_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        # Extract components.schemas
        components = ((spec or {}).get("components") or {}).get("schemas") or {}
        if not components:
            # Skip empty components but continue scanning others
            continue
        components_list.append(components)

        # Emit top-level enums
        enums = collect_top_level_enums(components)
        for name, values in enums.items():
            pascal_name = to_pascal_case(name)
            if pascal_name in generated_names:
                continue
            src_enum = generate_enum_java(name, values, args.package)
            (outdir / f"{pascal_name}.java").write_text(src_enum, encoding="utf-8")
            generated_names.add(pascal_name)

        # Emit classes
        for name, schema in components.items():
            if is_enum_schema(schema):
                continue  # enum already emitted
            pascal_name = to_pascal_case(name)
            if pascal_name in generated_names:
                continue
            cls_schema = build_schema_for_class(schema, components)
            src_class, _ = generate_class_java(name, cls_schema, args.package, args.lombok)
            if src_class.strip():
                (outdir / f"{pascal_name}.java").write_text(src_class, encoding="utf-8")
                generated_names.add(pascal_name)

    # After processing all specs, generate a common DTO if there are multiple specs
    if len(components_list) > 1:
        # Determine common fields across all schemas
        field_counts: Dict[str, int] = {}
        field_types: Dict[str, Set[str]] = {}
        for comps in components_list:
            for name, schema in comps.items():
                if is_enum_schema(schema):
                    continue
                # Expand allOf etc. to flatten inheritance
                cls_schema = build_schema_for_class(schema, comps)
                props = (cls_schema.get("properties") or {})
                for raw_name, prop in props.items():
                    field_counts[raw_name] = field_counts.get(raw_name, 0) + 1
                    jtype, _, _ = to_java_type(prop or {})
                    field_types.setdefault(raw_name, set()).add(jtype)
        # Build dictionary of common fields (appear in at least 2 specs)
        common_fields: Dict[str, Set[str]] = {
            raw_name: types
            for raw_name, count in field_counts.items()
            if count > 1
            for types in [field_types[raw_name]]
        }
        if common_fields:
            # Generate and write CommonDTO
            src_common = generate_common_dto(common_fields, args.package)
            (outdir / "CommonDTO.java").write_text(src_common, encoding="utf-8")

    print(f"Done. Wrote files to: {outdir}")


if __name__ == "__main__":
    main()