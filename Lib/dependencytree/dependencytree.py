""" 
Dependency Tree creates dependcy trees from a structured list and returns the tree visually in the command line.

Tree list rules: 
• First entery is the root and it is one dimmensional.
• The root can have many children.
• Every child can have additional children.
• A child is always one level higher compared to its parent
    • This hirachiy is described by the dimmension of the sublist
• The last child is mark by the following parent on the same level (the next object with on the same level).
• It is important, that only ids (int) are stored in the tree. All other possitions have to be "None".

Example tree list (_tree):
[
[85],
[None,     1001],
[None,     None,      1002],
[None,     None,      1003],
[None,     None,      1004],
[None,     1005],
[None,     None,      1006],
[None,     None,      1007],
[None,     None,      1008],
[None,     None,      None,       1009],
]

This tree creates the output

85
├─ 1001
|   ├─ 1002
|   ├─ 1003
|   └─ 1004
└─ 1005
    ├─ 1006
    ├─ 1007
    └─ 1008
        └─ 1009

The name list contains the ids combinded with the objcet name.
The name string can contain a name or a hole sentence.

• First entery is the id.
• Second entery the name.
• If an id is missing, the id from the _tree list gets the name.

Example name list (_object_names):
[
[85,        "root folder"],
[1001,      "sub folder1"],
[1002,      "sub sub folder2"],
[1003,      "sub sub folder3"],
[1004,      "sub sub folder4"],
[1005,      "sub folder2"],
[1006,      "sub sub folder5"],
[1007,      "sub sub folder6"],
[1008,      "sub sub folder7"],
[1009,      "sub sub sub folder1"],
]

"""

@staticmethod
def dependencytree_print(_tree: list = [], _object_names: list = [], _add_names: bool = False, _names_only: bool = False) -> int:
    """ Print tree function """
    
    """
        Attributes:             
            _tree               list    contains the tree shape, information about the heritage
            _objcet_names       list    contains the name for every object
            _add_names          bool    if True, prints the id and the name
            _names_only         bool    if True, prints only the name, overrieds _add_names

        Return value:
            int 
    """

    # Get the children list
    children = _get_all_children(_tree= _tree)

    # Print tree
    _print_tree(_tree= _tree, _children= children, _object_names= _object_names, _add_names= _add_names, _names_only= _names_only)
    return 1

@staticmethod
def _get_all_children (_tree) -> list:
        """ Find all "close" children """
    
        """
            Attributes:             
                _tree               list    contains the tree shape, information about the heritage
            
            Return value:
                children            list    list of close children 
        """
        n = len(_tree)
        result = []
        last_seen = []

        parents = []
        for row in _tree:
            while len(last_seen) < len(row):
                last_seen.append(None)
            # Update last_seen with non-None values
            for i, val in enumerate(row):
                if val is not None:
                    last_seen[i] = val
            # Parent is last_seen at previous depth
            parent = last_seen[len(row)-2] if len(row) > 1 else None
            parents.append(parent)

        # Collect children
        ids = [row[-1] for row in _tree]
        for idx, id_ in enumerate(ids):
            children = [j for j in range(idx+1, n) if parents[j] == id_]
            result.append([idx] + children)

        return result

@staticmethod
def _print_tree(_tree: list = [], _children: list = [], _object_names: list = [], _add_names: bool = False, _names_only: bool = False) -> int:
    """ Print the tree  """
    
    """
        Attributes:             
            _tree               list    contains the tree shape, information about the heritage
            _children           list    contains the infomration about the closesed children
            _objcet_names       list    contains the name for every object
            _add_names          bool    if True, prints the id and the name
            _names_only         bool    if True, prints only the name, overrieds _add_names

        Return value:
            int 
    """
    
    vertical = "│"
    branch_middle = "├"
    branch_last = "└"
    horizontal = "─"
    prefix=""

    ids = [row[-1] for row in _tree]
    names_lookup = {item[0]: item[1] for item in _object_names}

    def _print_node(_idx, _prefix_parts= []) -> None:
        """ Creates one node """
    
        """
            Attributes:             
                _idx                int     current node index
                _prefix_parts       list    contains the tree elements

            Return value:
                None 
        """
        node_id = ids[_idx]
        node_name = names_lookup.get(node_id, "")
        text = _create_object_print(_id= node_id, _name= node_name, _add_names= _add_names, _names_only= _names_only)

        prefix = ""
        for i, has_vertical in enumerate(_prefix_parts[:-1]):
            prefix += vertical + "   " if has_vertical else "    "

        if _prefix_parts:
            connector = branch_last + horizontal*1 if not _prefix_parts[-1] else branch_middle + horizontal*1
            prefix += connector

        print(prefix + text)

        children_idx = _children[_idx][1:]
        n = len(children_idx)
        for i, child in enumerate(children_idx):
            is_middle = (i != n - 1)
            _print_node(child, _prefix_parts + [is_middle])

    # Start printing
    _print_node(0)

@staticmethod
def _create_object_print(_id: int = 0, _name: str = None, _add_names: bool = False, _names_only: bool = False) -> str:
    """ Creates  """
    
    """
        Attributes:             
            _id                 int     contains the node id
            _name               str     contains the node name
            _add_names          bool    if True, prints the id and the name
            _names_only         bool    if True, prints only the name, overrieds _add_names

        Return value:
            printable text      str     text which should be printed at this node in the tree
    """
    if _names_only:
        return _name
    elif _add_names:
        return (str(_id) +  ", "+ _name)
    else:
        return str(_id)