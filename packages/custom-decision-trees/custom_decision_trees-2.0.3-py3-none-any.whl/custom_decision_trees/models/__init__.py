# # Classe de base
# class DecisionTree:
#     def __init__(self, max_depth=None):
#         self.max_depth = max_depth
#         self.tree = None

#     def fit(self, X, y):
#         # Utilise get_partition_value, qui sera surchargée dans l'enfant
#         partition_value = self.get_partition_value(y)
#         print(f"[DecisionTree] Partition utilisée : {partition_value}")
#         self.tree = "arbre construit"

#     def get_partition_value(self, y):
#         raise NotImplementedError("Doit être défini dans la classe enfant")

# # Classifier avec argument supplémentaire "classes"
# class DecisionTreeClassifier(DecisionTree):
#     def fit(self, X=1, y=1):
#         # On peut traiter "classes" ici
#         if classes is not None:
#             print(f"Classes spécifiées : {classes}")
#         # Appel du fit parent pour la logique commune
#         super().fit(X, y)

#     def get_partition_value(self, y):
#         from collections import Counter
#         counts = Counter(y)
#         mode = counts.most_common(1)[0][0]
#         return mode

# # Regressor reste simple
# class DecisionTreeRegressor(DecisionTree):
#     def get_partition_value(self, y):
#         return sum(y) / len(y)
