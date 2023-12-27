import os
import numpy as np
from copy import deepcopy
import random
import pandas as pd

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from collections import defaultdict

def clean_text(input_text):
    return input_text.strip()

def take_inputs(filepath = os.getcwd()+"/data/restaurant.csv"):
    text = input(
        "Please enter 0 to use Default column names:\n"
        """["Alternate", "Bar", "Fri/Sat",
        "Hungry", "Patrons", "Price", "Raining",
        "Reservation", "Type", "Wait_Estimate", "Will_wait"]
        """
        "for the restaurant CSV.\n "
        "Please enter 1 to use the column names from the csv.\n "
        "Print enter 2 to enter your own column names in the same format as above.\n"
        "Press 'q' to quit.\n")
    if text == "1":
        input_data = pd.read_csv(filepath, index_col = False)
    elif text == "0":
        input_data = pd.read_csv(filepath, names = ["Alternate", "Bar", "Fri/Sat",
                                                   "Hungry", "Patrons", "Price", "Raining",
                                                   "Reservation", "Type", "Wait_Estimate", "Will_wait"],
                                index_col = False)
    elif text == "2":
        lew_list = input("Please enter the column names.")
        new_list = eval(lew_list)
        for ele in new_list:
            print(ele)
        input_data = pd.read_csv(filepath, names = new_list,
                                index_col = False)
    elif text == "q":
        return None
    input_data = input_data.applymap(clean_text)
    return input_data


class Tree:
    """
    Decision tree implementation here. Also implemented an inference tool but not sure if that's required.
    """
    def __init__(self, parent, df, target_column, previous_answer=None):
        self.parent = parent
        self.target_column = target_column # Will_wait which we are trying to predict
        self.questioning_attribute = None # current column that gives the most information
        self.answer = None # T/F to target_column (Will_wait) 
        self.children = []
        self.previous_answer = previous_answer # the questioning attribute's answer
        self.df = df # all the data

    def travel_recursively(self, parent_node, graph, labels_dict, inverse_labels_dict, edge_labels):
        for child in parent_node.children:
            current_id = len(graph.nodes)
            graph.add_node(current_id)
            labels_dict[current_id] = child.describe_node()
            inverse_labels_dict[child.describe_node()] = current_id
            graph.add_edge(inverse_labels_dict[parent_node.describe_node()], current_id)

            edge_labels[(inverse_labels_dict[parent_node.describe_node()], current_id)] = child.previous_answer
            graph, labels_dict, inverse_labels_dict, edge_labels = parent_node.travel_recursively(parent_node=child,
                                                                                                  graph=graph,
                                                                                                  labels_dict=labels_dict,
                                                                                                  inverse_labels_dict=inverse_labels_dict,
                                                                                                  edge_labels=edge_labels)
        return graph, labels_dict, inverse_labels_dict, edge_labels

    def describe_node(self):
        if self.answer is not None:
            return self.answer
        if self.questioning_attribute is not None:
            return self.questioning_attribute + "? {Information gain = " + str(
                self.calculate_info_gain(self.df, relevant_column=self.questioning_attribute)) + "}"
        
    # used chat gpt to find a simplified entropy calculator == B() from the book
    def entropy(self, data):
        classes, counts = np.unique(data, return_counts=True)
        probabilities = counts / len(self.df[self.target_column])
        # print(probabilities)
        entropy_value = -np.sum(probabilities * np.log2(probabilities))
        return entropy_value
    
    # Gain(questioning_attribute) == Gain(A) from the book
    def caclulate_info_gain(self, df, questioning_attribute):
        print(questioning_attribute)
        total_examples = len(df[self.target_column]) # total rows of current df
        parent_entropy = self.entropy(df[self.target_column]) # entropy of our current df
        child_entropy = 0.0

        split_values = np.unique(df[questioning_attribute]) # obtain different target values

        # for each of the possible child values, build a child set and sum the child set's entropies
        for value in split_values:
            child_set = []
            for i in df[questioning_attribute]:
                if i == value:
                    child_set.append(i)
            weight = len(child_set) / total_examples
            
            # print(child_set)
            # print()
            child_entropy += weight * self.entropy(child_set)
        # print(parent_entropy)
        # print(weight)
        # print(child_entropy)
        # print(parent_entropy - child_entropy)
        # print()
        return parent_entropy - child_entropy
        

    def visualise_tree(self, file_name = "decision_tree.png"):


        """
        Visualises the tree and saves the graph as "decision_tree.png"
        """
        visual_graph = nx.DiGraph()

        visual_graph.add_node(self.describe_node())  # Root node
        labels_dict = {self.describe_node(): self.describe_node()}
        inverse_labels_dict = {self.describe_node(): self.describe_node()}
        edge_labels = {}
        visual_graph, labels_dict, inverse_labels_dict, edge_labels = self.travel_recursively(parent_node=self,
                                                                                              graph=visual_graph,
                                                                                              labels_dict=labels_dict,
                                                                                              inverse_labels_dict=inverse_labels_dict,
                                                                                              edge_labels=edge_labels)

        d = dict()
        for ele in visual_graph:
            d[ele] = len(labels_dict[ele]) * 10
        plt.figure(figsize=(20, 20))
        plt.title('Decision Tree')
        pos = graphviz_layout(visual_graph, prog='dot')
        nx.draw(visual_graph, pos, with_labels=True, arrows=True, node_size=[v * 50 for v in d.values()],
                labels=labels_dict)

        nx.draw_networkx_edge_labels(
            visual_graph, pos,
            edge_labels=edge_labels,
            font_color='red'
        )
        plt.savefig(file_name)
    
    def learn_decision_tree(self, df, attributes, parent_df):
        if len(df) is 0:
            return self.plurality_values(parent_df)
        elif all(value == df[self.target_column][0] for value in df[self.target_column]):
            return
            # return the value and remove the columns
        elif len(attributes) is 0:
            return self.plurality_values(df)
            # return random classification and remove the columns
        else:
            # determining the next attribute to search
            max_info_gain = 0
            questioning_attribute = ""
            for attribute in attributes:
                cur_info_gain = self.caclulate_info_gain(df, attribute)
                print(cur_info_gain)
                if cur_info_gain > max_info_gain:
                    max_info_gain = cur_info_gain
                    questioning_attribute = attribute
        
            tree = Tree(self, df, questioning_attribute, self.answer)
            self.children.append(tree)
            tree.parent = self
            tree.previous_answer = self.answer
            stuff, unique_values = np.unique(df[questioning_attribute], return_counts=True)
            for value in unique_values:
                new_df = (df[questioning_attribute] == value)
                attributes.remove(questioning_attribute)
                subTree = tree.learn_decision_tree(new_df, attributes, df)
                tree.children.append(subTree)

    def plurality_values(self, df):
        num_of_unique_value, unique_values = np.unique(df[self.questioning_attribute], return_counts=True)
        index = 0
        maxval = 0
        maxvalindex = 0
        for value in num_of_unique_value:
            if value > maxval:
                maxval = value
                maxvalindex = maxvalindex
            index += 1
        
        return unique_values[maxvalindex]



def check_quitting(text):
    if text == "q":
        print("exiting")
        return True

def main():
    data_read = False
    dt_trained = False
    dt_pruned = False
    training_data_frame = None
    while True:
        if not data_read:
            text = input(
                "Please enter the relative path of the input text file. Should look like this : \"data/restaurant.csv\". Press 'q' to quit.\n")

            if check_quitting(text):
                return
            try:
                training_data_frame = take_inputs(text)  # Reading Data
                if training_data_frame is None:
                    if check_quitting("q"):
                        return
                data_read = True
            except:
                if check_quitting(text):
                    return
                print("Invalid file path. Please try again.")
                continue


        if not dt_trained and data_read:
            print("Columns are : ", [col for col in training_data_frame.columns])
            text = input(
                "Please enter the name of the column to predict. Press 'q' to quit.\n")
            if check_quitting(text):
                return
            print(f"recieved input : {text}", text in training_data_frame.columns)
            # try:
            dt = Tree(parent = None, df=training_data_frame, target_column=text)

            # Generate children here
            dt.learn_decision_tree(dt.df, dt.df.columns, dt.df)


            dt.visualise_tree()
            print("All done. Please look at \"decision_tree.png\" and \"pruned_decision_tree.png\" for the decision tree.")
            dt_trained = True
            exit()
            # except:
            #     if check_quitting(text):
            #         return
            #     print("Invalid column name. Please try again.")
            #     continue




if __name__ == '__main__':main()