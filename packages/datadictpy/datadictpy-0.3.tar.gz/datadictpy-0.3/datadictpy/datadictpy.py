import pickle
import os

class Db:
    def __init__(self, dictionary):
        self.find = None
        self.node = None
        self.relate = None
        self.a = None
        self.dictionary=dictionary
        lista = list()
        self.lista = lista
        self.blista = list()


    def serialize(self):
        try:
            with open(f"{self.a}.pkl", "wb") as file:
                pickle.dump(self.lista, file)
                print("list created")
        except Exception as e:
            print(f"ocorreu um erro: {e}")

    def add_element(self, a):
        self.a = a
        Db.binary(self)
        for item in self.blista:
            self.lista.append(item)
        self.lista.append(self.dictionary.copy())
        Db.serialize(self)
        return self.lista

    def binary(self):
        try:
            with open(f"{self.a}.pkl", "rb") as file:
                self.blista = pickle.load(file)
                return self.blista
        except Exception as e:
            print(f"ocorreu um erro: {e}")

    def find_key_element(self, key, table):
        self.a = table
        Db.binary(self)
        find = list()
        self.find = find
        for element in self.blista:
            find.append(element[key])
        return find

    def find_id(self, id, table):
        self.a = table
        Db.binary(self)
        for dictionary in self.blista:
            if dictionary["id"] == id:
                return dictionary
        return None

    def show_list(self, slist):
        self.a = slist
        Db.binary(self)
        for element in self.blista:
           print(f"{element}")

    def find_value_element(self, fkey, value, lista):
        data = Db.find_key_element(self, fkey, lista)
        if value in data:
            return True
        else:
            return False

    def drop_dict(self, id, lista):
        self.a = lista
        Db.binary(self)
        for dictionary in self.blista:
            if dictionary["id"] == id:
                self.blista.remove(dictionary)
                print("dictionary deleted")
        Db.serialize(self)

    def drop_list(self, lista):
        self.a = lista
        try:
            os.remove(f"{self.a}.pkl")
            print("list removed")
        except FileNotFoundError:
            print("file not found")
        except Exception as e:
            print(f"ocorreu um erro: {e}")

class Relation:
   def __init__(self):
       self.root = None
       self.left = None
       self.right = None

   def data_tree(self):
       self.tree = {
           "root": {
               "rooting": None,
               "node": {
                   "right": None,
                   "left": None,
               }
           }
       }
       return self.tree

   def run_dictionary(self, dictionary):
       self.values = list()
       for key, value in dictionary.items():
           if isinstance(value, dict):
               self.run_dictionary(value)
           else:
               self.values.append(value)
       return self.values


   def relate(self, rkey, root, right, left):
       tree = Relation.data_tree(self)
       self.a = rkey
       tree["root"]["rooting"] = root
       tree["root"]["node"]["left"] = left
       tree["root"]["node"]["right"] = right
       self.lista = tree
       Db.serialize(self)


   def find_relate_element(self, rkey):
       self.a = rkey
       blist = Db.binary(self)
       self.aux = Relation.run_dictionary(self, blist)
       return self.aux

   def search(self, key, rkey):
       self.a = rkey
       Relation.find_relate_element(self, rkey)
       search_list = list()
       out_list = list()
       search_list.append(self.aux[0])
       for item in self.aux[1]:
           search_list.append(item)
       for item in search_list:
           out_list.append(Db.find_key_element(self, key, item))
       return out_list

   def search_id(self, id, rkey):
       self.a = rkey
       Relation.find_relate_element(self, rkey)
       search_list = list()
       out_list = list()
       search_list.append(self.aux[0])
       for item in self.aux[1]:
           search_list.append(item)
       for item in search_list:
           out_list.append(Db.find_id(self, id, item))
       return out_list