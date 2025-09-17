
import copy

def format_values(exprn, value):
    # 单值情况
    print("exprn",exprn)
    print("value",value)
    if not isinstance(exprn, list):
        return f"{value}[{exprn}]"
    
    # 列表情况
    if isinstance(exprn, list) and isinstance(value, list):
        if len(exprn) != len(value):
            raise ValueError("exprn 和 value 长度不一致")
        return [f"{v}[{e}]" for v, e in zip(value, exprn)]
    
    raise TypeError("exprn 和 value 类型不匹配")

class CclTtNode:
    def __init__(self, tree, node_id: int, name: str = None):
        self.tree = tree
        self.node_id = node_id
        self.name = name

    def __str__(self):
        return f"CclTtNode (id={self.node_id} name={self.name})"
    
    def value(self):
        return self.tree.db.get_node_value(self.tree.name, self.node_id)
    
    def type(self):
        return self.tree.db.get_node_type(self.tree.name, self.node_id)
    
    def exprn(self):
        return self.tree.db.get_node_exprn(self.tree.name, self.node_id)

    def __repr__(self):
        return self.__str__()
    
    def add(self, path: str):
        """自己添加一个子节点"""
        return self.tree.add_path(self.node_id, path)
    def get(self, path: str):
        return self.tree.find_by_path_with_wildcard(self.node_id, path)
    
    def retype(self, type: str):
        self.tree.retype(type)
    
    def revalue(self, value):
        self.tree.revalue(value)

    def rename(self, name):
        self.name = name
        self.tree.rename(name)
    
    def print(self,indent):
        ans = indent
        ans += self.name
        cnt = 0
        if self.type():
            ans += " : "
            ans += self.type()
            cnt = 1
        if self.value():
            ans += " = "
            exprn = self.exprn()
            value = "\"" + self.value() + "\"" if self.type() == "str" else self.value()
            if exprn is not None:
                ans += format_values(exprn, value)
            else:
                ans += str(value)
            cnt = 1
        if cnt == 1 :
            return ans
        children = self.tree.find_by_path_with_wildcard(self.node_id,"*")
        if children:
            ans += '\n'
            ans += indent
            ans += "children :"
            for child in children:
                ans += '\n'
                ans += child.print(indent + "    ")
        return ans    
    def transfrom(self,indent):
        ans = indent
        ans += self.name
        if self.value() is not None and self.type() is not None :
            ans += " = "
            value = "\"" + self.value() + "\"" if self.type() == "str" else self.value()
            exprn = self.exprn()
            if exprn is not None:
                ans += format_values(exprn, value)
            else:
                ans += str(value)
            return ans
        ans += "\n"
        ans += indent
        ans += "{"
        for child in self.tree.find_by_path_with_wildcard(self.node_id,"*"):
            ans += '\n'
            ans += child.transfrom(indent + "    ")
        ans += '\n'
        ans += indent
        ans += "}"
        return ans

class CclTtNodes:
    def __init__(self, nodes):
        self.nodes= nodes
    

    def __str__(self):
        return f"CclTtNodes (nodes: {self.nodes})"

    def __repr__(self):
        return self.__str__()

    def value(self):
        if len(self.nodes) != 1:
            return None
        return self.nodes[0].value()
    
    def type(self):
        if len(self.nodes) != 1:
            return None
        return self.nodes[0].type()

    def add(self, path, val = None):
        """自己添加一个子节点"""
        if not isinstance(path, str) and not isinstance(path, CclTtNodes):
            if self.add_link(val, path):
                return True
            return False
        elif val is not None:
            if self.add_val(path, val):
                return True
            return False
        elif isinstance(path, str):
            if self.add_dir(path):
                return True
            return False
        elif isinstance(path, CclTtNodes):
            if self.add_tree(path):
                return True
            return False
        
    
    def add_dir(self, path: str):
        """自己添加一个子节点"""
        for node in self.nodes:
            if not node.tree.add_path(node.node_id, path):
                return False
        return True
    
    def add_tree(self, nodes):
        if len(self.nodes) != 1:
            return False
        root_node = self.nodes[0]
        for node in nodes.nodes:
            if node.tree.name != root_node.tree.name:
                if( not root_node.tree.deep_copy(root_node.node_id, node.node_id, source_tree = node.tree.name)):
                    return False
            else:
                if( not root_node.tree.deep_copy(root_node.node_id, node.node_id)):
                    return False
        return True
    
    def add_val(self, path ,val):
        if isinstance(val, bool):
            for node in self.nodes:
                if not node.tree.add_val(node.node_id, path,"bool",val):
                    return False
            return True
        elif isinstance(val, str):
            for node in self.nodes:
                if not node.tree.add_val(node.node_id, path,"str",val):
                    return False
            return True
        elif isinstance(val, int):
            for node in self.nodes:
                if not node.tree.add_val(node.node_id, path,"int",val):
                    return False
            return True
        elif isinstance(val, float):
            for node in self.nodes:
                if not node.tree.add_val(node.node_id, path,"real",val):
                    return False
            return True
        elif isinstance(val, list) and all(isinstance(x, int) for x in val):
            for node in self.nodes:
                if not node.tree.add_val(node.node_id, path,"int list",val):
                    return False
            return True
        elif isinstance(val, list) and all(isinstance(x, float) for x in val):
            for node in self.nodes:
                if not node.tree.add_val(node.node_id, path,"real list",val):
                    return False
            return True

    def add_link(self, node, alias: str | None):
        if len(self.nodes) != 1:
            return False
        if len(node.nodes) != 1:
            return False
        root_node = self.nodes[0]
        add_node = node.nodes[0]
        if( not root_node.tree.add_link(root_node.node_id, add_node.node_id, alias)):
            return False
        return True
    
    def get(self, path: str):
        ans = []
        for node in self.nodes:
            ans.extend(node.tree.find_by_path_with_wildcard(node.node_id, path))
        if len(ans) == 0:
            return None
        return CclTtNodes(ans)
    
    def name(self):
        if len(self.nodes) == 1:
            return self.nodes[0].name
        return None
    
    def copy(self):
        return CclTtNodes(copy.copy(self.nodes))
    
    def delete(self, path = None):
        """删除节点"""
        if path is  None:
            for node in self.nodes:
                node.tree.delete_node_and_children(node.node_id)
            del self
            return
        node = self.get(path)
        if node is None:
            return
        node.delete()
        return 
    
    def rename(self, name1: str ,name2 :str = None):
        if name2 is None:
            if len(self.nodes) == 1:
                self.nodes[0].name = name1
                self.nodes[0].tree.rename(self.nodes[0].node_id,name1)
                return True
            else:
                return False
        else:
            chul_node =  self.get(name1)
            if chul_node is None:
                return False
            chul_node.rename(name2)
            return True
        
    def retype(self, type: str):
        if len(self.nodes) == 1:
            self.nodes[0].tree.retype(self.nodes[0].node_id,type)
            return True
        else:
            return False
    
    def revalue(self, value):
        if len(self.nodes) == 1:
            self.nodes[0].tree.revalue(self.nodes[0].node_id,value)
            return True
        else:
            return False
        
    def cclnodes(self):
        res = []
        for i in self.nodes:
            res.append(CclTtNodes([i]))
        return res
    
    def print(self):
        ans = ""
        for node in self.nodes:
            ans += node.print("")
            ans += '\n\n'
        return ans

    def transfrom(self):
        ans = ""
        for node in self.nodes:
            ans += node.transfrom("")
            ans += "\n"
        return ans
    
    def add_exprn(self,exprn):
        if len(self.nodes) != 1:
            return False
        root_node = self.nodes[0]
        if( not root_node.tree.add_exprn(root_node.node_id,exprn)):
            return False
        return True

        

def merge(a:CclTtNodes, b:CclTtNodes, c = None):
    """两个节点的并集"""
    if a is None:
        return b
    if b is None:
        return a
    return CclTtNodes(a.nodes + b.nodes)

def remove(a:CclTtNodes, b:CclTtNodes):
    a_copy = a.copy()
    for node in a_copy.nodes:
        for node2 in b.nodes:
            if node.node_id == node2.node_id and node.tree.name == node2.tree.name:
                a_copy.nodes.remove(node)
    return a_copy