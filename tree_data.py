"""
=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser.
"""
import os
from random import randint
import math


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    === Public Attributes ===
    @type data_size: int
        The total size of all leaves of this tree.
    @type colour: (int, int, int)
        The RGB colour value of the root of this tree.

    === Private Attributes ===
    @type _root: obj | None
        The root value of this tree, or None if this tree is empty.
    @type _subtrees: list[AbstractTree]
        The subtrees of this tree.
    @type _parent_tree: AbstractTree | None
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    def __init__(self, root, subtrees, data_size=0):
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this
        tree's data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.

        @type self: AbstractTree
        @type root: object
        @type subtrees: list[AbstractTree]
        @type data_size: int
        @rtype: None
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None

        self.colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        if self._subtrees == []:
            self.data_size = data_size
        else:
            self.data_size = 0
            for subtree in self._subtrees:
                self.data_size += subtree.data_size
                subtree._parent_tree = self

    def is_empty(self):
        """Return True if this tree is empty.

        @type self: AbstractTree
        @rtype: bool
        """
        return self._root is None

    def generate_treemap(self, rect):
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """
        if self.data_size == 0:
            return []
        elif self._subtrees == []:
            return [(rect, self.colour)]
        else:
            treemap = []
            x, y, width, height = rect
            h_left = height
            w_left = width
            for tree in self._subtrees:
                ratio = tree.data_size / self.data_size
                value = math.floor(ratio * max(width, height))

                if width > height and tree is self._subtrees[-1]:
                    new_rect = (x, y, w_left, height)
                    w_left -= value
                    x += value
                elif width > height:
                    new_rect = (x, y, value, height)
                    w_left -= value
                    x += value
                elif height >= width and tree is self._subtrees[-1]:
                    new_rect = (x, y, width, h_left)
                    h_left -= value
                    y += value
                else:
                    new_rect = (x, y, width, value)
                    h_left -= value
                    y += value
                treemap.extend(tree.generate_treemap(new_rect))
            return treemap

    def list_leaves(self):
        """Return a list of leaves in this tree in the same order as the tree's
        treemap.

        @type self: AbstractTree
        @rtype: list[Tree]
        """
        if self.data_size == 0:
            return []
        elif self._subtrees == []:
            return [self]
        else:
            trees = []
            for tree in self._subtrees:
                trees.extend(tree.list_leaves())
            return trees

    def get_leaf(self, position, treemap):
        """Return the leaf in the tree at specified position in the treemap.

        @type self: AbstractTree
        @type position: (int, int)
        @type treemap: list[((int, int, int, int), (int, int, int))]
        @rtype: AbstractTree
        """
        if treemap == []:
            return None
        else:
            directory = {}
            files = self.list_leaves()
            for i in range(len(files)):
                x, y, w, h = treemap[i][0]
                directory[files[i]] = [(x, y), (x + w, y + h)]
            # Directory is a dictionary of leaves to each leaf's position range

            x, y = position
            for leaf in directory:
                if leaf is not None:
                    x1, y1 = directory[leaf][0][0], directory[leaf][0][1]
                    x2, y2 = directory[leaf][1][0], directory[leaf][1][1]
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        return leaf

    def get_path(self):
        """Return the names of the nodes on the path from the root to the
        current leaf, separated by a subclass-specific separator string.

        @type self: AbstractTree
        @rtype: str
        """
        if self.is_empty():
            return ''
        elif self._parent_tree is None:
            return self._root
        else:
            return self._parent_tree.get_path() + self.get_separator() + \
                   self._root

    def delete(self):
        """Delete the current leaf.

        Change the data size of current leaf to 0 and update all ancestors'
        data size. The leaf should still remain in the tree.

        Precondition: This can be only used on leaves (trees with no subtrees).

        @type self: AbstractTree
        @rtype: None
        """
        if not self.is_empty():
            size, self.data_size, self._root = self.data_size, 0, None
            parent = self._parent_tree
            while parent is not None:
                parent.data_size -= size
                parent = parent._parent_tree

    def change_size(self, symbol):
        """Increase or decrease the current tree's data size by 1% according to
        the given symbol. Update all ancestors' data size.

        The 1 % amount is always rounded up before applying the change. A leaf's
        data_size cannot decrease below 1. There is no upper limit on the value
        of data_size.

        Precondition: the symbol is either '+' or '-'.

        @type self: AbstractTree
        @type symbol: str
        @rtype: None
        """
        value = math.ceil(self.data_size * 0.01)
        parent = self._parent_tree
        if symbol == '+':
            self.data_size += value
            while parent is not None:
                parent.data_size += value
                parent = parent._parent_tree
        elif symbol == '-' and self.data_size - value > 0:
            self.data_size -= value
            while parent is not None:
                parent.data_size -= value
                parent = parent._parent_tree

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        @type self: AbstractTree
        @rtype: str
        """
        raise NotImplementedError


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.
    """
    def __init__(self, path):
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.

        @type self: FileSystemTree
        @type path: str
        @rtype: None
        """
        if not os.path.isdir(path):
            AbstractTree.__init__(self, os.path.basename(path), [],
                                  os.path.getsize(path))
        elif os.listdir(path) == []:
            AbstractTree.__init__(self, os.path.basename(path), [])
        else:
            folders = []
            for folder in os.listdir(path):
                new_path = os.path.join(path, folder)
                folders.append(FileSystemTree(new_path))
            AbstractTree.__init__(self, os.path.basename(path), folders,
                                  os.path.getsize(path))

    def get_separator(self):
        """Return the string used to separate nodes in the string
        representation of a path from the root folder to a file.

        @type self: AbstractTree
        @rtype: str
        """
        return '/'

if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config='pylintrc.txt')
