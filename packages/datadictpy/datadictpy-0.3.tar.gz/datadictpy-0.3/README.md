
# Datadictpy doc

#**install**
-
`pip install datadictpy`

#**import**
-
`from datadictpy import Db, Relation`

#**MAIN METHODS:**
-

**ADD_ELEMENT()**

**HOW TO USE:**

    

in a separate file create a class, this class will contain all the dictionaries (tables) of the bank, create your dictionaries and   create an object with the Db class

Ex:


  ```
  class teste:

  usuario = {`
      "id": uuid.uuid4().hex,
       "nome": str,
       "senha": str,
   }`
   user = Db(usuario)
   ```





 in another file like a Flask project for example, add elements to the dictionaries in the standard python way (don't forget to declare the class you created for the dictionaries, after all        the additions call the add\_elemente method (remembering to call the object and class you created), pass as a parameter a string with the name of the table.

Ex:

 
     ```
     teste.usuario['nome'] = nome
     teste.usuario['senha'] = senha
     teste.user.add_element("usuario")
     ```


**FIND_KEY_ELEMENT()**

     **HOW TO USE:**



     This method is used to find all elements with the same key in the list (table) like all names and returns, pass as a parameter in this order, the dictionary key and the list name

    Ex:



      `teste.user.find_key_element("nome", "usuario")`





**FIND_ID()**

    **HOW TO USE:**



 This method returns the data related to the id passed in the parameter, pass the id and the name of the list as parameters in this order

   EX:

     

`teste.user.find_id      ("646e59b9cb9f4d2c9bfffeb5c5b34898",        "usuario")`



**SHOW_LIST()**

    **HOW TO USE:**



   This method returns all dictionaries from the list passed as a parameter

 Ex:



   `` teste.user.show_list("usuario")`



**FIND_VALUE_ELEMENT()**

    **HOW TO USE:**



    This method receives as parameters the dictionary key, a  dictionary value and a list name, and analyzes whether the value exists, if it exists it returns true if not it returns false

   Ex:



  `` teste.user.find_value_element("nome", "david", "usuario")`



**DROP_DICT()**

    **HOW TO USE:**



    This method receives an id and a list name as parameters and deletes the dictionary with that id.

   Ex:



`teste.user.drop_dict     ("646e59b9cb9f4d2c9bfffeb5c5b34898",          "usuario")`



**DROP_LIST()**

    **HOW TO USE:**

    

    This method receives the name of a list as a parameter and deletes it.

   Ex:



`teste.user.drop_list("usuario")`



**RELATE()**

    **HOW TO USE:**



    This method receives as a parameter in this order a name for the relation, a string "node", the name of the first list to be related, and a list with the name of all the lists that will be related to it.

   Ex:



     `teste.rel.relate("rel1", "node", "usuario", \["relation1, "relation2"]`

     (It is necessary to create an object for the Relation class in the same file in which the dictionaries are created)



**SEARCH()**

    **HOW TO USE:**



    This method does the same thing as find\_key\_element, with the difference that SEARCH searches all lists of a relation, and receives as parameters the dictionary key and the name of the created relation.

   Ex:



`teste.rel.search("nome", "rel1")`
