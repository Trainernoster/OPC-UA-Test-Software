from dependencytree import dependencytree_Print

def main():
    testlist: list = [
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
    
    testnames: list = [
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
    
    dependencytree_Print(_tree= testlist, _object_names= testnames, _add_names= True, _names_only= True)

main()