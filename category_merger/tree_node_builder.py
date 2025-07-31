from collections import defaultdict
from category_merger.constants import MAX_NUM_ITEMS_PER_NODE
from category_merger.category_api_utils import categories



# Defining the data structure for tree 
class TreeNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.category_ids = []
        self.size = 0
        self.children = []

    def add_category(self, cat_id, count):
        self.category_ids.append(cat_id)
        self.size += count


# Building a tree based on the category information provided

def build_tree_structure():
    tree = defaultdict(list)
    parents = {}
    item_counts = {}
    roots = []

    for cat_id, cat in categories.items():
        parent = cat.parent_id
        if parent is not None:
            tree[parent].append(cat_id)
        else:
            roots.append(cat_id)
        parents[cat_id] = parent
        item_counts[cat_id] = cat.count

    return tree, parents, item_counts, roots


# Merging the tree based on the condition MAX_NUM_ITEMS_PER_NODE


def merge_categories():
    tree, parents, item_counts, roots = build_tree_structure()

    node_id_counter = [1]
    cat_to_node = {}
    node_map = {}

    def dfs(cat_id):
        child_nodes = []

        for child in sorted(tree.get(cat_id, [])):
            dfs(child)
            child_node_id = cat_to_node[child]
            child_node = node_map[child_node_id]
            child_nodes.append(child_node)

        base_node = TreeNode(node_id_counter[0])
        node_id_counter[0] += 1
        base_node.add_category(cat_id, item_counts[cat_id])

        for child_node in sorted(child_nodes, key=lambda n: n.node_id):
            if base_node.size + child_node.size <= MAX_NUM_ITEMS_PER_NODE:
                base_node.category_ids.extend(child_node.category_ids)
                base_node.size += child_node.size
                for cid in child_node.category_ids:
                    cat_to_node[cid] = base_node.node_id
                del node_map[child_node.node_id]
            else:
                base_node.children.append(child_node.node_id)

        for cid in base_node.category_ids:
            cat_to_node[cid] = base_node.node_id
        node_map[base_node.node_id] = base_node

    for root in sorted(roots):
        dfs(root)

    # Ensure all parents are linked properly
    for node in node_map.values():
        for cid in node.category_ids:
            parent = parents.get(cid)
            if parent is not None:
                parent_node_id = cat_to_node.get(parent)
                if parent_node_id and parent_node_id != node.node_id:
                    parent_node = node_map[parent_node_id]
                    if node.node_id not in parent_node.children:
                        parent_node.children.append(node.node_id)

    return node_map



# Finding the root node in the merged tree 

def find_root_node(node_map):
    node_ids = set(node_map.keys())
    child_ids = set()
    for node in node_map.values():
        child_ids.update(node.children)
    root_ids = list(node_ids - child_ids)
    return root_ids[0] if len(root_ids) == 1 else None