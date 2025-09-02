# """Generate the code reference pages."""


# from pathlib import Path
# from time import sleep

# import mkdocs_gen_files

# root = Path(__file__).parent.parent.parent
# src = root / "src"  # (1)!

# for path in src.rglob("*.py"):  # (2)!
#     module_path = path.relative_to(src).with_suffix(suffix="")  # (3)!
#     doc_path = path.relative_to(src).with_suffix(".md")  # (4)!
#     full_doc_path = Path("reference", doc_path)  # (5)!
#     parts = tuple(module_path.parts)
#     if parts[-1] == "__init__":  # (6)!
#         parts = parts[:-1]
        
#     # print(parts) 

#     with mkdocs_gen_files.open(full_doc_path, "w") as fd:  # (7)!
#         identifier = ".".join(parts)  # (8)!
#         print("::: " + identifier, file=fd)  # (9)!
#         print(
# """    
#     handler: python
#     options:
#       members: true
#       docstring_style: google
#       show_source: true
#       show_root_heading: true
#       show_root_full_path: false
#       show_submodules: false          
#       merge_init_into_class: true
#       members_order: source
#       show_inheritance_diagram: true
#       filters:
#         - "!^_"                      
#         - "!^__" """, file=fd
#         ) 
#         mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))  # (10)!
