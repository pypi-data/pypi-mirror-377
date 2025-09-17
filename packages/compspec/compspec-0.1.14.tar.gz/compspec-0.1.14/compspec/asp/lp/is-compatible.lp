%=============================================================================
% A and B are two instances of the same library. Can B replace A?
% Diff rules (the rules below define the diffspec
% This will be directional going from A to B (B-A)

% Libraries A and B are different if A!=B
% This is a sanity check that the unique id of things we're compating is different!
is_different(A, B) :- is_a(A), is_b(B), A != B.

% A node is a parent of another if they have a relation
is_parent(Namespace, NodeA, NodeB, Relation) :-
    node(Namespace, NodeA, _, _, _),
    node(Namespace, NodeB, _, _, _),
    relation(Namespace, NodeA, Relation, NodeB).

is_parent(Namespace, NodeA, NodeB, NameA, NameB, Relation) :-
    node(Namespace, NodeA, NameA, _, _),
    node(Namespace, NodeB, NameB, _, _),
    relation(Namespace, NodeA, Relation, NodeB).


% This could be reversed using the same function above,
% but we can provide the named function as a courtesy
is_child(Namespace, NodeA, NodeB, Relation) :-
    node(Namespace, NodeA, _, _, _),
    node(Namespace, NodeB, _, _, _),
    relation(Namespace, NodeB, Relation, NodeA).

% Return children of node in namespace, any parent node or relation
get_node_parents(Namespace, Parent, Node) :- is_parent(Namespace, Parent, Node, _).

% Note that we simply count 1 if the node has any parents, this isn't an accurate number.
has_parents(Namespace, Node) :- N = #count{ 1 : get_node_parents(Namespace, _, Node)}, node(Namespace, Node, _, _), N>0.
is_root(Namespace, Node) :- N = #count{ 1 : get_node_parents(Namespace, _, Node)}, node(Namespace, Node, _, _), N == 0.

% What is removed if we move from A to B?
% present in A but not B
% This covers anything with a parent (not a root)
removed_node(A, B, NodeA, Name, Path) :-
    is_a(A), is_b(B),
    node(A, NodeA, Name, ValueA, Path),
    not node(B, NodeB, Name, _, Path),
    not is_connector(A, NodeA),
    shared_parent_missing(NodeA, NodeB, Name),
    path(A, Path),
    not path(B, Path),
    not changed_node_value(A, B, _, _, _, _, _, _, Path),
    not changed_node_value(A, B, _, _, _, _, _, Path, _),
    not changed_parent(A, B, NodeA, NodeB).

% This covers top level cases (no parents)
removed_node(A, B, NodeA, Name, Value, Path) :-
    is_a(A), is_b(B),
    node(A, NodeA, Name, Value, Path),
    not node(B, _, Name, Value, Path),
    not is_connector(A, NodeA),
    not changed_node_value(A, B, _, _, Name, _, _, _, Path),
    not changed_node_value(A, B, _, _, Name, _, _, Path, _),
    path(A, Path),
    not path(B, Path),
    not changed_parent(A, B, NodeA, _).


% What is added if we move from A to B?
% present in B but not A?
% We have the entity in B but not A
added_node(A, B, EntityB, Name, Value, Path) :-
    is_a(A), is_b(B),
    node(B, EntityB, Name, Value, Path),
    not node(A, _, Name, Value, Path),
    not is_connector(B, EntityB),
    not changed_node_value(A, B, _, _, Name, _, _, Path, _),
    not changed_node_value(A, B, _, _, Name, _, _, _, Path),
    path(B, Path),
    not path(A, Path),
    not changed_parent(A, B, _, EntityB).


% What nodes are shared (at the highest level)
shared_nodes(A, B, EntityA, EntityB, Type, Name) :-
    is_a(A), is_b(B),
    node(B, EntityB, Type, Name, Path),
    node(A, EntityA, Type, Name, Path),
    path(A, Path),
    path(B, Path).

% or values
changed_node_value(A, B, EntityA, EntityB, Name, ValueA, ValueB, PathA, PathB) :-
    is_a(A), is_b(B),
    node(A, EntityA, Name, ValueA, PathA),
    node(B, EntityB, Name, ValueB, PathB),
    not is_connector(A, EntityA),
    not is_connector(B, EntityB),
    shared_parent(EntityA, EntityB, Name),

    % the parents aren't changed
    not changed_parent(A, B, EntityA, EntityB),
    ValueA != ValueB,
    PathA != PathB.


% changed parent for just one node namespace
changed_parent(A, EntityA) :-
    is_parent(A, ParentA, EntityA, _),
    changed_node_value(A, B, ParentA, _, _, _, _, _, _),
    changed_node_value(B, A, _, ParentA, _, _, _, _, _).
changed_parent(A, EntityA) :-
    is_parent(A, ParentA, EntityA, _),
    changed_parent(A, ParentA).


changed_parent(A, B, EntityA, EntityB) :-

    % the parents aren't changed
    is_parent(A, ParentA, EntityA, _),
    is_parent(B, ParentB, EntityB, _),

    changed_node_value(A, B, ParentA, _, _, _, _, _, _),
    changed_node_value(A, B, _, ParentB, _, _, _, _, _).


changed_parent(A, B, EntityA, EntityB) :-
    is_parent(A, ParentA, EntityA, _),
    is_parent(B, ParentB, EntityB, _),
    changed_parent(A, B, ParentA, ParentB).


% Two nodes have a shared parent (across states A and B) if:
shared_parent(NodeA, NodeB, Name) :-
    node(NamespaceA, NodeA, Name, _, _),
    node(NamespaceB, NodeB, Name, _, _),
    is_parent(NamespaceA, ParentA, NodeA, ParentName, _, Relation),
    is_parent(NamespaceB, ParentB, NodeB, ParentName, _, Relation),
    shared_parent(NodeA, NodeB, ParentName),
    NamespaceA != NamespaceB.

shared_parent(NodeA, NodeB, Name) :-
    node(NamespaceA, NodeA, Name, _, _),
    node(NamespaceB, NodeB, Name, _, _),
    is_parent(NamespaceA, ParentA, NodeA, ParentName, _, Relation),
    is_parent(NamespaceB, ParentB, NodeB, ParentName, _, Relation),
    NamespaceA != NamespaceB,
    NodeA == NodeB.

% This function is used to determine if two nodes have the same parent tree
% even if one is missing.
shared_parent_missing_node(NodeA, NodeB, Name) :-
    node(NamespaceA, NodeA, Name, _, _),
    not node(NamespaceB, NodeB, Name, _, _),
    is_parent(NamespaceA, ParentA, NodeA, ParentName, _, Relation),
    is_parent(NamespaceB, ParentB, NodeB, ParentName, _, Relation),
    shared_parent_missing(NodeA, NodeB, ParentName),
    NamespaceA != NamespaceB.

shared_parent_missing(NodeA, NodeB, Name) :-
    node(NamespaceA, NodeA, Name, _, _),
    not node(NamespaceB, NodeB, Name, _, _),
    is_parent(NamespaceA, ParentA, NodeA, ParentName, _, Relation),
    is_parent(NamespaceB, ParentB, NodeB, ParentName, _, Relation),
    NamespaceA != NamespaceB,
    NodeA == NodeB.

#defined relation/4.
#defined node/4.
#defined is_connector/2.
#show added_node/6.
#show removed_node/5.
#show removed_node/6.
#show changed_node_value/9.
%#show is_parent/4.
%#show is_child/4.
%#show has_parents/2.
%#show is_root/2.
%#show shared_parent/3.
%#show added_attribute/7.
%#show shared_attribute/7.
