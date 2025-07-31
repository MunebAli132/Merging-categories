## Merging categories

### Heads-up: What are we expecting from the solution
 - readable + maintainable code
 - reasonably efficient code
 - tested code
 - generally pretend like it's a standard task at work even though there are some simplifications
 - this is not a primarily algorithmic task, the focus is mainly on all the other parts of the implementation
 - solution does NOT have to result in optimal merging, a simple heuristic solution is perfectly fine

### Intro:

Imagine a website full of fashion items, every item having exactly 
one category e.g. **women-jackets**.
Some categories are sub-categories, e.g. **women-jackets** 
has 2 sub-categories: **women-leather-jackets** and **women-jean-jackets**.
The categories together with their sub-categories form a tree:

```
women-jackets
|- women-leather-jackets
|- women-jean-jackets            
```

The category tree is typically quite wide = up to thousands of categories 
but not very deep = depth < 10.

Each category:
 - has a unique ID called category-id
 - contains a certain number of items, it can be zero
 - has [0-1] parent categories
 - has [0-N] sub-categories

Something to be careful about is that number of items in women-jackets 
does NOT mean sum of items in women-jackets sub-categories. 
Items in women-jackets are not in any other category, they are not in any sub-categories either.
In other words: categories form distinct sets of items.

### The problem
We are in the process of creating a service that will take items in a certain category 
and wrap them by some Machine Learning model.

However, we found out that deploying one model per category results 
in a lot of overhead. 
We have therefore decided to merge some of the small categories together 
to reduce the number of models we will need to deploy.

Your task will be to implement the logic of merging categories 
as part of the already existing code. 
Specifics of the merging are described in section **The Task**.

### The existing code
We have already prepared a REST API that allows you to:
 - create category
 - list information about given category
 - delete category
 - list all categories

Counts in `GET /category/[category_id]` are without items in subcategories.

The endpoints can be found in `app_blueprint.py`.
The provided code should be runnable without any modifications.

### The task:
1. Extend the provided Flask application with the following endpoints:

 - `/tree_node`
   - method: `GET`
   - returns JSON with keys: 
     - `NodeIds`: List[int] of node ids.
     - `RootId`: Node ID of the root node.
 - `/tree_node/[int:node_id]` (Flask definition /tree_node/**<**int:node_id**>**)
   - method: `GET`
   - returns JSON with keys:
     - `NodeId`: Integer Node ID.
     - `CategoryIds`: List of category IDs. Each node should contain [1-N] categories.
     - `Size`: Integer, total number of items in this node.
     - `Children`: List of child Node IDs.
   - should work for every Node ID returned in `NodeIds` by the `/tree_node` endpoint

2. Check that the provided categories form a valid tree.

**Resulting Tree structure requirements:**
 - trivial solution is that each category is a node, this resulting tree would satisfy all requirements 
   but we would like a tree with fewer nodes than categories (if possible)
 - starting with the trivial solution we can merge two nodes only if they are directly connected 

**Examples of valid merging with the following category tree:**
```
A
| \
B  C
|  | \
D  E  F
```
In one merging step:
 - Can be merged (if sum of their items is <= `MAX_NUM_ITEMS_PER_NODE`):
   - `B` into `A`  
   - `C` into `A`  
   - `D` into `B` 
   - `E` into `C` 
   - `F` into `C` 
 - Cannot be merged:
   - all the other possible combinations cannot be merged e.g.: 
     - `D` into `A`
     - `E` into `B`


After merging e.g. `F` into `C` we get:
```
A
| \
B  C,F
|  | 
D  E  
```

After merging e.g. `C,F` into `A` we get:
```
A,C,F
| \
B  E
|   
D    
```


**Sanity-checks that should be true after valid merging:**
 - each node cannot contain more than `constants.MAX_NUM_ITEMS_PER_NODE` items
 - resulting tree nodes must form a valid tree with a single root node
 - resulting tree must contain all the provided categories in its nodes
 - each category can be in only one tree node
 - resulting tree should have as little nodes as possible
 - these requirements will be satisfied if the merging requirements are followed 

**Expected behavior of the tree_node API**
 - API responses must be deterministic
   - for given categories, we expect identical resulting tree with identical nodes
 - categories can be added at any time (e.g. between tree_node API calls)
   - if there is a change in the given categories, we expect that the tree_node API responses will respect these changes
   - in other words:
     - each POST or DELETE category API call changes the structure of the current category tree
     - tree_node API responses should always be about the current categories
 - if you encounter some edge cases that are not covered here, simply try to solve them as you see fit 

### Examples of usage
1. Run the Flask app:
 - `python -m category_merger.main`

2. Insert a set of categories:
```
curl -X POST --header "Content-Type: application/json" --data '{"Id": 4, "Count": 30}'  http://127.0.0.1:5000/category
curl -X POST --header "Content-Type: application/json" --data '{"Id": 5, "Count": 10, "Parent": 4}'  http://127.0.0.1:5000/category
curl -X POST --header "Content-Type: application/json" --data '{"Id": 6, "Count": 80, "Parent": 5}'  http://127.0.0.1:5000/category
curl -X POST --header "Content-Type: application/json" --data '{"Id": 7, "Count": 90, "Parent": 6}'  http://127.0.0.1:5000/category
curl -X POST --header "Content-Type: application/json" --data '{"Id": 8, "Count": 5, "Parent": 6}'  http://127.0.0.1:5000/category
curl -X POST --header "Content-Type: application/json" --data '{"Id": 9, "Count": 8, "Parent": 6}'  http://127.0.0.1:5000/category
curl -X POST --header "Content-Type: application/json" --data '{"Id": 10, "Count": 20, "Parent": 4}'  http://127.0.0.1:5000/category
```

3. Receive the resulting nodes containing all the inserted categories:
 - the results of this step depend on your chosen algorithm of merging the categories into nodes
 - there are multiple possibilities
```
curl -X GET  http://127.0.0.1:5000/tree_node
curl -X GET  http://127.0.0.1:5000/tree_node/1
curl -X GET  http://127.0.0.1:5000/tree_node/2
curl -X GET  http://127.0.0.1:5000/tree_node/3
curl -X GET  http://127.0.0.1:5000/tree_node/4
```
 - for a simple heuristic (which would be fine as a solution as well as many others) the result of the calls above could be:
```
curl -X GET  http://127.0.0.1:5000/tree_node
{
  "NodeIds": [
    1,
    3,
    4
  ],
  "RootId": 1
}

curl -X GET  http://127.0.0.1:5000/tree_node/1
{
  "CategoryIds": [
    4,
    10,
    5
  ],
  "Children": [
    3
  ],
  "NodeId": 1,
  "Size": 60
}

curl -X GET  http://127.0.0.1:5000/tree_node/2
{
  "error message": "Not a tree node."
}

curl -X GET  http://127.0.0.1:5000/tree_node/3
{
  "CategoryIds": [
    6,
    9,
    8
  ],
  "Children": [
    4
  ],
  "NodeId": 3,
  "Size": 93
}

curl -X GET  http://127.0.0.1:5000/tree_node/4
{
  "CategoryIds": [
    7
  ],
  "Children": [],
  "NodeId": 4,
  "Size": 90
}

```

Visualizations of the category tree provided in step 3.:
```
    4
    | \
    5  10
    |
    6
 /  |  \
 7  8  9
```
And the resulting tree (for this simple heuristic, which would be a valid solution):
```
    4,10,5
       |
     6,9,8
       |
       7   
```

### Environment to be able to run the provided code
 - Python 3.11
 - package versions are in `requirements.txt`

### Optional Reading
 - intro to [Flask](https://flask.palletsprojects.com/en/stable/)
