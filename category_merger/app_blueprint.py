from typing import TypeVar

from flask import Blueprint, request

from category_merger.api_utils import APIErrorResponse
from category_merger.category_api_utils import (
    CategoryListResponse,
    CategoryInsertQuery,
    Category,
    CategoryItemResponse,
    categories,
)

T = TypeVar("T")

from flask import jsonify
from category_merger.tree_node_builder import merge_categories
from category_merger.tree_node_builder import find_root_node



########################################################################################################################
#
#    API
#


# API blueprint defining the Flask app endpoints
api_bp = Blueprint("api_bp", __name__)


########################################################################################################################
#
#    category API
#


@api_bp.route("/category", methods=["POST"])
def create_category():
    query = CategoryInsertQuery.parse(request.json)
    if query.id in categories:
        return APIErrorResponse(status_code=409, status="Conflict: Endpoint exists.").make_response()

    new_category = Category(id=query.id, label=query.label, count=query.count, parent_id=query.parent)
    categories[query.id] = new_category

    return CategoryItemResponse.from_category(new_category).make_response()


@api_bp.route("/category", methods=["GET"])
def list_categories():
    return CategoryListResponse(ids=list(categories.keys())).make_response()


@api_bp.route("/category/<int:cat_id>", methods=["GET"])
def get_category(cat_id):
    try:
        return CategoryItemResponse.from_category(categories[cat_id]).make_response()
    except KeyError:
        return APIErrorResponse(status_code=404, status="Category not found.").make_response()


@api_bp.route("/category/<int:cat_id>", methods=["DELETE"])
def delete_category(cat_id):
    try:
        del categories[cat_id]
        return CategoryItemResponse(just_deleted=True).make_response()
    except KeyError:
        return APIErrorResponse(status_code=404, status="Category not found.").make_response()





tree_cache = {}

@api_bp.route("/tree_node", methods=["GET"])
def get_all_tree_nodes():
    node_map = merge_categories()
    tree_cache.clear()
    tree_cache.update(node_map)

    root_id = find_root_node(node_map)
    return jsonify({
        "NodeIds": sorted(node_map.keys()),
        "RootId": root_id
    })


@api_bp.route("/tree_node/<int:node_id>", methods=["GET"])
def get_tree_node_details(node_id):
    if node_id not in tree_cache:
        return jsonify({"error message": "Not a tree node."}), 404

    node = tree_cache[node_id]
    return jsonify({
        "NodeId": node.node_id,
        "CategoryIds": sorted(node.category_ids),
        "Size": node.size,
        "Children": sorted(node.children)
    })




